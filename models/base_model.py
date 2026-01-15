"""Base class for VLM models."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from PIL import Image
import torch


class BaseVLMModel(ABC):
    """Abstract base class for Vision Language Models."""
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        """
        Initialize base VLM model.
        
        Args:
            model_id: HuggingFace model identifier
            config: Model configuration dictionary
        """
        self.model_id = model_id
        self.config = config
        self.model = None
        self.processor = None
        self.device = self._get_device()
        
    def _get_device(self) -> str:
        """Determine optimal device for model inference."""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    @abstractmethod
    def load_model(self) -> None:
        """Load model and processor from HuggingFace."""
        pass
    
    @abstractmethod
    def process_image(self, image: Image.Image, prompt: Optional[str] = None) -> str:
        """
        Process image and return text output.
        
        Args:
            image: PIL Image object
            prompt: Optional prompt for the model
            
        Returns:
            Extracted text or model response
        """
        pass
    
    def extract_fields(self, text: str, fields: List[str]) -> Dict[str, str]:
        """
        Extract structured fields from text.
        
        Args:
            text: Raw text from OCR
            fields: List of field names to extract
            
        Returns:
            Dictionary mapping field names to extracted values
        """
        result = {}
        
        for field in fields:
            # Basic field extraction logic
            # TODO: Implement more sophisticated extraction
            result[field] = self._extract_single_field(text, field)
        
        return result
    
    def _extract_single_field(self, text: str, field: str) -> str:
        """
        Extract single field from text.
        
        Args:
            text: Source text
            field: Field name to extract
            
        Returns:
            Extracted field value or empty string
        """
        # Simple keyword-based extraction
        # In production, use NER or structured prompting
        lines = text.split('\n')
        field_lower = field.lower()
        
        for i, line in enumerate(lines):
            if field_lower in line.lower():
                # Try to extract value after colon or on next line
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        return parts[1].strip()
                elif i + 1 < len(lines):
                    return lines[i + 1].strip()
        
        return ""
    
    def chat(self, image: Image.Image, message: str, history: List[Dict[str, str]] = None) -> str:
        """
        Interactive chat with image context.
        
        Args:
            image: Context image
            message: User message
            history: Chat history
            
        Returns:
            Model response
        """
        # Default implementation uses process_image
        # Override in subclasses for proper chat support
        return self.process_image(image, message)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and statistics."""
        return {
            "model_id": self.model_id,
            "device": self.device,
            "config": self.config,
            "loaded": self.model is not None
        }
    
    def unload_model(self) -> None:
        """Unload model from memory."""
        if self.model is not None:
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()