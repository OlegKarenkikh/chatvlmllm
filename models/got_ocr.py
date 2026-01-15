"""GOT-OCR 2.0 model integration."""

from typing import List, Dict
from PIL import Image
import torch
from transformers import AutoModel, AutoTokenizer

from .base_model import BaseVLMModel


class GOTOCRModel(BaseVLMModel):
    """GOT-OCR 2.0 specialized OCR model."""
    
    def __init__(self, model_id: str = "stepfun-ai/GOT-OCR2_0", **kwargs):
        super().__init__(model_id, **kwargs)
        self.tokenizer = None
        
    def load_model(self) -> None:
        """Load GOT-OCR model and tokenizer."""
        try:
            print(f"Loading GOT-OCR model from {self.model_id}...")
            
            # Load model with appropriate settings
            load_kwargs = {
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }
            
            if self.device == "cuda":
                load_kwargs["device_map"] = "auto"
                if self.precision == "fp16":
                    load_kwargs["torch_dtype"] = torch.float16
                elif self.precision == "int8":
                    load_kwargs["load_in_8bit"] = True
            
            self.model = AutoModel.from_pretrained(
                self.model_id,
                **load_kwargs
            )
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            print(f"GOT-OCR model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"Error loading GOT-OCR model: {e}")
            raise
    
    def process_image(self, image: Image.Image, prompt: str = "") -> str:
        """
        Process image with GOT-OCR for text extraction.
        
        Args:
            image: PIL Image to process
            prompt: OCR mode or specific instructions
            
        Returns:
            Extracted text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # GOT-OCR specific processing
            # Default to plain OCR if no prompt specified
            if not prompt:
                prompt = "ocr"
            
            # Process with model
            with torch.no_grad():
                result = self.model.chat(
                    self.tokenizer,
                    image,
                    ocr_type=prompt
                )
            
            return result
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return f"Error: {str(e)}"
    
    def chat(self, image: Image.Image, message: str, history: List[Dict] = None) -> str:
        """
        GOT-OCR is primarily for OCR, but can handle basic queries.
        
        Args:
            image: PIL Image
            message: User question
            history: Not used for GOT-OCR
            
        Returns:
            Response text
        """
        # GOT-OCR is not designed for chat, so we route to OCR processing
        return self.process_image(image, prompt="ocr")
    
    def extract_structured_text(self, image: Image.Image, format_type: str = "markdown") -> str:
        """
        Extract text with structure preservation.
        
        Args:
            image: Input image
            format_type: Output format ('markdown', 'latex', 'plain')
            
        Returns:
            Formatted text
        """
        if format_type == "markdown":
            return self.process_image(image, prompt="format")
        elif format_type == "latex":
            return self.process_image(image, prompt="ocr")
        else:
            return self.process_image(image, prompt="ocr")