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
            device: Device to load model on ('cuda', 'cpu', or 'auto')
            precision: Model precision ('fp16', 'fp32', 'int8')
        """
        self.model_id = model_id
        self.device = self._setup_device(device)
        self.precision = precision
        self.model = None
        self.processor = None
        
    def _setup_device(self, device: str) -> str:
        """Setup and validate device."""
        if device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the model and processor."""
        pass
    
    @abstractmethod
    def process_image(self, image: Image.Image, prompt: str = "") -> str:
        """Process an image and return text output.
        
        Args:
            image: PIL Image object
            prompt: Optional text prompt for the model
            
        Returns:
            Extracted text or model response
        """
        pass
    
    @abstractmethod
    def extract_fields(self, image: Image.Image, field_names: List[str]) -> Dict[str, str]:
        """Extract specific fields from a document image.
        
        Args:
            image: PIL Image object
            field_names: List of field names to extract
            
        Returns:
            Dictionary mapping field names to extracted values
        """
        pass
    
    def chat(self, image: Image.Image, message: str, history: Optional[List[Dict]] = None) -> str:
        """Interactive chat about an image.
        
        Args:
            image: PIL Image object
            message: User message
            history: Optional conversation history
            
        Returns:
            Model response
        """
        return self.process_image(image, message)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            "model_id": self.model_id,
            "device": self.device,
            "precision": self.precision,
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