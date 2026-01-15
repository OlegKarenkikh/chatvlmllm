"""Base class for all VLM models."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from PIL import Image
import torch


class BaseVLMModel(ABC):
    """Abstract base class for Vision Language Models."""
    
    def __init__(self, model_id: str, device: str = "auto", precision: str = "fp16"):
        """
        Initialize the base model.
        
        Args:
            model_id: HuggingFace model identifier
            device: Device to run the model on ('cuda', 'cpu', or 'auto')
            precision: Model precision ('fp16', 'fp32', 'int8')
        """
        self.model_id = model_id
        self.device = self._get_device(device)
        self.precision = precision
        self.model = None
        self.processor = None
        
    def _get_device(self, device: str) -> str:
        """Determine the device to use."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the model and processor."""
        pass
    
    @abstractmethod
    def process_image(self, image: Image.Image, prompt: str = "") -> str:
        """
        Process an image and return text output.
        
        Args:
            image: PIL Image to process
            prompt: Optional text prompt for the model
            
        Returns:
            Extracted or generated text
        """
        pass
    
    @abstractmethod
    def chat(self, image: Image.Image, message: str, history: List[Dict] = None) -> str:
        """
        Interactive chat with the model about an image.
        
        Args:
            image: PIL Image for context
            message: User message
            history: Conversation history
            
        Returns:
            Model response
        """
        pass
    
    def extract_fields(self, text: str, template: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Extract structured fields from OCR text.
        
        Args:
            text: OCR output text
            template: Field template dictionary
            
        Returns:
            Dictionary of extracted fields
        """
        # Basic implementation - can be overridden by specific models
        fields = {}
        for field in template.get("fields", []):
            # Simple keyword search - can be enhanced with LLM
            fields[field] = self._extract_field_value(text, field)
        return fields
    
    def _extract_field_value(self, text: str, field_name: str) -> str:
        """Extract a single field value from text."""
        # Placeholder implementation
        lines = text.split('\n')
        for line in lines:
            if field_name.lower() in line.lower():
                # Try to extract value after field name
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
        return ""
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_id": self.model_id,
            "device": self.device,
            "precision": self.precision,
            "loaded": self.model is not None
        }
    
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