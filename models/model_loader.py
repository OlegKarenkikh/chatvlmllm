"""Model loader utility."""

from typing import Dict, Any, Optional
import yaml
from pathlib import Path

from .base_model import BaseVLMModel
from .got_ocr import GOTOCRModel
from .qwen_vl import Qwen2VLModel


class ModelLoader:
    """Factory class for loading VLM models."""
    
    _models_cache: Dict[str, BaseVLMModel] = {}
    
    MODEL_CLASSES = {
        'got_ocr': GOTOCRModel,
        'qwen_vl_2b': Qwen2VLModel,
        'qwen_vl_7b': Qwen2VLModel,
    }
    
    @classmethod
    def load_config(cls, config_path: str = "config.yaml") -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def load(cls, model_key: str, config_path: str = "config.yaml", 
             force_reload: bool = False) -> BaseVLMModel:
        """
        Load a VLM model by key.
        
        Args:
            model_key: Key identifying the model in config
            config_path: Path to configuration file
            force_reload: Force reload even if cached
            
        Returns:
            Loaded VLM model instance
        """
        # Check cache
        if not force_reload and model_key in cls._models_cache:
            cached_model = cls._models_cache[model_key]
            if cached_model.is_loaded():
                print(f"Using cached {cached_model.model_name}")
                return cached_model
        
        # Load config
        config = cls.load_config(config_path)
        
        if model_key not in config['models']:
            raise ValueError(f"Model '{model_key}' not found in configuration")
        
        model_config = config['models'][model_key]
        
        # Get model class
        if model_key not in cls.MODEL_CLASSES:
            raise ValueError(f"No implementation found for model: {model_key}")
        
        model_class = cls.MODEL_CLASSES[model_key]
        
        # Create and load model
        model = model_class(model_config)
        model.load_model()
        
        # Cache model
        cls._models_cache[model_key] = model
        
        return model
    
    @classmethod
    def get_available_models(cls, config_path: str = "config.yaml") -> Dict[str, Dict[str, Any]]:
        """Get list of available models from config."""
        config = cls.load_config(config_path)
        return config.get('models', {})
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear model cache."""
        cls._models_cache.clear()
        print("Model cache cleared")