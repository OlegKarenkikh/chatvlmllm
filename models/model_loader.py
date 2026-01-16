"""Model loader with factory pattern and cache support."""

from typing import Dict, Optional
from pathlib import Path
import yaml

from models.base_model import BaseModel
from models.got_ocr import GOTOCRModel
from models.qwen_vl import QwenVLModel
from models.qwen3_vl import Qwen3VLModel
from models.dots_ocr import DotsOCRModel
from utils.model_cache import ModelCacheManager, check_model_availability
from utils.logger import logger


class ModelLoader:
    """Factory for loading and managing models."""
    
    # Registry of available models
    MODEL_REGISTRY: Dict[str, type] = {
        "got_ocr": GOTOCRModel,
        "qwen_vl_2b": QwenVLModel,
        "qwen_vl_7b": QwenVLModel,
        "qwen3_vl_2b": Qwen3VLModel,
        "qwen3_vl_4b": Qwen3VLModel,
        "qwen3_vl_8b": Qwen3VLModel,
        "dots_ocr": DotsOCRModel,
    }
    
    # Cache for loaded model instances
    _loaded_models: Dict[str, BaseModel] = {}
    
    # Cache manager
    _cache_manager = ModelCacheManager()
    
    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> dict:
        """Load configuration from YAML file."""
        resolved_path = Path(config_path) if config_path else Path("config.yaml")
        with open(resolved_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @classmethod
    def get_available_models(cls, config_path: Optional[str] = None) -> Dict[str, dict]:
        """
        Return available models from configuration.
        
        Args:
            config_path: Optional path to config.yaml
        
        Returns:
            Mapping of model keys to configuration
        """
        config = cls.load_config(config_path)
        return config.get("models", {})
    
    @classmethod
    def check_model_cache(cls, model_key: str) -> tuple[bool, Optional[str]]:
        """
        Check if model is in cache.
        
        Args:
            model_key: Model identifier from config
            
        Returns:
            Tuple of (is_cached, message)
        """
        config = cls.load_config()
        
        if model_key not in config["models"]:
            return False, f"Model '{model_key}' not found in config"
        
        model_config = config["models"][model_key]
        model_path = model_config.get("model_path")
        
        if not model_path:
            return False, "No model_path in config"
        
        return check_model_availability(model_path)
    
    @classmethod
    def get_cache_info(cls) -> dict:
        """
        Get information about cached models.
        
        Returns:
            Dictionary with cache information
        """
        return cls._cache_manager.get_cache_info()
    
    @classmethod
    def load_model(
        cls,
        model_key: str,
        force_reload: bool = False,
        **kwargs
    ) -> BaseModel:
        """
        Load a model by key.
        
        Args:
            model_key: Model identifier from config
            force_reload: Force reload even if cached
            **kwargs: Additional arguments for model initialization
            
        Returns:
            Loaded model instance
            
        Raises:
            ValueError: If model key is not found
            RuntimeError: If model fails to load
        """
        # Check if already loaded
        if not force_reload and model_key in cls._loaded_models:
            logger.info(f"Using cached model instance: {model_key}")
            return cls._loaded_models[model_key]
        
        # Check if model class exists
        if model_key not in cls.MODEL_REGISTRY:
            available = ", ".join(cls.MODEL_REGISTRY.keys())
            raise ValueError(
                f"Model '{model_key}' not found. Available: {available}"
            )
        
        # Load configuration
        config = cls.load_config()
        
        if model_key not in config["models"]:
            raise ValueError(f"Model '{model_key}' not found in config.yaml")
        
        model_config = config["models"][model_key]
        
        # Check cache status
        is_cached, cache_msg = cls.check_model_cache(model_key)
        if is_cached:
            logger.info(f"Model found in cache: {cache_msg}")
        else:
            logger.warning(f"Model not in cache: {cache_msg}")
            logger.info(f"Model will be downloaded on first load: {model_config.get('model_path')}")
        
        # Get model class
        model_class = cls.MODEL_REGISTRY[model_key]
        
        # Merge config with kwargs
        init_kwargs = {**model_config, **kwargs}
        
        try:
            logger.info(f"Loading model: {model_key}")
            logger.info(f"Model path: {model_config.get('model_path')}")
            
            # Initialize model
            model = model_class(config=init_kwargs)
            
            # Load model weights
            model.load_model()
            
            # Cache the instance
            cls._loaded_models[model_key] = model
            
            logger.info(f"Successfully loaded model: {model_key}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model '{model_key}': {e}")
            raise RuntimeError(f"Failed to load model '{model_key}': {e}")
    
    @classmethod
    def unload_model(cls, model_key: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_key: Model identifier
            
        Returns:
            True if unloaded successfully
        """
        if model_key in cls._loaded_models:
            try:
                model = cls._loaded_models[model_key]
                if hasattr(model, 'unload'):
                    model.unload()
                del cls._loaded_models[model_key]
                logger.info(f"Unloaded model: {model_key}")
                return True
            except Exception as e:
                logger.error(f"Failed to unload model '{model_key}': {e}")
                return False
        return False
    
    @classmethod
    def unload_all_models(cls) -> None:
        """Unload all models from memory."""
        model_keys = list(cls._loaded_models.keys())
        for model_key in model_keys:
            cls.unload_model(model_key)
        logger.info("All models unloaded")
    
    @classmethod
    def get_loaded_models(cls) -> list[str]:
        """
        Get list of currently loaded models.
        
        Returns:
            List of model keys
        """
        return list(cls._loaded_models.keys())
    
    @classmethod
    def is_model_loaded(cls, model_key: str) -> bool:
        """
        Check if model is loaded.
        
        Args:
            model_key: Model identifier
            
        Returns:
            True if model is loaded
        """
        return model_key in cls._loaded_models
