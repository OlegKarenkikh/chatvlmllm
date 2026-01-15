"""GOT-OCR 2.0 model implementation."""

from typing import Dict, List
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
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_id,
                trust_remote_code=True
            )
            
            # Load model with appropriate precision
            if self.precision == "fp16":
                self.model = AutoModel.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    device_map=self.device
                )
            elif self.precision == "int8":
                self.model = AutoModel.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                    load_in_8bit=True,
                    device_map=self.device
                )
            else:
                self.model = AutoModel.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                    device_map=self.device
                )
            
            self.model.eval()
            print("GOT-OCR model loaded successfully!")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load GOT-OCR model: {str(e)}")
    
    def process_image(self, image: Image.Image, prompt: str = "") -> str:
        """Extract text from image using GOT-OCR.
        
        Args:
            image: PIL Image object
            prompt: Optional OCR mode ('ocr', 'format', 'table')
            
        Returns:
            Extracted text
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Default to standard OCR if no prompt specified
            if not prompt:
                prompt = "ocr"
            
            # Process image based on mode
            with torch.no_grad():
                result = self.model.chat(
                    self.tokenizer,
                    image,
                    ocr_type=prompt
                )
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"OCR processing failed: {str(e)}")
    
    def extract_fields(self, image: Image.Image, field_names: List[str]) -> Dict[str, str]:
        """Extract specific fields from document.
        
        Args:
            image: PIL Image object
            field_names: List of field names to extract
            
        Returns:
            Dictionary with extracted field values
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # First, get all text from the document
            full_text = self.process_image(image, "ocr")
            
            # Create prompt for field extraction
            fields_str = ", ".join(field_names)
            prompt = f"Extract the following fields from the document: {fields_str}"
            
            # Use the model to extract structured data
            with torch.no_grad():
                result = self.model.chat(
                    self.tokenizer,
                    image,
                    ocr_type="ocr",
                    ocr_box="",
                    ocr_color=""
                )
            
            # Parse the result into fields
            # This is a simplified implementation - in production, you'd use more sophisticated parsing
            extracted_fields = {}
            for field in field_names:
                # Try to find the field in the text
                field_lower = field.lower()
                if field_lower in result.lower():
                    # Extract value after field name (simplified)
                    lines = result.split('\n')
                    for line in lines:
                        if field_lower in line.lower():
                            parts = line.split(':', 1)
                            if len(parts) > 1:
                                extracted_fields[field] = parts[1].strip()
                            break
                
                if field not in extracted_fields:
                    extracted_fields[field] = ""
            
            return extracted_fields
            
        except Exception as e:
            raise RuntimeError(f"Field extraction failed: {str(e)}")
    
    def extract_table(self, image: Image.Image) -> str:
        """Extract table structure from image.
        
        Args:
            image: PIL Image with table
            
        Returns:
            Structured table representation
        """
        return self.process_image(image, "table")
    
    def extract_formula(self, image: Image.Image) -> str:
        """Extract mathematical formulas from image.
        
        Args:
            image: PIL Image with formulas
            
        Returns:
            LaTeX representation of formulas
        """
        return self.process_image(image, "format")