"""dots.ocr model integration - OFFICIAL MODAL NOTEBOOKS IMPLEMENTATION.

Based on: https://modal.com/docs/examples/notebooks/dots-ocr
Official: https://huggingface.co/rednote-hilab/dots.ocr
GitHub: https://github.com/rednote-hilab/dots.ocr

This implementation exactly follows the working Modal Notebooks example.
"""

import os
import json
import torch
from typing import Any, Dict, List, Optional
from PIL import Image

from models.base_model import BaseModel
from utils.logger import logger


class DotsOCRModel(BaseModel):
    """dots.ocr for unified document parsing - OFFICIAL IMPLEMENTATION."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
        self.prompt_mode = config.get('prompt_mode', 'layout_all')
        self.max_new_tokens = config.get('max_new_tokens', 24000)  # Official uses 24000
        
        # Set environment variable for tokenizers
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    def load_model(self) -> None:
        """Load dots.ocr model using exact Modal Notebooks implementation."""
        try:
            logger.info(f"Loading dots.ocr from {self.model_path}")
            
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Build loading kwargs using base class method
            load_kwargs = self._get_load_kwargs()
            
            # Official Modal Notebooks parameters
            load_kwargs.update({
                'torch_dtype': torch.bfloat16,  # Official uses bfloat16
                'trust_remote_code': True,
                'attn_implementation': "eager"  # Fallback since we don't have flash_attention_2
            })
            
            # Try PyTorch SDPA with Flash Attention backend first
            try:
                # Test PyTorch SDPA Flash Attention availability
                with torch.backends.cuda.sdp_kernel(enable_flash=True):
                    test_tensor = torch.randn(1, 1, 10, 64, device='cuda', dtype=torch.bfloat16)
                    torch.nn.functional.scaled_dot_product_attention(test_tensor, test_tensor, test_tensor)
                
                load_kwargs['attn_implementation'] = "sdpa"
                logger.info("✅ Используем PyTorch SDPA с Flash Attention backend - МАКСИМАЛЬНАЯ ПРОИЗВОДИТЕЛЬНОСТЬ!")
                
            except Exception as e:
                logger.warning(f"⚠️ PyTorch SDPA Flash недоступен: {e}")
                
                # Fallback to external flash attention
                try:
                    import flash_attn
                    load_kwargs['attn_implementation'] = "flash_attention_2"
                    logger.info("✅ Используем внешний flash_attention_2")
                except ImportError:
                    logger.warning("⚠️ Flash attention недоступен - используем eager (медленнее)")
                    logger.info("💡 PyTorch SDPA рекомендуется для лучшей производительности")
                    load_kwargs['attn_implementation'] = "eager"
            
            # Load model (exact Modal implementation)
            logger.info("Loading model weights...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **load_kwargs
            )
            
            # Load processor (exact Modal implementation)
            self.processor = AutoProcessor.from_pretrained(
                self.model_path, 
                trust_remote_code=True, 
                use_fast=True
            )
            
            self.model.eval()
            logger.info("dots.ocr loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load dots.ocr: {e}")
            raise
    
    def _get_official_prompt(self, mode: str = "ocr") -> str:
        """Get official prompt from dots.ocr repository."""
        try:
            from dots_ocr.utils import dict_promptmode_to_prompt
            
            if mode == "layout_all":
                return dict_promptmode_to_prompt["prompt_layout_all_en"]
            elif mode == "ocr":
                return dict_promptmode_to_prompt["ocr"]
            else:
                return dict_promptmode_to_prompt.get(mode, dict_promptmode_to_prompt["ocr"])
                
        except ImportError:
            logger.warning("dots_ocr.utils not found, using fallback prompts")
            # Fallback prompts
            if mode == "layout_all":
                return """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

1. Bbox format: [x1, y1, x2, y2]
2. Layout Categories: The possible categories are ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title'].
3. Text Extraction & Formatting Rules:
   - Picture: For the 'Picture' category, the text field should be omitted.
   - Formula: Format its text as LaTeX.
   - Table: Format its text as HTML.
   - All Others (Text, Title, etc.): Format their text as Markdown.
4. Constraints:
   - The output text must be the original text from the image, with no translation.
   - All layout elements must be sorted according to human reading order.
5. Final Output: The entire output must be a single JSON object."""
            else:
                return "Extract all text from this image."
    
    def inference(self, image_path_or_pil, prompt: str):
        """Точная копия функции inference из Modal Notebooks."""
        try:
            # Handle both file path and PIL Image (exact Modal implementation)
            if isinstance(image_path_or_pil, str):
                image_for_messages = image_path_or_pil
            else:
                # For PIL Image, use it directly
                image_for_messages = image_path_or_pil
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image_for_messages},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
            # Preparation for inference (exact Modal implementation)
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Process vision info using qwen_vl_utils (exact Modal implementation)
            from qwen_vl_utils import process_vision_info
            image_inputs, video_inputs = process_vision_info(messages)
            
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            
            # Move to model device (CPU or GPU)
            device = next(self.model.parameters()).device
            inputs = inputs.to(device)
            
            # Inference: Generation of the output (exact Modal implementation)
            generated_ids = self.model.generate(**inputs, max_new_tokens=24000)
            
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            (output_text,) = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )
            
            # Return parsed JSON (exact Modal implementation)
            return json.loads(output_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Raw output: {output_text}")
            return output_text
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"[dots.ocr error: {e}]"
    
    def process_image(self, image: Image.Image, prompt: Optional[str] = None, 
                     mode: Optional[str] = None, bbox: Optional[List[int]] = None) -> str:
        """Process image with dots.ocr using official API."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            mode = mode or self.prompt_mode
            if prompt is None:
                prompt = self._get_official_prompt(mode)
            
            logger.info(f"Processing with mode: {mode}")
            
            # Validate image
            if image is None:
                raise ValueError("Image is None")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Use official inference method
            result = self.inference(image, prompt)
            
            logger.info("Processing completed successfully")
            
            # Handle different result types
            if isinstance(result, list):
                # If result is already a list (JSON parsed), convert to string
                import json
                return json.dumps(result, ensure_ascii=False)
            elif isinstance(result, str):
                return result.strip() if result else "[dots.ocr: Empty result]"
            else:
                return str(result) if result else "[dots.ocr: Empty result]"
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"[dots.ocr error: {e}]"
    
    def chat(self, image: Image.Image, prompt: str, **kwargs) -> str:
        """Chat with model."""
        return self.process_image(image, prompt=prompt, **kwargs)
    
    def parse_document(self, image: Image.Image, return_json: bool = True) -> Dict[str, Any]:
        """Parse document with layout using official layout_all mode."""
        result = self.process_image(image, mode="layout_all")
        if return_json:
            try:
                # Try to parse as JSON (official output format)
                parsed = json.loads(result)
                return parsed
            except json.JSONDecodeError:
                logger.warning("Result is not valid JSON, returning as text")
                return {"raw_text": result, "error": "Invalid JSON"}
        return {"raw_text": result}
    
    def extract_text_only(self, image: Image.Image) -> str:
        """Extract only text without layout information."""
        return self.process_image(image, mode="ocr")
    
    def unload(self) -> None:
        """Unload model."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("dots.ocr unloaded")