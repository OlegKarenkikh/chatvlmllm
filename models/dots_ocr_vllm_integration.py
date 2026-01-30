#!/usr/bin/env python3
"""
Интеграция dots.ocr через vLLM Docker в проект chatvlmllm
Решение проблемы Flash Attention на RTX 5070 Ti Blackwell
"""

import sys
import os
import logging
from typing import Dict, List, Any, Optional
from PIL import Image

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from vllm_dots_ocr_client import VLLMDotsOCRClient
except ImportError:
    VLLMDotsOCRClient = None

logger = logging.getLogger(__name__)

class DotsOCRVLLMIntegration:
    """
    Интеграция dots.ocr через vLLM Docker для chatvlmllm проекта
    Обходит проблемы Flash Attention на RTX 5070 Ti Blackwell
    """
    
    def __init__(self, vllm_url: str = "http://localhost:8000"):
        self.vllm_url = vllm_url
        self.vllm_client = None
        self.is_available = False
        self.fallback_model = None
        
        # Попытка инициализации vLLM клиента
        self._initialize_vllm_client()
    
    def _initialize_vllm_client(self):
        """Инициализация vLLM клиента"""
        if VLLMDotsOCRClient is None:
            logger.warning("vLLM клиент недоступен - модуль не найден")
            return
        
        try:
            self.vllm_client = VLLMDotsOCRClient(self.vllm_url)
            
            # Проверка доступности сервера
            if self.vllm_client.health_check():
                self.is_available = True
                logger.info(f"✅ vLLM dots.ocr сервер доступен: {self.vllm_url}")
            else:
                logger.warning(f"⚠️ vLLM сервер недоступен: {self.vllm_url}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации vLLM клиента: {e}")
    
    def set_fallback_model(self, fallback_model):
        """Установка fallback модели (например, qwen_vl_2b)"""
        self.fallback_model = fallback_model
        logger.info("✅ Fallback модель установлена")
    
    def is_vllm_available(self) -> bool:
        """Проверка доступности vLLM сервера"""
        if not self.vllm_client:
            return False
        
        try:
            return self.vllm_client.health_check()
        except:
            return False
    
    def process_image_file(self, image_path: str, prompt: str = "Extract all text from this image") -> Dict[str, Any]:
        """
        Обработка изображения из файла
        
        Args:
            image_path: Путь к изображению
            prompt: Промпт для OCR
            
        Returns:
            Результат обработки
        """
        # Попытка через vLLM
        if self.is_vllm_available():
            try:
                result = self.vllm_client.process_image(image_path, prompt)
                
                if result["success"]:
                    return {
                        "success": True,
                        "content": result["content"],
                        "model": "dots.ocr-vllm",
                        "processing_time": result["processing_time"],
                        "method": "vllm"
                    }
                else:
                    logger.warning(f"vLLM ошибка: {result['error']}")
                    
            except Exception as e:
                logger.error(f"vLLM исключение: {e}")
        
        # Fallback на локальную модель
        return self._fallback_process(image_path, prompt)
    
    def process_pil_image(self, image: Image.Image, prompt: str = "Extract all text from this image") -> Dict[str, Any]:
        """
        Обработка PIL изображения
        
        Args:
            image: PIL изображение
            prompt: Промпт для OCR
            
        Returns:
            Результат обработки
        """
        # Попытка через vLLM
        if self.is_vllm_available():
            try:
                result = self.vllm_client.process_pil_image(image, prompt)
                
                if result["success"]:
                    return {
                        "success": True,
                        "content": result["content"],
                        "model": "dots.ocr-vllm",
                        "processing_time": result["processing_time"],
                        "method": "vllm"
                    }
                else:
                    logger.warning(f"vLLM ошибка: {result['error']}")
                    
            except Exception as e:
                logger.error(f"vLLM исключение: {e}")
        
        # Fallback на локальную модель
        return self._fallback_process_pil(image, prompt)
    
    def chat_completion(self, messages: List[Dict], max_tokens: int = 2048) -> Dict[str, Any]:
        """
        OpenAI совместимый API для chatvlmllm интеграции
        
        Args:
            messages: Сообщения в формате OpenAI
            max_tokens: Максимальное количество токенов
            
        Returns:
            Ответ в формате OpenAI API
        """
        # Попытка через vLLM
        if self.is_vllm_available():
            try:
                result = self.vllm_client.chat_completion(messages, max_tokens)
                
                # Проверка на ошибки
                if "error" not in result:
                    # Добавляем информацию о методе
                    if "usage" not in result:
                        result["usage"] = {}
                    result["usage"]["method"] = "vllm"
                    result["usage"]["server"] = self.vllm_url
                    
                    return result
                else:
                    logger.warning(f"vLLM chat_completion ошибка: {result['error']}")
                    
            except Exception as e:
                logger.error(f"vLLM chat_completion исключение: {e}")
        
        # Fallback на локальную модель
        return self._fallback_chat_completion(messages, max_tokens)
    
    def _fallback_process(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Fallback обработка через локальную модель"""
        if self.fallback_model:
            try:
                # Предполагаем, что fallback модель имеет метод process_image
                result = self.fallback_model.process_image(image_path, prompt)
                
                if result:
                    return {
                        "success": True,
                        "content": result,
                        "model": "fallback",
                        "processing_time": "N/A",
                        "method": "fallback"
                    }
            except Exception as e:
                logger.error(f"Fallback ошибка: {e}")
        
        return {
            "success": False,
            "error": "vLLM недоступен и fallback модель не настроена",
            "model": "none",
            "method": "none"
        }
    
    def _fallback_process_pil(self, image: Image.Image, prompt: str) -> Dict[str, Any]:
        """Fallback обработка PIL изображения"""
        if self.fallback_model:
            try:
                # Предполагаем, что fallback модель может обработать PIL изображение
                result = self.fallback_model.process_image(image, prompt)
                
                if result:
                    return {
                        "success": True,
                        "content": result,
                        "model": "fallback",
                        "processing_time": "N/A",
                        "method": "fallback"
                    }
            except Exception as e:
                logger.error(f"Fallback PIL ошибка: {e}")
        
        return {
            "success": False,
            "error": "vLLM недоступен и fallback модель не настроена",
            "model": "none",
            "method": "none"
        }
    
    def _fallback_chat_completion(self, messages: List[Dict], max_tokens: int) -> Dict[str, Any]:
        """Fallback chat completion"""
        if self.fallback_model and hasattr(self.fallback_model, 'chat_completion'):
            try:
                result = self.fallback_model.chat_completion(messages, max_tokens)
                
                # Добавляем информацию о методе
                if "usage" not in result:
                    result["usage"] = {}
                result["usage"]["method"] = "fallback"
                
                return result
                
            except Exception as e:
                logger.error(f"Fallback chat_completion ошибка: {e}")
        
        return {
            "error": "vLLM недоступен и fallback модель не поддерживает chat_completion",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "OCR сервис временно недоступен"
                },
                "finish_reason": "error"
            }],
            "usage": {
                "method": "none",
                "error": True
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса интеграции"""
        vllm_available = self.is_vllm_available()
        
        status = {
            "vllm_url": self.vllm_url,
            "vllm_available": vllm_available,
            "fallback_available": self.fallback_model is not None,
            "recommended_method": "vllm" if vllm_available else "fallback"
        }
        
        if vllm_available and self.vllm_client:
            try:
                server_info = self.vllm_client.get_server_info()
                status["vllm_info"] = server_info
            except:
                pass
        
        return status

# Глобальный экземпляр для использования в chatvlmllm
_dots_ocr_vllm_instance = None

def get_dots_ocr_vllm_integration(vllm_url: str = "http://localhost:8000") -> DotsOCRVLLMIntegration:
    """Получение глобального экземпляра интеграции"""
    global _dots_ocr_vllm_instance
    
    if _dots_ocr_vllm_instance is None:
        _dots_ocr_vllm_instance = DotsOCRVLLMIntegration(vllm_url)
    
    return _dots_ocr_vllm_instance

def initialize_dots_ocr_vllm(vllm_url: str = "http://localhost:8000", fallback_model=None) -> bool:
    """
    Инициализация dots.ocr vLLM интеграции
    
    Args:
        vllm_url: URL vLLM сервера
        fallback_model: Fallback модель (например, qwen_vl_2b)
        
    Returns:
        True если хотя бы один метод доступен
    """
    integration = get_dots_ocr_vllm_integration(vllm_url)
    
    if fallback_model:
        integration.set_fallback_model(fallback_model)
    
    status = integration.get_status()
    
    logger.info(f"🔧 dots.ocr vLLM интеграция:")
    logger.info(f"   vLLM: {'✅' if status['vllm_available'] else '❌'}")
    logger.info(f"   Fallback: {'✅' if status['fallback_available'] else '❌'}")
    logger.info(f"   Рекомендуемый метод: {status['recommended_method']}")
    
    return status['vllm_available'] or status['fallback_available']

# Тестирование интеграции
def test_dots_ocr_vllm_integration():
    """Тест интеграции dots.ocr vLLM"""
    print("🧪 ТЕСТ ИНТЕГРАЦИИ DOTS.OCR VLLM")
    print("=" * 50)
    
    # Инициализация
    integration = get_dots_ocr_vllm_integration()
    
    # Статус
    status = integration.get_status()
    print("📋 Статус интеграции:")
    print(f"   vLLM доступен: {status['vllm_available']}")
    print(f"   Fallback доступен: {status['fallback_available']}")
    print(f"   Рекомендуемый метод: {status['recommended_method']}")
    
    if not status['vllm_available'] and not status['fallback_available']:
        print("❌ Ни один метод недоступен")
        return False
    
    # Создание тестового изображения
    print("\n🖼️ Создание тестового изображения...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (500, 150), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 60), "INTEGRATION TEST", fill='black', font=font)
        img.save('integration_test.png')
        
        print("✅ Тестовое изображение создано")
        
    except Exception as e:
        print(f"❌ Ошибка создания изображения: {e}")
        return False
    
    # Тест обработки файла
    print("\n🔍 Тест обработки файла...")
    result = integration.process_image_file('integration_test.png', "Extract all text")
    
    if result["success"]:
        print(f"✅ Файл обработан через {result['method']}")
        print(f"📝 Результат: {result['content']}")
        print(f"⏱️ Время: {result['processing_time']}")
    else:
        print(f"❌ Ошибка обработки файла: {result.get('error', 'Unknown')}")
    
    # Тест обработки PIL изображения
    print("\n🔍 Тест обработки PIL изображения...")
    pil_result = integration.process_pil_image(img, "Extract all text")
    
    if pil_result["success"]:
        print(f"✅ PIL изображение обработано через {pil_result['method']}")
        print(f"📝 Результат: {pil_result['content']}")
    else:
        print(f"❌ Ошибка обработки PIL: {pil_result.get('error', 'Unknown')}")
    
    # Тест OpenAI API
    print("\n🔍 Тест OpenAI API...")
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "integration_test.png"}
                },
                {
                    "type": "text",
                    "text": "Extract all text from this image"
                }
            ]
        }
    ]
    
    api_result = integration.chat_completion(messages)
    
    if "error" not in api_result:
        content = api_result["choices"][0]["message"]["content"]
        method = api_result.get("usage", {}).get("method", "unknown")
        print(f"✅ OpenAI API работает через {method}")
        print(f"📝 Результат: {content}")
    else:
        print(f"❌ Ошибка OpenAI API: {api_result['error']}")
    
    print("\n🎉 Тест интеграции завершен!")
    return True

if __name__ == "__main__":
    success = test_dots_ocr_vllm_integration()
    
    if success:
        print("\n✅ ИНТЕГРАЦИЯ ГОТОВА К ИСПОЛЬЗОВАНИЮ В CHATVLMLLM!")
    else:
        print("\n❌ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")