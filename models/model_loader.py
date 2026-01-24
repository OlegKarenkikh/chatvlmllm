"""Model loader with factory pattern and cache support."""

from typing import Dict, Optional
from pathlib import Path
import yaml

from models.base_model import BaseModel
from models.got_ocr import GOTOCRModel
from models.qwen_vl import QwenVLModel
from models.qwen3_vl import Qwen3VLModel
from models.dots_ocr import DotsOCRModel
from models.phi3_vision import Phi3VisionModel
from models.got_ocr_variants import GOTOCRUCASModel, GOTOCRHFModel
from models.deepseek_ocr import DeepSeekOCRModel
from utils.model_cache import ModelCacheManager, check_model_availability
from utils.logger import logger

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available, GPU features disabled")


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
        "phi3_vision": Phi3VisionModel,
        "got_ocr_ucas": GOTOCRUCASModel,
        "got_ocr_hf": GOTOCRHFModel,
        "deepseek_ocr": DeepSeekOCRModel,
    }
    
    # Cache for loaded model instances
    _loaded_models: Dict[str, BaseModel] = {}
    
    # Cache manager
    _cache_manager = ModelCacheManager()
    
    @classmethod
    def load_config(cls) -> dict:
        """Load configuration from YAML file."""
        config_path = Path("config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
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
    def get_available_vram(cls) -> float:
        """
        Get available GPU VRAM in GB.
        
        Returns:
            Available VRAM in GB, or 0 if no GPU available
        """
        if not TORCH_AVAILABLE or not torch.cuda.is_available():
            return 0.0
        
        try:
            props = torch.cuda.get_device_properties(0)
            total_vram = props.total_memory / (1024 ** 3)  # Convert to GB
            allocated = torch.cuda.memory_allocated(0) / (1024 ** 3)
            reserved = torch.cuda.memory_reserved(0) / (1024 ** 3)
            available = total_vram - reserved
            
            logger.info(f"GPU VRAM: {total_vram:.2f}GB total, {allocated:.2f}GB allocated, {available:.2f}GB available")
            return available
        except Exception as e:
            logger.warning(f"Failed to get VRAM info: {e}")
            return 0.0
    
    @classmethod
    def auto_select_precision(cls, model_key: str, config: dict) -> str:
        """
        Automatically select precision based on available VRAM.
        
        Args:
            model_key: Model identifier
            config: Configuration dictionary
            
        Returns:
            Selected precision (fp16, int8, or int4)
        """
        # Check if auto precision is enabled
        performance_config = config.get("performance", {})
        if not performance_config.get("auto_precision", False):
            # Return configured precision
            model_config = config["models"][model_key]
            return model_config.get("precision", "fp16")
        
        # Get available VRAM
        available_vram = cls.get_available_vram()
        
        if available_vram == 0.0:
            logger.info("No GPU available, using fp32 for CPU")
            return "fp32"
        
        # Get auto precision rules from config
        gpu_config = config.get("gpu_requirements", {})
        optimization = gpu_config.get("optimization", {})
        rules = optimization.get("auto_precision_rules", {
            "< 6GB": "int4",
            "< 8GB": "int8",
            "< 12GB": "fp16",
            ">= 12GB": "fp16"
        })
        
        # Apply rules
        if available_vram < 6:
            precision = rules.get("< 6GB", "int4")
            logger.info(f"Auto-selected precision: {precision} (VRAM < 6GB)")
        elif available_vram < 8:
            precision = rules.get("< 8GB", "int8")
            logger.info(f"Auto-selected precision: {precision} (VRAM 6-8GB)")
        elif available_vram < 12:
            precision = rules.get("< 12GB", "fp16")
            logger.info(f"Auto-selected precision: {precision} (VRAM 8-12GB)")
        else:
            precision = rules.get(">= 12GB", "fp16")
            logger.info(f"Auto-selected precision: {precision} (VRAM >= 12GB)")
        
        return precision
    
    @classmethod
    def load_model(
        cls,
        model_key: str,
        force_reload: bool = False,
        precision: str = "auto",
        **kwargs
    ) -> BaseModel:
        """
        Load a model by key.
        
        Args:
            model_key: Model identifier from config
            force_reload: Force reload even if cached
            precision: Model precision (auto, fp32, fp16, int8, int4)
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
        
        # Auto-select precision if requested
        if precision == "auto":
            precision = cls.auto_select_precision(model_key, config)
            # Override config precision with auto-selected
            model_config["precision"] = precision
        elif precision != "auto":
            # Override config precision with specified value
            model_config["precision"] = precision
            logger.info(f"Using specified precision: {precision}")
        
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
            logger.info(f"Precision: {init_kwargs.get('precision')}")
            logger.info(f"Flash Attention: {init_kwargs.get('use_flash_attention')}")
            
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
                
                # Clear GPU cache if available
                if TORCH_AVAILABLE and torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.info(f"Cleared GPU cache after unloading {model_key}")
                
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
    
    @classmethod
    def get_gpu_status(cls) -> dict:
        """
        Get current GPU status and recommendations.
        
        Returns:
            Dictionary with GPU status information
        """
        status = {
            "cuda_available": False,
            "gpu_count": 0,
            "gpu_name": None,
            "total_vram_gb": 0.0,
            "available_vram_gb": 0.0,
            "allocated_vram_gb": 0.0,
            "recommended_precision": "fp32",
            "flash_attention_available": False
        }
        
        if not TORCH_AVAILABLE:
            return status
        
        status["cuda_available"] = torch.cuda.is_available()
        
        if not status["cuda_available"]:
            return status
        
        try:
            status["gpu_count"] = torch.cuda.device_count()
            status["gpu_name"] = torch.cuda.get_device_name(0)
            
            props = torch.cuda.get_device_properties(0)
            status["total_vram_gb"] = props.total_memory / (1024 ** 3)
            status["allocated_vram_gb"] = torch.cuda.memory_allocated(0) / (1024 ** 3)
            status["available_vram_gb"] = cls.get_available_vram()
            
            # Determine recommended precision
            vram = status["available_vram_gb"]
            if vram < 6:
                status["recommended_precision"] = "int4"
            elif vram < 8:
                status["recommended_precision"] = "int8"
            else:
                status["recommended_precision"] = "fp16"
            
            # Check Flash Attention
            try:
                import flash_attn
                status["flash_attention_available"] = True
            except ImportError:
                status["flash_attention_available"] = False
                
        except Exception as e:
            logger.error(f"Error getting GPU status: {e}")
        
        return status
