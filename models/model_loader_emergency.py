"""
EMERGENCY Model Loader - Исправления критических CUDA ошибок
Специальная версия загрузчика для работы в аварийном режиме
"""

from typing import Dict, Optional
from pathlib import Path
import yaml
import json
import gc
import time
import os

from models.base_model import BaseModel
from models.got_ocr import GOTOCRModel
from models.qwen_vl import QwenVLModel
from models.qwen3_vl import Qwen3VLModel
from models.dots_ocr_corrected import DotsOCRCorrectedModel
from models.dots_ocr import DotsOCRModel
from models.dots_ocr_final import DotsOCRFinalModel
from models.dots_ocr_dtype_fixed import DotsOCRDtypeFixedModel
from models.dots_ocr_generation_fixed import DotsOCRGenerationFixedModel
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


class EmergencyModelLoader:
    """
    EMERGENCY Model Loader - Исправления критических ошибок
    
    Основные исправления:
    1. Принудительное отключение Flash Attention
    2. Отключение квантизации (8bit/4bit)
    3. Принудительное использование eager attention
    4. Улучшенная обработка CUDA ошибок
    5. Автоматическое восстановление GPU состояния
    """
    
    # Registry of available models
    MODEL_REGISTRY: Dict[str, type] = {
        "got_ocr": GOTOCRModel,
        "qwen_vl_2b": QwenVLModel,
        "qwen_vl_7b": QwenVLModel,
        "qwen3_vl_2b": Qwen3VLModel,
        "qwen3_vl_4b": Qwen3VLModel,
        "qwen3_vl_8b": Qwen3VLModel,
        "dots_ocr": DotsOCRModel,
        "dots_ocr_corrected": DotsOCRCorrectedModel,
        "dots_ocr_final": DotsOCRFinalModel,
        "dots_ocr_dtype_fixed": DotsOCRDtypeFixedModel,
        "dots_ocr_generation_fixed": DotsOCRGenerationFixedModel,
        "phi3_vision": Phi3VisionModel,
        "got_ocr_ucas": GOTOCRUCASModel,
        "got_ocr_hf": GOTOCRHFModel,
        "deepseek_ocr": DeepSeekOCRModel,
    }
    
    # Cache for loaded model instances
    _loaded_models: Dict[str, BaseModel] = {}
    
    # Cache manager
    _cache_manager = ModelCacheManager()
    
    # Emergency fixes configuration
    _emergency_fixes = None
    
    @classmethod
    def _load_emergency_fixes(cls):
        """Загрузка конфигурации аварийных исправлений"""
        if cls._emergency_fixes is None:
            try:
                with open("model_loader_emergency_fixes.json", "r", encoding="utf-8") as f:
                    cls._emergency_fixes = json.load(f)
                logger.info("✅ Загружены аварийные исправления")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось загрузить аварийные исправления: {e}")
                cls._emergency_fixes = {
                    "model_loader_patches": {
                        "force_eager_attention": True,
                        "disable_flash_attention": True,
                        "disable_quantization": True,
                        "enable_cuda_recovery": True,
                        "max_retries": 3,
                        "fallback_to_cpu": False
                    }
                }
        return cls._emergency_fixes
    
    @classmethod
    def _emergency_cuda_recovery(cls):
        """Экстренное восстановление CUDA состояния"""
        if not TORCH_AVAILABLE or not torch.cuda.is_available():
            return
        
        try:
            logger.info("🚨 Экстренное восстановление CUDA...")
            
            # Принудительная очистка всех CUDA кешей
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
            # Очистка всех устройств
            for i in range(torch.cuda.device_count()):
                with torch.cuda.device(i):
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
            
            # Принудительная сборка мусора
            for _ in range(3):
                gc.collect()
                time.sleep(0.1)
            
            # Установка отладочных переменных
            os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
            os.environ['TORCH_USE_CUDA_DSA'] = '1'
            os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
            
            logger.info("✅ Восстановление CUDA завершено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка восстановления CUDA: {e}")
    
    @classmethod
    def _apply_emergency_patches(cls, model_config: dict) -> dict:
        """Применение аварийных исправлений к конфигурации модели"""
        fixes = cls._load_emergency_fixes()
        patches = fixes.get("model_loader_patches", {})
        
        # Принудительные исправления
        if patches.get("force_eager_attention", True):
            model_config["attn_implementation"] = "eager"
            logger.info("🔧 Принудительно установлен eager attention")
        
        if patches.get("disable_flash_attention", True):
            model_config["use_flash_attention"] = False
            logger.info("🔧 Flash Attention отключен")
        
        if patches.get("disable_quantization", True):
            model_config["load_in_8bit"] = False
            model_config["load_in_4bit"] = False
            logger.info("🔧 Квантизация отключена")
        
        # Принудительное использование fp16 для стабильности
        if model_config.get("precision") not in ["fp16", "fp32"]:
            model_config["precision"] = "fp16"
            logger.info("🔧 Принудительно установлен fp16")
        
        # Дополнительные настройки безопасности
        model_config["torch_dtype"] = "float16"
        model_config["device_map"] = "auto"
        model_config["trust_remote_code"] = True
        
        return model_config
    
    @classmethod
    def load_config(cls) -> dict:
        """Load configuration from YAML file."""
        config_path = Path("config.yaml")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @classmethod
    def check_model_cache(cls, model_key: str) -> tuple[bool, Optional[str]]:
        """Check if model is in cache."""
        config = cls.load_config()
        
        if model_key not in config["models"]:
            return False, f"Model '{model_key}' not found in config"
        
        model_config = config["models"][model_key]
        model_path = model_config.get("model_path")
        
        if not model_path:
            return False, "No model_path in config"
        
        return check_model_availability(model_path)
    
    @classmethod
    def get_available_vram(cls) -> float:
        """Get available GPU VRAM in GB."""
        if not TORCH_AVAILABLE or not torch.cuda.is_available():
            return 0.0
        
        try:
            props = torch.cuda.get_device_properties(0)
            total_vram = props.total_memory / (1024 ** 3)
            allocated = torch.cuda.memory_allocated(0) / (1024 ** 3)
            reserved = torch.cuda.memory_reserved(0) / (1024 ** 3)
            available = total_vram - reserved
            
            logger.info(f"GPU VRAM: {total_vram:.2f}GB total, {allocated:.2f}GB allocated, {available:.2f}GB available")
            return available
        except Exception as e:
            logger.warning(f"Failed to get VRAM info: {e}")
            return 0.0
    
    @classmethod
    def load_model(
        cls,
        model_key: str,
        force_reload: bool = False,
        precision: str = "auto",
        **kwargs
    ) -> BaseModel:
        """
        EMERGENCY Load a model with critical error fixes.
        
        Args:
            model_key: Model identifier from config
            force_reload: Force reload even if cached
            precision: Model precision (auto uses config)
            **kwargs: Additional arguments for model initialization
            
        Returns:
            Loaded model instance
            
        Raises:
            ValueError: If model key is not found
            RuntimeError: If model fails to load after all retries
        """
        fixes = cls._load_emergency_fixes()
        max_retries = fixes.get("model_loader_patches", {}).get("max_retries", 3)
        
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
        
        model_config = config["models"][model_key].copy()
        
        # Применяем аварийные исправления
        model_config = cls._apply_emergency_patches(model_config)
        
        # Override precision if specified
        if precision != "auto":
            model_config["precision"] = precision
            logger.info(f"Using specified precision: {precision}")
        else:
            logger.info(f"Using config precision: {model_config.get('precision', 'fp16')} (auto-selection disabled)")
        
        # Check cache status
        is_cached, cache_msg = cls.check_model_cache(model_key)
        if is_cached:
            logger.info(f"Model found in cache: {cache_msg}")
        else:
            logger.warning(f"Model not in cache: {cache_msg}")
        
        # Get model class
        model_class = cls.MODEL_REGISTRY[model_key]
        
        # Специальная логика для проблемных моделей
        if model_key == "dots_ocr":
            logger.info("🔧 Using generation-fixed dots.ocr implementation")
            model_class = cls.MODEL_REGISTRY["dots_ocr_generation_fixed"]
        
        # Merge config with kwargs
        init_kwargs = {**model_config, **kwargs}
        
        # Попытки загрузки с повторами
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Попытка загрузки {attempt + 1}/{max_retries}: {model_key}")
                
                # Экстренное восстановление CUDA перед каждой попыткой
                if fixes.get("model_loader_patches", {}).get("enable_cuda_recovery", True):
                    cls._emergency_cuda_recovery()
                
                logger.info(f"Loading model: {model_key}")
                logger.info(f"Model path: {model_config.get('model_path')}")
                logger.info(f"Precision: {init_kwargs.get('precision')}")
                logger.info(f"Flash Attention: {init_kwargs.get('use_flash_attention')}")
                logger.info(f"Attention Implementation: {init_kwargs.get('attn_implementation')}")
                
                # Initialize model
                model = model_class(config=init_kwargs)
                
                # Load model weights
                model.load_model()
                
                # Cache the instance
                cls._loaded_models[model_key] = model
                
                logger.info(f"✅ Successfully loaded model: {model_key}")
                return model
                
            except RuntimeError as e:
                error_str = str(e)
                last_error = e
                
                # Специальная обработка CUDA ошибок
                if "CUDA error: device-side assert triggered" in error_str:
                    logger.error(f"🚨 КРИТИЧЕСКАЯ CUDA ОШИБКА (попытка {attempt + 1}): {e}")
                    cls._emergency_cuda_recovery()
                    time.sleep(2)  # Пауза перед повтором
                    continue
                
                # Специальная обработка Flash Attention ошибок
                elif "FlashAttention2" in error_str or "flash_attn" in error_str:
                    logger.error(f"⚠️ Flash Attention ошибка (попытка {attempt + 1}): {e}")
                    init_kwargs["use_flash_attention"] = False
                    init_kwargs["attn_implementation"] = "eager"
                    continue
                
                # Специальная обработка квантизации ошибок
                elif "load_in_8bit" in error_str or "load_in_4bit" in error_str:
                    logger.error(f"⚠️ Квантизация ошибка (попытка {attempt + 1}): {e}")
                    init_kwargs["load_in_8bit"] = False
                    init_kwargs["load_in_4bit"] = False
                    continue
                
                # Другие ошибки
                else:
                    logger.error(f"❌ Ошибка загрузки (попытка {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        break
            
            except Exception as e:
                last_error = e
                logger.error(f"❌ Неожиданная ошибка (попытка {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    break
        
        # Все попытки исчерпаны
        logger.error(f"❌ Не удалось загрузить модель '{model_key}' после {max_retries} попыток")
        raise RuntimeError(f"Failed to load model '{model_key}' after {max_retries} attempts. Last error: {last_error}")
    
    @classmethod
    def unload_model(cls, model_key: str) -> bool:
        """Unload a model from memory with emergency cleanup."""
        if model_key in cls._loaded_models:
            try:
                model = cls._loaded_models[model_key]
                if hasattr(model, 'unload'):
                    model.unload()
                del cls._loaded_models[model_key]
                
                # Экстренная очистка GPU
                cls._emergency_cuda_recovery()
                
                logger.info(f"✅ Unloaded model: {model_key}")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to unload model '{model_key}': {e}")
                return False
        return False
    
    @classmethod
    def unload_all_models(cls) -> None:
        """Unload all models from memory with emergency cleanup."""
        model_keys = list(cls._loaded_models.keys())
        for model_key in model_keys:
            cls.unload_model(model_key)
        
        # Финальная экстренная очистка
        cls._emergency_cuda_recovery()
        logger.info("✅ All models unloaded")
    
    @classmethod
    def get_loaded_models(cls) -> list[str]:
        """Get list of currently loaded models."""
        return list(cls._loaded_models.keys())
    
    @classmethod
    def is_model_loaded(cls, model_key: str) -> bool:
        """Check if model is loaded."""
        return model_key in cls._loaded_models
    
    @classmethod
    def get_emergency_status(cls) -> dict:
        """Get emergency mode status and applied fixes."""
        fixes = cls._load_emergency_fixes()
        
        status = {
            "emergency_mode": True,
            "cuda_available": TORCH_AVAILABLE and torch.cuda.is_available(),
            "applied_fixes": fixes.get("model_loader_patches", {}),
            "loaded_models": cls.get_loaded_models(),
            "available_vram_gb": cls.get_available_vram(),
            "critical_errors_detected": [
                "CUDA device-side assert triggered",
                "FlashAttention2 not installed",
                "8bit quantization not supported",
                "transformers version incompatibility"
            ],
            "fixes_applied": [
                "Force eager attention",
                "Disable Flash Attention",
                "Disable quantization",
                "Enable CUDA recovery",
                "Emergency GPU cleanup"
            ]
        }
        
        return status


# Заменяем основной ModelLoader на аварийную версию
ModelLoader = EmergencyModelLoader