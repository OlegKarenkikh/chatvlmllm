"""Base class for VLM models."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from PIL import Image
import torch


class BaseVLMModel(ABC):
    """Abstract base class for Vision Language Models."""
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize base VLM model.
        
        Args:
            model_config: Configuration dictionary for the model
        """
        self.model_config = model_config
        self.model_name = model_config.get("name")
        self.model_id = model_config.get("model_id")
        self.device = self._setup_device()
        self.model = None
        self.processor = None
        
    def _setup_device(self) -> str:
        """Setup computation device (CPU/GPU)."""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the model and processor."""
        pass
    
    @abstractmethod
    def process_image(self, image: Image.Image, **kwargs) -> Dict[str, Any]:
        """Process image and return results."""
        pass
    
    @abstractmethod
    def extract_text(self, image: Image.Image) -> str:
        """Extract text from image."""
        pass
    
    def extract_fields(self, text: str, template: Dict[str, List[str]]) -> Dict[str, str]:
        """Extract structured fields from text using template."""
        fields = {}
        lines = text.split('\n')
        
        for field_name in template.get('fields', []):
            # Simple pattern matching for field extraction
            for line in lines:
                if field_name.lower() in line.lower():
                    # Extract value after colon or field name
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        fields[field_name] = parts[1].strip()
                        break
            
            if field_name not in fields:
                fields[field_name] = ""
        
        return fields
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'name': self.model_name,
            'model_id': self.model_id,
            'device': self.device,
            'loaded': self.is_loaded(),
            'config': self.model_config
        }