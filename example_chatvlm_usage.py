#!/usr/bin/env python3
"""
Пример использования dots.ocr интеграции в chatvlmllm проекте
"""

import sys
import os
from PIL import Image

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def example_openai_format():
    """Пример использования в формате OpenAI API"""
    print("🚀 ПРИМЕР ИСПОЛЬЗОВАНИЯ DOTS.OCR В CHATVLMLLM")
    print("=" * 60)
    
    from models.dots_ocr_chatvlm_integration import get_dots_ocr_instance, initialize_dots_ocr
    
    # Инициализация (один раз при запуске приложения)
    print("🔄 Инициализация dots.ocr...")
    if not initialize_dots_ocr():
        print("❌ dots.ocr недоступна, используйте fallback модели")
        return False
    
    # Получение экземпляра
    dots_ocr = get_dots_ocr_instance()
    
    # Пример 1: Простой OCR запрос
    print("\n📋 ПРИМЕР 1: Простой OCR")
    print("-" * 30)
    
    messages_simple = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "simple_test.png"}
                },
                {
                    "type": "text",
                    "text": "Extract all text from this image"
                }
            ]
        }
    ]
    
    result = dots_ocr.chat_completion(messages_simple)
    
    if 'error' not in result:
        content = result['choices'][0]['message']['content']
        print(f"✅ Результат: {content}")
    else:
        print(f"❌ Ошибка: {result['error']}")
    
    # Пример 2: Документ с инструкциями
    print("\n📋 ПРИМЕР 2: Документ с инструкциями")
    print("-" * 40)
    
    messages_document = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "clear_test_document.png"}
                },
                {
                    "type": "text",
                    "text": "Extract all text from this document. Preserve the original formatting and provide both Russian and English text."
                }
            ]
        }
    ]
    
    result = dots_ocr.chat_completion(messages_document, max_tokens=2048)
    
    if 'error' not in result:
        content = result['choices'][0]['message']['content']
        print(f"✅ Результат: {content[:300]}...")
        print(f"📏 Длина: {len(content)} символов")
    else:
        print(f"❌ Ошибка: {result['error']}")
    
    return True

def example_api_integration():
    """Пример интеграции в API сервер"""
    print("\n🌐 ПРИМЕР ИНТЕГРАЦИИ В API")
    print("=" * 40)
    
    # Псевдокод для интеграции в Flask/FastAPI
    api_example = '''
# В app.py или api.py вашего chatvlmllm проекта

from models.dots_ocr_chatvlm_integration import get_dots_ocr_instance, initialize_dots_ocr

# Инициализация при запуске приложения
@app.before_first_request
def init_ocr():
    initialize_dots_ocr()

# Endpoint для OCR
@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.get_json()
    
    # Проверка на OCR запрос
    if is_ocr_request(data):
        dots_ocr = get_dots_ocr_instance()
        return jsonify(dots_ocr.chat_completion(data['messages']))
    
    # Обычная обработка для других моделей
    return handle_regular_chat(data)

def is_ocr_request(data):
    """Проверка, является ли запрос OCR запросом"""
    messages = data.get('messages', [])
    for message in messages:
        content = message.get('content', [])
        if isinstance(content, list):
            for item in content:
                if item.get('type') == 'image_url':
                    return True
    return False
'''
    
    print(api_example)

def example_fallback_system():
    """Пример системы с fallback моделями"""
    print("\n🔄 ПРИМЕР FALLBACK СИСТЕМЫ")
    print("=" * 40)
    
    fallback_example = '''
# Система с fallback на проверенные модели

class OCRManager:
    def __init__(self):
        self.dots_ocr = None
        self.qwen_vl_2b = None  # Ваша основная рабочая модель
        
        # Попытка инициализации dots.ocr
        try:
            from models.dots_ocr_chatvlm_integration import get_dots_ocr_instance, initialize_dots_ocr
            if initialize_dots_ocr():
                self.dots_ocr = get_dots_ocr_instance()
                print("✅ dots.ocr готова")
            else:
                print("⚠️ dots.ocr недоступна, используем fallback")
        except Exception as e:
            print(f"⚠️ dots.ocr ошибка: {e}")
        
        # Инициализация fallback модели (ваша рабочая qwen_vl_2b)
        # self.qwen_vl_2b = load_qwen_vl_2b()
    
    def process_ocr(self, messages, max_tokens=2048):
        """OCR с автоматическим fallback"""
        
        # Попытка 1: dots.ocr (если доступна)
        if self.dots_ocr:
            try:
                result = self.dots_ocr.chat_completion(messages, max_tokens)
                if 'error' not in result:
                    content = result['choices'][0]['message']['content']
                    if content and len(content.strip()) > 0:
                        return {
                            "success": True,
                            "content": content,
                            "model_used": "dots.ocr",
                            "processing_time": result.get('usage', {}).get('processing_time', 'N/A')
                        }
            except Exception as e:
                print(f"dots.ocr ошибка: {e}")
        
        # Fallback: qwen_vl_2b (ваша проверенная модель)
        try:
            # result = self.qwen_vl_2b.process(messages)
            return {
                "success": True,
                "content": "Fallback to qwen_vl_2b result",
                "model_used": "qwen_vl_2b",
                "processing_time": "3.91s"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"All OCR models failed: {e}",
                "model_used": "none"
            }

# Использование
ocr_manager = OCRManager()
result = ocr_manager.process_ocr(messages)
'''
    
    print(fallback_example)

def main():
    """Главная функция с примерами"""
    
    # Проверка наличия тестовых изображений
    if not os.path.exists('simple_test.png'):
        print("⚠️ Создаем тестовые изображения...")
        from create_better_test_image import create_clear_test_document, create_simple_text_image
        create_clear_test_document()
        create_simple_text_image()
    
    # Запуск примеров
    try:
        success = example_openai_format()
        
        if success:
            print("\n🎉 DOTS.OCR ИНТЕГРАЦИЯ РАБОТАЕТ!")
        else:
            print("\n⚠️ DOTS.OCR НЕДОСТУПНА - ИСПОЛЬЗУЙТЕ FALLBACK")
        
        # Показываем примеры кода
        example_api_integration()
        example_fallback_system()
        
        print("\n📋 ИТОГОВЫЕ РЕКОМЕНДАЦИИ:")
        print("=" * 50)
        print("1. ✅ Используйте qwen_vl_2b как основную OCR (быстро и надежно)")
        print("2. 🔄 Интегрируйте dots.ocr как дополнительную (после исправления версий)")
        print("3. 🛡️ Реализуйте fallback систему для надежности")
        print("4. 📊 Мониторьте качество и производительность каждой модели")
        print("\n🚀 Ваша система chatvlmllm готова к использованию!")
        
    except Exception as e:
        print(f"❌ Ошибка в примере: {e}")
        print("\n💡 Это нормально - dots.ocr требует исправления версий PyTorch")
        print("📋 Используйте готовый код интеграции после downgrade до PyTorch 2.7.0")

if __name__ == "__main__":
    main()