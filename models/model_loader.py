"""Model loader utility."""

from typing import Dict, Optional
import yaml
from pathlib import Path

from .base_model import BaseVLMModel
from .got_ocr import GOTOCRModel
from .qwen_vl import Qwen2VLModel


class ModelLoader:
    """Factory for loading VLM models."""
    
    _model_classes = {
        "got_ocr": GOTOCRModel,
        "qwen_vl_2b": Qwen2VLModel,
        "qwen_vl_7b": Qwen2VLModel,
    }
    
    _loaded_models: Dict[str, BaseVLMModel] = {}
    
    @classmethod
    def load_config(cls, config_path: str = "config.yaml") -> Dict:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    @classmethod
    def load(cls, model_name: str, config: Optional[Dict] = None, force_reload: bool = False) -> BaseVLMModel:
        """
        Load a VLM model.
        
        Args:
            model_name: Model identifier from config
            config: Optional config dict (loads from file if not provided)
            force_reload: Force reload even if already loaded
            
        Returns:
            Loaded model instance
        """
        # Return cached model if available
        if model_name in cls._loaded_models and not force_reload:
            print(f"Using cached {model_name} model")
            return cls._loaded_models[model_name]
        
        # Load config if not provided
        if config is None:
            config = cls.load_config()
        
        # Get model config
        if model_name not in config.get("models", {}):
            raise ValueError(f"Unknown model: {model_name}")
        
        model_config = config["models"][model_name]
        
        # Get model class
        if model_name not in cls._model_classes:
            raise ValueError(f"No implementation for model: {model_name}")
        
        model_class = cls._model_classes[model_name]
        
        # Create and load model
        print(f"Loading {model_config['name']}...")
        model = model_class(
            model_id=model_config["model_id"],
            device=model_config.get("device_map", "auto"),
            precision=model_config.get("precision", "fp16")
        )
        
        model.load_model()
        
        # Cache model
        cls._loaded_models[model_name] = model
        
        return model
    
    @classmethod
    def unload(cls, model_name: str) -> None:
        """Unload a model from memory."""
        if model_name in cls._loaded_models:
            print(f"Unloading {model_name}...")
            cls._loaded_models[model_name].unload()
            del cls._loaded_models[model_name]
    
    @classmethod
    def unload_all(cls) -> None:
        """Unload all loaded models."""
        for model_name in list(cls._loaded_models.keys()):
            cls.unload(model_name)
    
    @classmethod
    def get_available_models(cls, config: Optional[Dict] = None) -> Dict[str, Dict]:
        """Get list of available models from config."""
        if config is None:
            config = cls.load_config()
        return config.get("models", {})
    
    @classmethod
    def is_loaded(cls, model_name: str) -> bool:
        """Check if a model is loaded."""
        return model_name in cls._loaded_models