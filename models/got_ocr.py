"""GOT-OCR 2.0 model integration."""

from typing import Optional
from PIL import Image
import torch
from transformers import AutoModel, AutoTokenizer

from .base_model import BaseVLMModel


class GOTOCRModel(BaseVLMModel):
    """GOT-OCR 2.0 specialized OCR model."""
    
    def load_model(self) -> None:
        """Load GOT-OCR model and tokenizer."""
        print(f"Loading GOT-OCR model: {self.model_id}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            # Load model with device mapping
            self.model = AutoModel.from_pretrained(
                self.model_id,
                trust_remote_code=True,
                device_map=self.config.get("device_map", "auto"),
                torch_dtype=torch.float16 if self.config.get("precision") == "fp16" else torch.float32,
                low_cpu_mem_usage=True
            )
            
            self.model.eval()
            print(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def process_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """
        Process image with GOT-OCR.
        
        Args:
            image: PIL Image object
            prompt: Optional OCR mode (e.g., 'ocr', 'format', 'table')
            
        Returns:
            Extracted text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Default OCR mode
            ocr_type = prompt if prompt in ['ocr', 'format', 'table'] else 'ocr'
            
            # Process image through model
            with torch.no_grad():
                result = self.model.chat(
                    self.tokenizer,
                    image,
                    ocr_type=ocr_type
                )
            
            return result
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return f"Error: {str(e)}"
    
    def process_with_boxes(self, image: Image.Image) -> dict:
        """
        Process image and return text with bounding boxes.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with text and box coordinates
        """
        if self.model is None:
            raise RuntimeError("Model not loaded.")
        
        try:
            # Use box output mode if supported
            with torch.no_grad():
                result = self.model.chat(
                    self.tokenizer,
                    image,
                    ocr_type='ocr',
                    render=True
                )
            
            return result
            
        except Exception as e:
            print(f"Error processing with boxes: {e}")
            return {"text": "", "boxes": []}