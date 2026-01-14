"""GOT-OCR 2.0 model integration."""

from typing import Dict, Any, Optional
from PIL import Image
import torch
from .base_model import BaseVLMModel


class GOTOCRModel(BaseVLMModel):
    """GOT-OCR 2.0 model for document OCR."""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
        self.max_length = model_config.get("max_length", 2048)
        
    def load_model(self) -> None:
        """Load GOT-OCR model."""
        try:
            from transformers import AutoModel, AutoTokenizer
            
            print(f"Loading {self.model_name} from {self.model_id}...")
            
            # Load model with specified precision
            precision = self.model_config.get("precision", "fp16")
            torch_dtype = torch.float16 if precision == "fp16" else torch.float32
            
            self.model = AutoModel.from_pretrained(
                self.model_id,
                trust_remote_code=True,
                torch_dtype=torch_dtype,
                device_map=self.model_config.get("device_map", "auto"),
                low_cpu_mem_usage=True
            )
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            self.model.eval()
            print(f"✓ {self.model_name} loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"✗ Error loading {self.model_name}: {str(e)}")
            raise
    
    def process_image(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        """Process image with GOT-OCR."""
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            mode = kwargs.get('mode', 'ocr')
            
            # GOT-OCR specific processing
            if mode == 'ocr':
                result = self.model.chat(
                    self.tokenizer,
                    image,
                    ocr_type='ocr'
                )
            elif mode == 'format':
                result = self.model.chat(
                    self.tokenizer,
                    image,
                    ocr_type='format'
                )
            else:
                result = self.extract_text(image)
            
            return {
                'success': True,
                'text': result,
                'model': self.model_name,
                'mode': mode
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': self.model_name
            }
    
    def extract_text(self, image: Image.Image) -> str:
        """Extract plain text from image."""
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            result = self.model.chat(
                self.tokenizer,
                image,
                ocr_type='ocr'
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Text extraction failed: {str(e)}")
    
    def extract_table(self, image: Image.Image) -> str:
        """Extract table structure from image."""
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            result = self.model.chat(
                self.tokenizer,
                image,
                ocr_type='format',
                ocr_box=''
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Table extraction failed: {str(e)}")