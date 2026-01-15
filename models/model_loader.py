"""Model loader utility."""

from typing import Dict, Optional
import yaml
from pathlib import Path

from .base_model import BaseVLMModel
from .got_ocr import GOTOCRModel
from .qwen_vl import Qwen2VLModel


class ModelLoader:
    """Utility class for loading and managing VLM models."""
    
    _model_classes = {
        "got_ocr": GOTOCRModel,
        "qwen_vl_2b": Qwen2VLModel,
        "qwen_vl_7b": Qwen2VLModel,
    }
    
    _loaded_models: Dict[str, BaseVLMModel] = {}
    
    @classmethod
    def load_config(cls, config_path: str = "config.yaml") -> Dict:
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML config: {str(e)}")
    
    @classmethod
    def load_model(cls, model_name: str, config_path: str = "config.yaml") -> BaseVLMModel:
        """Load a model by name from configuration.
        
        Args:
            model_name: Name of the model from config (e.g., 'got_ocr', 'qwen_vl_2b')
            config_path: Path to configuration file
            
        Returns:
            Loaded model instance
        """
        # Check if model already loaded
        if model_name in cls._loaded_models:
            print(f"Model {model_name} already loaded, returning cached instance.")
            return cls._loaded_models[model_name]
        
        # Load config
        config = cls.load_config(config_path)
        
        if model_name not in config["models"]:
            raise ValueError(f"Model {model_name} not found in config. "
                           f"Available models: {list(config['models'].keys())}")
        
        # Get model config
        model_config = config["models"][model_name]
        
        # Get model class
        if model_name not in cls._model_classes:
            raise ValueError(f"No implementation for model: {model_name}")
        
        model_class = cls._model_classes[model_name]
        
        # Initialize model
        print(f"Initializing {model_config['name']}...")
        model = model_class(
            model_id=model_config["model_id"],
            device=model_config.get("device_map", "auto"),
            precision=model_config.get("precision", "fp16")
        )
        
        # Load model weights
        model.load_model()
        
        # Cache model
        cls._loaded_models[model_name] = model
        
        return model
    
    @classmethod
    def unload_model(cls, model_name: str) -> None:
        """Unload a model from memory.
        
        Args:
            model_name: Name of the model to unload
        """
        if model_name in cls._loaded_models:
            print(f"Unloading model {model_name}...")
            cls._loaded_models[model_name].unload_model()
            del cls._loaded_models[model_name]
            print(f"Model {model_name} unloaded.")
        else:
            print(f"Model {model_name} not loaded.")
    
    @classmethod
    def unload_all(cls) -> None:
        """Unload all loaded models."""
        for model_name in list(cls._loaded_models.keys()):
            cls.unload_model(model_name)
    
    @classmethod
    def get_loaded_models(cls) -> list:
        """Get list of currently loaded models.
        
        Returns:
            List of loaded model names
        """
        return list(cls._loaded_models.keys())
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[Dict]:
        """Get information about a loaded model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary or None if not loaded
        """
        if model_name in cls._loaded_models:
            return cls._loaded_models[model_name].get_model_info()
        return None