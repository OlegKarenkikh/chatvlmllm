"""dots.ocr model integration - FIXED VERSION.

Official: https://huggingface.co/rednote-hilab/dots.ocr
GitHub: https://github.com/rednote-hilab/dots.ocr

dots.ocr is a 1.7B parameter multilingual document parser with SOTA performance.
This is a simplified, robust version that avoids NoneType errors.
"""

from typing import Any, Dict, List, Optional
from PIL import Image
import torch
import json

from models.base_model import BaseModel
from utils.logger import logger


class DotsOCRModel(BaseModel):
    """dots.ocr for unified document parsing - FIXED VERSION."""
    
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
        self.tokenizer = None
        self.prompt_mode = config.get('prompt_mode', 'layout_all')
        self.max_new_tokens = config.get('max_new_tokens', 2000)  # Reduced for stability
    
    def load_model(self) -> None:
        """Load dots.ocr model with robust error handling."""
        try:
            logger.info(f"Loading dots.ocr from {self.model_path}")
            
            from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Load tokenizer first (most reliable)
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path,
                    trust_remote_code=True
                )
                logger.info("Tokenizer loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load tokenizer: {e}")
                raise
            
            # Try to load processor with fallback
            try:
                self.processor = AutoProcessor.from_pretrained(
                    self.model_path,
                    trust_remote_code=True
                )
                logger.info("Processor loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load AutoProcessor: {e}")
                # Use tokenizer as fallback
                self.processor = self.tokenizer
                logger.info("Using tokenizer as processor fallback")
            
            # Load model with base class method
            load_kwargs = self._get_load_kwargs()
            
            # Force eager attention for stability
            load_kwargs['attn_implementation'] = "eager"
            
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    **load_kwargs
                )
                
                # Move to device if not using device_map
                if not torch.cuda.is_available():
                    device = self._get_device()
                    self.model = self.model.to(device)
                
                self.model.eval()
                logger.info("dots.ocr loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
            
        except Exception as e:
            logger.error(f"Failed to load dots.ocr: {e}")
            raise
    
    def _get_prompt(self, mode: str = "layout_all") -> str:
        """Get prompt for mode."""
        prompts = {
            "layout_all": "Extract all text from this image with layout information.",
            "layout_only": "Detect layout elements in this image.",
            "ocr_only": "Extract all text from this image.",
            "grounding_ocr": "Extract text from specified region."
        }
        return prompts.get(mode, prompts["ocr_only"])
    
    def process_image(self, image: Image.Image, prompt: Optional[str] = None, 
                     mode: Optional[str] = None, bbox: Optional[List[int]] = None) -> str:
        """Process image with dots.ocr - ROBUST VERSION."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            mode = mode or self.prompt_mode
            if prompt is None:
                prompt = self._get_prompt(mode)
                if mode == "grounding_ocr" and bbox:
                    prompt += f" Focus on region: {bbox}"
            
            logger.info(f"Processing with mode: {mode}")
            
            # Validate image
            if image is None:
                raise ValueError("Image is None")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Simple, reliable processing
            try:
                # Method 1: Try with processor if available
                if hasattr(self.processor, 'apply_chat_template'):
                    result = self._process_with_chat_template(image, prompt)
                else:
                    result = self._process_simple(image, prompt)
                
                logger.info("Processing completed successfully")
                return result.strip() if result else "[dots.ocr: Empty result]"
                
            except Exception as e:
                logger.error(f"Processing failed: {e}")
                return f"[dots.ocr error: {e}]"
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"[dots.ocr error: {e}]"
    
    def _process_with_chat_template(self, image: Image.Image, prompt: str) -> str:
        """Process using chat template."""
        try:
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }]
            
            # Apply chat template
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            # Process inputs
            inputs = self.processor(
                text=[text],
                images=[image],
                padding=True,
                return_tensors="pt"
            )
            
            # Validate inputs
            if inputs is None:
                raise ValueError("Processor returned None")
            
            # Check required fields
            if 'input_ids' not in inputs or inputs['input_ids'] is None:
                raise ValueError("input_ids is None")
            
            # Move to device
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) if torch.is_tensor(v) else v for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    do_sample=False,
                    use_cache=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode
            if generated_ids is None:
                raise ValueError("Generation returned None")
            
            input_length = inputs['input_ids'].shape[1]
            if generated_ids.shape[1] <= input_length:
                return "[dots.ocr: No new tokens generated]"
            
            new_tokens = generated_ids[0][input_length:]
            result = self.processor.batch_decode([new_tokens], skip_special_tokens=True)[0]
            
            return result
            
        except Exception as e:
            logger.error(f"Chat template processing failed: {e}")
            raise
    
    def _process_simple(self, image: Image.Image, prompt: str) -> str:
        """Simple processing fallback."""
        try:
            # Tokenize prompt
            text_inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
            
            # Simple image processing
            import torchvision.transforms as transforms
            
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            pixel_values = transform(image).unsqueeze(0)
            
            # Combine inputs
            device = next(self.model.parameters()).device
            inputs = {
                'input_ids': text_inputs['input_ids'].to(device),
                'attention_mask': text_inputs['attention_mask'].to(device),
                'pixel_values': pixel_values.to(device)
            }
            
            # Generate
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    do_sample=False,
                    use_cache=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode
            if generated_ids is None:
                raise ValueError("Generation returned None")
            
            input_length = inputs['input_ids'].shape[1]
            if generated_ids.shape[1] <= input_length:
                return "[dots.ocr: No new tokens generated]"
            
            new_tokens = generated_ids[0][input_length:]
            result = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Simple processing failed: {e}")
            return f"[dots.ocr simple processing error: {e}]"
    
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
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("dots.ocr unloaded")