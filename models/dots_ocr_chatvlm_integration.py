#!/usr/bin/env python3
"""
dots.ocr интеграция для проекта chatvlmllm
Оптимизировано для RTX 5070 Ti Blackwell архитектуры
"""

import torch
import time
import logging
from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image
import base64
import io
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DotsOCRChatVLM:
    """dots.ocr интеграция для chatvlmllm проекта"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = "rednote-hilab/dots.ocr"
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """Загрузка модели с Blackwell оптимизациями"""
        try:
            start_time = time.time()
            
            logger.info("🚀 Загружаем dots.ocr для chatvlmllm...")
            
            # Blackwell оптимизации для RTX 5070 Ti
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.enable_flash_sdp(True)
            
            # Загрузка модели с правильными параметрами
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,  # Оптимально для Blackwell
                attn_implementation="eager",  # ОБЯЗАТЕЛЬНО для RTX 5070 Ti
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Загрузка процессора
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            load_time = time.time() - start_time
            vram_used = torch.cuda.memory_allocated() / 1024**3
            
            logger.info(f"✅ dots.ocr загружена за {load_time:.2f}s")
            logger.info(f"✅ VRAM использовано: {vram_used:.2f}GB")
            logger.info(f"✅ Готова для chatvlmllm интеграции")
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки dots.ocr: {e}")
            self.is_loaded = False
            return False
    
    def _process_image_from_url(self, image_url: str) -> Optional[Image.Image]:
        """Обработка изображения из URL или base64"""
        try:
            if image_url.startswith('data:image'):
                # Base64 изображение
                header, data = image_url.split(',', 1)
                image_data = base64.b64decode(data)
                return Image.open(io.BytesIO(image_data)).convert('RGB')
            elif image_url.startswith('http'):
                # URL изображение
                response = requests.get(image_url)
                return Image.open(io.BytesIO(response.content)).convert('RGB')
            else:
                # Локальный файл
                return Image.open(image_url).convert('RGB')
        except Exception as e:
            logger.error(f"Ошибка обработки изображения: {e}")
            return None
    
    def chat_completion(self, messages: List[Dict], max_tokens: int = 2048) -> Dict[str, Any]:
        """
        OpenAI совместимый API для chatvlmllm
        
        Args:
            messages: Список сообщений в формате OpenAI
            max_tokens: Максимальное количество токенов
            
        Returns:
            Ответ в формате OpenAI API
        """
        if not self.is_loaded:
            return {
                "error": "dots.ocr model not loaded",
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "Model not available"
                    }
                }]
            }
        
        try:
            start_time = time.time()
            
            # Извлечение изображения и текста из messages
            image_content = None
            text_content = "Extract all text from this image"
            
            for message in messages:
                if message.get("role") == "user":
                    content = message.get("content", [])
                    
                    # Обработка разных форматов content
                    if isinstance(content, str):
                        text_content = content
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                if item.get("type") == "image_url":
                                    image_url = item.get("image_url", {})
                                    if isinstance(image_url, dict):
                                        url = image_url.get("url")
                                    else:
                                        url = image_url
                                    
                                    if url:
                                        image_content = self._process_image_from_url(url)
                                        
                                elif item.get("type") == "text":
                                    text_content = item.get("text", text_content)
            
            if not image_content:
                return {
                    "error": "No image provided",
                    "choices": [{
                        "message": {
                            "role": "assistant", 
                            "content": "Please provide an image for OCR processing"
                        }
                    }]
                }
            
            # Обработка через dots.ocr
            result = self.process_image(image_content, text_content, max_tokens)
            
            processing_time = time.time() - start_time
            
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result or "No text detected in the image"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "processing_time": f"{processing_time:.3f}s",
                    "model": "dots.ocr"
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка chat_completion: {e}")
            return {
                "error": str(e),
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": f"Error processing request: {str(e)}"
                    }
                }]
            }
    
    def process_image(self, image: Image.Image, prompt: str, max_tokens: int = 2048) -> Optional[str]:
        """
        Основная обработка изображения через dots.ocr
        
        Args:
            image: PIL изображение
            prompt: Текстовый промпт
            max_tokens: Максимальное количество токенов
            
        Returns:
            Извлеченный текст или None при ошибке
        """
        if not self.model or not self.processor:
            logger.error("Модель не загружена")
            return None
            
        try:
            # Правильный формат сообщений для dots.ocr (без qwen_vl_utils)
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }]
            
            # Применение chat template
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Прямая обработка без qwen_vl_utils
            inputs = self.processor(
                text=[text],
                images=[image],
                padding=True,
                return_tensors="pt",
            ).to("cuda")
            
            # Генерация с оптимизированными параметрами для Blackwell
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.1,
                    top_p=0.9,
                    use_cache=True,
                    pad_token_id=self.processor.tokenizer.eos_token_id,
                    eos_token_id=self.processor.tokenizer.eos_token_id,
                    # Параметры против повторений
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=3
                )
            
            # Декодирование результата
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            result = output_text.strip()
            
            # Проверка на пустой результат
            if not result or result.lower() in ['', 'none', 'no text']:
                logger.warning("dots.ocr вернула пустой результат")
                return None
                
            logger.info(f"✅ dots.ocr обработала изображение: {len(result)} символов")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка обработки изображения: {e}")
            return None
    
    def cleanup(self):
        """Очистка памяти"""
        if self.model:
            del self.model
            self.model = None
        if self.processor:
            del self.processor
            self.processor = None
        
        torch.cuda.empty_cache()
        self.is_loaded = False
        logger.info("🧹 dots.ocr память очищена")

# Глобальный экземпляр для использования в chatvlmllm
_dots_ocr_instance = None

def get_dots_ocr_instance() -> DotsOCRChatVLM:
    """Получение глобального экземпляра dots.ocr"""
    global _dots_ocr_instance
    
    if _dots_ocr_instance is None:
        _dots_ocr_instance = DotsOCRChatVLM()
        
    return _dots_ocr_instance

def initialize_dots_ocr() -> bool:
    """Инициализация dots.ocr для chatvlmllm"""
    instance = get_dots_ocr_instance()
    return instance.load_model()

# Тестирование интеграции
def test_chatvlm_integration():
    """Тест интеграции с chatvlmllm"""
    print("🧪 ТЕСТ ИНТЕГРАЦИИ DOTS.OCR С CHATVLMLLM")
    print("=" * 60)
    
    # Информация о системе
    print(f"🖥️ GPU: {torch.cuda.get_device_name(0)}")
    print(f"🐍 PyTorch: {torch.__version__}")
    print(f"⚡ CUDA: {torch.version.cuda}")
    print()
    
    # Инициализация
    if not initialize_dots_ocr():
        print("❌ Не удалось инициализировать dots.ocr")
        return False
    
    # Тестовые данные в формате chatvlmllm/OpenAI
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "test_document.png"}
                },
                {
                    "type": "text", 
                    "text": "Extract all text from this document in Russian and English"
                }
            ]
        }
    ]
    
    # Тест обработки
    instance = get_dots_ocr_instance()
    result = instance.chat_completion(messages, max_tokens=1024)
    
    print("📋 Результат обработки:")
    print(f"✅ Статус: {'Успех' if 'error' not in result else 'Ошибка'}")
    
    if 'error' not in result:
        content = result['choices'][0]['message']['content']
        print(f"📝 Текст: {content[:200]}...")
        print(f"⏱️ Время: {result.get('usage', {}).get('processing_time', 'N/A')}")
        print("🎉 ИНТЕГРАЦИЯ РАБОТАЕТ!")
        return True
    else:
        print(f"❌ Ошибка: {result['error']}")
        return False

if __name__ == "__main__":
    success = test_chatvlm_integration()
    if success:
        print("\n🚀 DOTS.OCR ГОТОВА ДЛЯ ИСПОЛЬЗОВАНИЯ В CHATVLMLLM!")
    else:
        print("\n❌ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")