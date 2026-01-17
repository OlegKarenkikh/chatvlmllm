"""DeepSeek OCR model integration.

Official: https://huggingface.co/deepseek-ai/deepseek-ocr
GitHub: https://github.com/deepseek-ai

DeepSeek OCR is a lightweight OCR model from DeepSeek AI with:
- Efficient inference
- Good accuracy for document OCR
- Small model size
- Fast processing
"""

from typing import Any, Dict, Optional, Union
from PIL import Image
import torch

from models.base_model import BaseModel
from utils.logger import logger


class DeepSeekOCRModel(BaseModel):
    """DeepSeek OCR model."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
    
    def load_model(self) -> None:
        """Load DeepSeek OCR model."""
        try:
            logger.info(f"Loading DeepSeek OCR from {self.model_path}")
            
            from transformers import AutoModel, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Load processor
            try:
                self.processor = AutoProcessor.from_pretrained(
                    self.model_path,
                    trust_remote_code=True
                )
            except Exception:
                # Fallback to tokenizer if processor not available
                from transformers import AutoTokenizer
                self.processor = AutoTokenizer.from_pretrained(
                    self.model_path,
                    trust_remote_code=True
                )
            
            # Build loading kwargs
            load_kwargs = {
                'trust_remote_code': True,
                'device_map': self.device_map,
            }
            
            # Set precision
            if self.precision == "fp16":
                load_kwargs['torch_dtype'] = torch.float16
            elif self.precision == "bf16":
                load_kwargs['torch_dtype'] = torch.bfloat16
            elif self.precision == "int8":
                load_kwargs['load_in_8bit'] = True
            elif self.precision == "int4":
                from transformers import BitsAndBytesConfig
                load_kwargs['quantization_config'] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load model
            logger.info("Loading model weights...")
            self.model = AutoModel.from_pretrained(
                self.model_path,
                **load_kwargs
            )
            
            self.model.eval()
            logger.info("DeepSeek OCR loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load DeepSeek OCR: {e}")
            raise
    
    def process_image(
        self,
        image: Union[Image.Image, str],
        prompt: Optional[str] = None
    ) -> str:
        """Process image with DeepSeek OCR.
        
        Args:
            image: PIL Image or image path
            prompt: Optional prompt (for OCR, usually not needed)
            
        Returns:
            Extracted text
        """
        if self.model is None or self.processor is None:
            raise RuntimeError("Model not loaded")
        
        try:
            logger.info("Processing image with DeepSeek OCR")
            
            # Process image
            if hasattr(self.processor, 'process'):
                # If processor has process method
                inputs = self.processor.process(image, return_tensors="pt")
            elif hasattr(self.processor, '__call__'):
                # If processor is callable
                inputs = self.processor(image, return_tensors="pt")
            else:
                # Fallback: basic preprocessing
                inputs = self._preprocess_image(image)
            
            # Move to device
            device = next(self.model.parameters()).device
            if isinstance(inputs, dict):
                inputs = {k: v.to(device) if torch.is_tensor(v) else v for k, v in inputs.items()}
            else:
                inputs = inputs.to(device)
            
            # Generate text
            with torch.no_grad():
                if hasattr(self.model, 'generate'):
                    outputs = self.model.generate(
                        **inputs if isinstance(inputs, dict) else {'input_ids': inputs},
                        max_new_tokens=2048,
                        do_sample=False,
                        pad_token_id=self.processor.pad_token_id if hasattr(self.processor, 'pad_token_id') else 0
                    )
                    
                    # Decode output
                    if hasattr(self.processor, 'decode'):
                        result = self.processor.decode(outputs[0], skip_special_tokens=True)
                    else:
                        result = self._decode_output(outputs[0])
                        
                elif hasattr(self.model, 'forward'):
                    # Direct forward pass
                    outputs = self.model(**inputs if isinstance(inputs, dict) else {'input_ids': inputs})
                    result = self._process_outputs(outputs)
                else:
                    # Fallback
                    result = self._basic_inference(image)
            
            logger.info("OCR processing completed")
            return result.strip() if isinstance(result, str) else str(result)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Basic image preprocessing fallback."""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Basic tensor conversion (placeholder)
        import torchvision.transforms as transforms
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return transform(image).unsqueeze(0)
    
    def _decode_output(self, output_ids: torch.Tensor) -> str:
        """Basic output decoding fallback."""
        # This is a placeholder - actual implementation depends on model
        return f"[DeepSeek OCR output - tokens: {output_ids.shape}]"
    
    def _process_outputs(self, outputs) -> str:
        """Process model outputs."""
        # This is a placeholder - actual implementation depends on model architecture
        return "[DeepSeek OCR result - implement based on model outputs]"
    
    def _basic_inference(self, image: Image.Image) -> str:
        """Basic inference fallback."""
        return "[DeepSeek OCR inference - implement based on model API]"
    
    def chat(
        self,
        image: Union[Image.Image, str],
        prompt: str,
        **kwargs
    ) -> str:
        """Chat interface (primarily returns OCR result).
        
        Args:
            image: PIL Image or path
            prompt: User prompt
            **kwargs: Additional parameters
            
        Returns:
            OCR result or model response
        """
        # For OCR models, we primarily extract text
        ocr_result = self.process_image(image)
        
        # If prompt asks for specific processing, we could add logic here
        if "extract" in prompt.lower() or "ocr" in prompt.lower():
            return ocr_result
        else:
            return f"OCR Result: {ocr_result}"
    
    def extract_text(
        self,
        image: Union[Image.Image, str],
        language: Optional[str] = None
    ) -> str:
        """Extract text from image.
        
        Args:
            image: PIL Image or path
            language: Optional language hint (may not be used by all models)
            
        Returns:
            Extracted text
        """
        return self.process_image(image)
    
    def unload(self) -> None:
        """Unload model from memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("DeepSeek OCR unloaded")