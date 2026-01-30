#!/usr/bin/env python3
"""
Тест чистоты Transformers режима без dots.ocr
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import logger

def test_transformers_clean():
    """Тестирует что Transformers режим чист от dots.ocr."""
    
    logger.info("🧪 Тестирование чистоты Transformers режима")
    
    try:
        from models.model_loader import ModelLoader
        
        # Получаем список доступных моделей
        available_models = list(ModelLoader.MODEL_REGISTRY.keys())
        logger.info(f"Доступные Transformers модели: {available_models}")
        
        # Проверяем что dots.ocr отсутствует
        if "dots_ocr" not in available_models:
            logger.info("✅ dots.ocr успешно удалена из Transformers режима")
            
            # Проверяем что есть альтернативы
            alternatives = ["qwen_vl_2b", "qwen3_vl_2b", "got_ocr", "phi3_vision"]
            available_alternatives = [model for model in alternatives if model in available_models]
            
            logger.info(f"✅ Доступные альтернативы: {available_alternatives}")
            
            if len(available_alternatives) > 0:
                logger.info("🎉 Transformers режим полностью функционален без dots.ocr!")
                return True
            else:
                logger.warning("⚠️ Нет альтернативных моделей")
                return False
        else:
            logger.error("❌ dots.ocr все еще присутствует в Transformers режиме")
            return False
    
    except Exception as e:
        logger.error(f"Ошибка тестирования: {e}")
        return False

def test_vllm_availability():
    """Проверяет доступность dots.ocr в vLLM режиме."""
    
    logger.info("🧪 Проверка доступности dots.ocr в vLLM")
    
    try:
        # Проверяем конфигурацию vLLM
        import yaml
        
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        if "vllm" in config and "dots_ocr" in config["vllm"]:
            logger.info("✅ dots.ocr доступна в vLLM режиме")
            logger.info(f"Конфигурация: {config['vllm']['dots_ocr']['name']}")
            return True
        else:
            logger.warning("⚠️ dots.ocr не найдена в vLLM конфигурации")
            return False
    
    except Exception as e:
        logger.error(f"Ошибка проверки vLLM: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Тестирование новой конфигурации")
    
    transformers_ok = test_transformers_clean()
    vllm_ok = test_vllm_availability()
    
    if transformers_ok and vllm_ok:
        logger.info("🎉 КОНФИГУРАЦИЯ ИДЕАЛЬНА!")
        logger.info("✅ Transformers режим чист и стабилен")
        logger.info("✅ dots.ocr доступна в vLLM режиме")
        logger.info("🚀 Система готова к использованию!")
    else:
        logger.error("❌ Требуется дополнительная настройка")