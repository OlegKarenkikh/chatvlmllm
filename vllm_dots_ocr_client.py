#!/usr/bin/env python3
"""
Клиент для dots.ocr через vLLM Docker сервер
Интеграция с chatvlmllm проектом
"""

import requests
import base64
import json
import time
from typing import Dict, List, Any, Optional
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class VLLMDotsOCRClient:
    """Клиент для dots.ocr через vLLM Docker контейнер"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def health_check(self) -> bool:
        """Проверка доступности vLLM сервера"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def get_models(self) -> Dict[str, Any]:
        """Получение списка доступных моделей"""
        try:
            response = self.session.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Кодирование изображения в base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Cannot encode image {image_path}: {e}")
    
    def encode_pil_image_to_base64(self, image: Image.Image) -> str:
        """Кодирование PIL изображения в base64"""
        try:
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Cannot encode PIL image: {e}")
    
    def process_image(self, image_path: str, prompt: str = "Extract all text from this image") -> Dict[str, Any]:
        """Обработка изображения через vLLM dots.ocr"""
        try:
            start_time = time.time()
            
            # Кодирование изображения
            image_base64 = self.encode_image_to_base64(image_path)
            
            # Подготовка запроса в формате OpenAI
            payload = {
                "model": "dots.ocr",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.0
            }
            
            # Отправка запроса
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=120  # Увеличенный timeout для OCR
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                return {
                    "success": True,
                    "content": content,
                    "model": "dots.ocr-vllm",
                    "processing_time": f"{processing_time:.3f}s",
                    "usage": result.get("usage", {}),
                    "raw_response": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "processing_time": f"{processing_time:.3f}s"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": "N/A"
            }
    
    def process_pil_image(self, image: Image.Image, prompt: str = "Extract all text from this image") -> Dict[str, Any]:
        """Обработка PIL изображения"""
        try:
            start_time = time.time()
            
            # Кодирование PIL изображения
            image_base64 = self.encode_pil_image_to_base64(image)
            
            payload = {
                "model": "dots.ocr",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.0
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=120
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                return {
                    "success": True,
                    "content": content,
                    "model": "dots.ocr-vllm",
                    "processing_time": f"{processing_time:.3f}s",
                    "usage": result.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "processing_time": f"{processing_time:.3f}s"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": "N/A"
            }
    
    def chat_completion(self, messages: List[Dict], max_tokens: int = 2048) -> Dict[str, Any]:
        """
        OpenAI совместимый метод для chatvlmllm интеграции
        
        Args:
            messages: Список сообщений в формате OpenAI
            max_tokens: Максимальное количество токенов
            
        Returns:
            Ответ в формате OpenAI API
        """
        try:
            start_time = time.time()
            
            payload = {
                "model": "dots.ocr",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.0
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=120
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                # Добавляем информацию о времени обработки
                if "usage" not in result:
                    result["usage"] = {}
                result["usage"]["processing_time"] = f"{processing_time:.3f}s"
                result["usage"]["model"] = "dots.ocr-vllm"
                
                return result
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": f"vLLM Error: {response.text}"
                        },
                        "finish_reason": "error"
                    }],
                    "usage": {
                        "processing_time": f"{processing_time:.3f}s",
                        "model": "dots.ocr-vllm",
                        "error": True
                    }
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": f"Connection error: {str(e)}"
                    },
                    "finish_reason": "error"
                }],
                "usage": {
                    "processing_time": "N/A",
                    "model": "dots.ocr-vllm",
                    "error": True
                }
            }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Получение информации о сервере"""
        try:
            # Проверка здоровья
            health = self.health_check()
            
            # Получение моделей
            models = self.get_models()
            
            # Попытка получить метрики (если доступны)
            try:
                metrics_response = self.session.get(f"{self.base_url}/metrics", timeout=5)
                metrics_available = metrics_response.status_code == 200
            except:
                metrics_available = False
            
            return {
                "healthy": health,
                "models": models,
                "metrics_available": metrics_available,
                "base_url": self.base_url
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "base_url": self.base_url
            }

# Глобальный экземпляр для использования в chatvlmllm
_vllm_client_instance = None

def get_vllm_dots_ocr_client(base_url: str = "http://localhost:8000") -> VLLMDotsOCRClient:
    """Получение глобального экземпляра vLLM клиента"""
    global _vllm_client_instance
    
    if _vllm_client_instance is None or _vllm_client_instance.base_url != base_url:
        _vllm_client_instance = VLLMDotsOCRClient(base_url)
    
    return _vllm_client_instance

def test_vllm_client():
    """Тест vLLM клиента"""
    print("🧪 ТЕСТ VLLM DOTS.OCR КЛИЕНТА")
    print("=" * 40)
    
    client = get_vllm_dots_ocr_client()
    
    # Проверка подключения
    print("🔍 Проверка подключения...")
    if not client.health_check():
        print("❌ vLLM сервер недоступен")
        print("💡 Убедитесь, что Docker контейнер запущен:")
        print("   docker ps | grep dots-ocr-server")
        return False
    
    print("✅ vLLM сервер доступен")
    
    # Получение информации о сервере
    print("\n📋 Информация о сервере:")
    server_info = client.get_server_info()
    print(f"   URL: {server_info['base_url']}")
    print(f"   Здоровье: {server_info['healthy']}")
    print(f"   Метрики: {server_info.get('metrics_available', False)}")
    
    # Создание тестового изображения
    print("\n🖼️ Создание тестового изображения...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (600, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 80), "VLLM DOTS.OCR TEST", fill='black', font=font)
        img.save('vllm_test_image.png')
        
        print("✅ Тестовое изображение создано")
        
    except Exception as e:
        print(f"❌ Ошибка создания изображения: {e}")
        return False
    
    # Тест OCR
    print("\n🔍 Тест OCR функциональности...")
    result = client.process_image('vllm_test_image.png', "Extract all text from this image")
    
    if result["success"]:
        print(f"✅ OCR успешно!")
        print(f"📝 Результат: {result['content']}")
        print(f"⏱️ Время: {result['processing_time']}")
        
        if "VLLM" in result['content'].upper() or "TEST" in result['content'].upper():
            print("🎉 Текст распознан корректно!")
            return True
        else:
            print("⚠️ Текст распознан не полностью")
            return True
    else:
        print(f"❌ OCR ошибка: {result['error']}")
        return False

if __name__ == "__main__":
    success = test_vllm_client()
    
    if success:
        print("\n🎉 VLLM DOTS.OCR КЛИЕНТ РАБОТАЕТ!")
        print("📋 Готов к интеграции в chatvlmllm")
    else:
        print("\n❌ ПРОБЛЕМЫ С VLLM КЛИЕНТОМ")
        print("💡 Проверьте настройку Docker контейнера")