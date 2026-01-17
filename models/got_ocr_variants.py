"""GOT-OCR 2.0 variants (UCAS and HuggingFace versions).

This module provides wrappers for different GOT-OCR implementations:
- ucaslcl/GOT-OCR2_0 (UCAS version)
- stepfun-ai/GOT-OCR-2.0-hf (HuggingFace version)

Both are variants of the same GOT-OCR 2.0 model with potentially different
implementations or optimizations.
"""

from typing import Any, Dict, Optional
from PIL import Image
import torch

from models.base_model import BaseModel
from utils.logger import logger


class GOTOCRUCASModel(BaseModel):
    """GOT-OCR 2.0 UCAS version (ucaslcl/GOT-OCR2_0)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.tokenizer = None
        
        # GOT-OCR specific settings
        self.ocr_type = config.get('ocr_type', 'format')
        self.ocr_color = config.get('ocr_color', '')
    
    def load_model(self) -> None:
        """Load GOT-OCR UCAS model."""
        try:
            logger.info(f"Loading GOT-OCR UCAS from {self.model_path}")
            
            from transformers import AutoModel, AutoTokenizer
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
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
            elif self.precision == "int8":
                load_kwargs['load_in_8bit'] = True
            
            # Load model
            self.model = AutoModel.from_pretrained(
                self.model_path,
                **load_kwargs
            )
            
            self.model.eval()
            logger.info("GOT-OCR UCAS loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load GOT-OCR UCAS: {e}")
            raise
    
    def process_image(
        self,
        image: Image.Image,
        ocr_type: Optional[str] = None,
        ocr_color: Optional[str] = None
    ) -> str:
        """Process image with GOT-OCR UCAS.
        
        Args:
            image: PIL Image to process
            ocr_type: OCR type ('format', 'ocr', 'multi-crop')
            ocr_color: Optional color specification
            
        Returns:
            Extracted text
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded")
        
        try:
            ocr_type = ocr_type or self.ocr_type
            ocr_color = ocr_color or self.ocr_color
            
            logger.info(f"Processing image with GOT-OCR UCAS (type: {ocr_type})")
            
            with torch.no_grad():
                if hasattr(self.model, 'chat'):
                    result = self.model.chat(
                        self.tokenizer,
                        image,
                        ocr_type=ocr_type,
                        ocr_color=ocr_color
                    )
                else:
                    # Fallback implementation
                    result = self._basic_inference(image)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _basic_inference(self, image: Image.Image) -> str:
        """Basic inference fallback."""
        return "[GOT-OCR UCAS inference - implement based on model API]"
    
    def chat(self, image: Image.Image, prompt: str, **kwargs) -> str:
        """Chat interface (returns OCR result)."""
        return self.process_image(image)
    
    def unload(self) -> None:
        """Unload model from memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("GOT-OCR UCAS unloaded")


class GOTOCRHFModel(BaseModel):
    """GOT-OCR 2.0 HuggingFace version (stepfun-ai/GOT-OCR-2.0-hf)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
        
        # GOT-OCR specific settings
        self.ocr_type = config.get('ocr_type', 'format')
        self.ocr_color = config.get('ocr_color', '')
    
    def load_model(self) -> None:
        """Load GOT-OCR HF model."""
        try:
            logger.info(f"Loading GOT-OCR HF from {self.model_path}")
            
            from transformers import AutoModel, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Load processor
            self.processor = AutoProcessor.from_pretrained(
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
            elif self.precision == "int8":
                load_kwargs['load_in_8bit'] = True
            
            # Load model
            self.model = AutoModel.from_pretrained(
                self.model_path,
                **load_kwargs
            )
            
            self.model.eval()
            logger.info("GOT-OCR HF loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load GOT-OCR HF: {e}")
            raise
    
    def process_image(
        self,
        image: Image.Image,
        ocr_type: Optional[str] = None,
        ocr_color: Optional[str] = None
    ) -> str:
        """Process image with GOT-OCR HF.
        
        Args:
            image: PIL Image to process
            ocr_type: OCR type ('format', 'ocr', 'multi-crop')
            ocr_color: Optional color specification
            
        Returns:
            Extracted text
        """
        if self.model is None or self.processor is None:
            raise RuntimeError("Model not loaded")
        
        try:
            ocr_type = ocr_type or self.ocr_type
            ocr_color = ocr_color or self.ocr_color
            
            logger.info(f"Processing image with GOT-OCR HF (type: {ocr_type})")
            
            # Process image
            inputs = self.processor(image, return_tensors="pt")
            
            # Move to device
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                if hasattr(self.model, 'generate'):
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=2048,
                        do_sample=False
                    )
                    result = self.processor.decode(outputs[0], skip_special_tokens=True)
                else:
                    # Alternative inference method
                    result = self._basic_inference(image)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _basic_inference(self, image: Image.Image) -> str:
        """Basic inference fallback."""
        return "[GOT-OCR HF inference - implement based on model API]"
    
    def chat(self, image: Image.Image, prompt: str, **kwargs) -> str:
        """Chat interface (returns OCR result)."""
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
        logger.info("GOT-OCR HF unloaded")