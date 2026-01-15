"""dots.ocr model integration following official recommendations.

Official: https://huggingface.co/rednote-hilab/dots.ocr
GitHub: https://github.com/rednote-hilab/dots.ocr

dots.ocr is a 1.7B parameter multilingual document parser with SOTA performance.
"""

from typing import Any, Dict, List, Optional
from PIL import Image
import torch
import json

from models.base_model import BaseModel
from utils.logger import logger


class DotsOCRModel(BaseModel):
    """dots.ocr for unified document parsing."""
    
    PROMPT_MODES = {
        "layout_all": "Parse all layout with detection and recognition",
        "layout_only": "Layout detection only",
        "ocr_only": "Text recognition only",
        "grounding_ocr": "OCR with bbox grounding"
    }
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
        self.prompt_mode = config.get('prompt_mode', 'layout_all')
        self.max_new_tokens = config.get('max_new_tokens', 24000)
    
    def load_model(self) -> None:
        """Load dots.ocr model."""
        try:
            logger.info(f"Loading dots.ocr from {self.model_path}")
            
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            self.processor = AutoProcessor.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            load_kwargs = {
                'device_map': self.device_map,
                'trust_remote_code': True,
            }
            
            if self.precision == "fp16":
                load_kwargs['torch_dtype'] = torch.float16
            elif self.precision == "bf16":
                load_kwargs['torch_dtype'] = torch.bfloat16
            elif self.precision == "int8":
                load_kwargs['load_in_8bit'] = True
            else:
                load_kwargs['torch_dtype'] = torch.bfloat16
            
            if self.config.get('use_flash_attention', False):
                load_kwargs['attn_implementation'] = "flash_attention_2"
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **load_kwargs
            )
            
            self.model.eval()
            logger.info("dots.ocr loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load dots.ocr: {e}")
            raise
    
    def _get_prompt(self, mode: str = "layout_all") -> str:
        """Get prompt for mode."""
        prompts = {
            "layout_all": (
                "Please output the layout information from the PDF image, including bbox, category, and text.\n"
                "1. Bbox: [x1, y1, x2, y2]\n"
                "2. Categories: ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', "
                "'Picture', 'Section-header', 'Table', 'Text', 'Title']\n"
                "3. Rules: Picture=no text, Formula=LaTeX, Table=HTML, Others=Markdown\n"
                "4. Output: Single JSON object, reading order"
            ),
            "layout_only": "Detect layout elements with bbox and category. Output JSON.",
            "ocr_only": "Extract all text, excluding headers/footers. Plain text, reading order.",
            "grounding_ocr": "Extract text from specified bbox region."
        }
        return prompts.get(mode, prompts["layout_all"])
    
    def process_image(self, image: Image.Image, prompt: Optional[str] = None, 
                     mode: Optional[str] = None, bbox: Optional[List[int]] = None) -> str:
        """Process image with dots.ocr."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            mode = mode or self.prompt_mode
            if prompt is None:
                prompt = self._get_prompt(mode)
                if mode == "grounding_ocr" and bbox:
                    prompt += f"\nBbox: {bbox}"
            
            logger.info(f"Processing with mode: {mode}")
            
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }]
            
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            try:
                from qwen_vl_utils import process_vision_info
                image_inputs, video_inputs = process_vision_info(messages)
            except:
                image_inputs, video_inputs = [image], None
            
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            
            device = next(self.model.parameters()).device
            inputs = inputs.to(device)
            
            with torch.no_grad():
                generated_ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
            
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
            
            logger.info("Processing completed")
            return output
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
    
    def chat(self, image: Image.Image, prompt: str, **kwargs) -> str:
        """Chat with model."""
        return self.process_image(image, prompt=prompt, **kwargs)
    
    def parse_document(self, image: Image.Image, return_json: bool = True) -> Dict[str, Any]:
        """Parse document with layout."""
        result = self.process_image(image, mode="layout_all")
        if return_json:
            try:
                return json.loads(result)
            except:
                return {"raw_text": result, "error": "Invalid JSON"}
        return {"raw_text": result}
    
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