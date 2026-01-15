"""Model loader and manager."""

from typing import Dict, Any, Optional
import yaml
from pathlib import Path

from .base_model import BaseVLMModel
from .got_ocr import GOTOCRModel
from .qwen_vl import Qwen2VLModel


class ModelLoader:
    """Factory for loading and managing VLM models."""
    
    _models = {
        "got_ocr": GOTOCRModel,
        "qwen_vl_2b": Qwen2VLModel,
        "qwen_vl_7b": Qwen2VLModel
    }
    
    _loaded_models: Dict[str, BaseVLMModel] = {}
    
    @classmethod
    def load_config(cls, config_path: str = "config.yaml") -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    @classmethod
    def load_model(cls, model_key: str, config_path: str = "config.yaml") -> BaseVLMModel:
        """
        Load a VLM model by key.
        
        Args:
            model_key: Model identifier from config (e.g., 'got_ocr', 'qwen_vl_2b')
            config_path: Path to configuration file
            
        Returns:
            Loaded model instance
        """
        # Check if already loaded
        if model_key in cls._loaded_models:
            print(f"Model {model_key} already loaded, returning cached instance")
            return cls._loaded_models[model_key]
        
        # Load config
        config = cls.load_config(config_path)
        
        if model_key not in config["models"]:
            raise ValueError(f"Model {model_key} not found in config")
        
        model_config = config["models"][model_key]
        model_id = model_config["model_id"]
        
        # Get model class
        if model_key not in cls._models:
            raise ValueError(f"No implementation for model: {model_key}")
        
        model_class = cls._models[model_key]
        
        # Create and load model
        print(f"Creating model instance: {model_key}")
        model = model_class(model_id, model_config)
        model.load_model()
        
        # Cache the model
        cls._loaded_models[model_key] = model
        
        return model
    
    @classmethod
    def unload_model(cls, model_key: str) -> None:
        """Unload a model from memory."""
        if model_key in cls._loaded_models:
            cls._loaded_models[model_key].unload_model()
            del cls._loaded_models[model_key]
            print(f"Model {model_key} unloaded")
    
    @classmethod
    def unload_all(cls) -> None:
        """Unload all models from memory."""
        for model_key in list(cls._loaded_models.keys()):
            cls.unload_model(model_key)
        print("All models unloaded")
    
    @classmethod
    def get_loaded_models(cls) -> list:
        """Get list of currently loaded models."""
        return list(cls._loaded_models.keys())
    
    @classmethod
    def get_available_models(cls, config_path: str = "config.yaml") -> Dict[str, Dict[str, Any]]:
        """Get all available models from config."""
        config = cls.load_config(config_path)
        return config["models"]