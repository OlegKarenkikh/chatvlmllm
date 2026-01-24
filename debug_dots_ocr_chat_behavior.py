#!/usr/bin/env python3
"""
Отладка поведения dots.ocr в режиме чата
Проверяем, почему модель отдает полные результаты OCR на любой вопрос
"""

import os
import sys
import time
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import traceback

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

def create_simple_test_image():
    """Создаем простое тестовое изображение."""
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Простой текст
    draw.text((20, 50), "Hello World!", fill='black', font=font)
    draw.text((20, 80), "This is a test document.", fill='black', font=font)
    draw.text((20, 110), "Number: 12345", fill='black', font=font)
    
    return img

def test_vllm_prompt_behavior():
    """Тестируем поведение dots.ocr с разными промптами в vLLM режиме."""
    print("🔍 ТЕСТИРОВАНИЕ ПОВЕДЕНИЯ dots.ocr В vLLM РЕЖИМЕ")
    print("=" * 60)
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        
        # Создаем адаптер
        adapter = VLLMStreamlitAdapter()
        
        # Создаем тестовое изображение
        test_image = create_simple_test_image()
        test_image.save("debug_simple_test.png")
        print("📷 Создано тестовое изображение: debug_simple_test.png")
        
        # Тестируем разные промпты
        test_prompts = [
            "Extract all text from this image",  # Стандартный OCR промпт
            "What do you see in this image?",    # Общий вопрос
            "What is the number in this image?", # Конкретный вопрос
            "Describe this image briefly",       # Описание
            "Is there any text in this image?",  # Да/нет вопрос
            "What color is the background?",     # Вопрос о цвете
            "How many words are there?",         # Подсчет
            "Tell me a joke",                    # Совершенно не связанный вопрос
        ]
        
        results = []
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Тест {i}: {prompt}")
            print("-" * 40)
            
            try:
                start_time = time.time()
                
                # Отправляем запрос
                result = adapter.process_image(
                    image=test_image,
                    prompt=prompt,
                    model="rednote-hilab/dots.ocr"
                )
                
                processing_time = time.time() - start_time
                
                if result and result.get("success"):
                    response = result["text"]
                    print(f"✅ Успех ({processing_time:.2f}с)")
                    print(f"📄 Ответ: {response[:150]}{'...' if len(response) > 150 else ''}")
                    
                    # Анализируем ответ
                    is_full_ocr = "Hello World" in response and "test document" in response and "12345" in response
                    is_specific_answer = len(response) < 100 and not is_full_ocr
                    
                    analysis = {
                        "prompt": prompt,
                        "response": response,
                        "response_length": len(response),
                        "processing_time": processing_time,
                        "is_full_ocr": is_full_ocr,
                        "is_specific_answer": is_specific_answer,
                        "success": True
                    }
                    
                    if is_full_ocr:
                        print("🔍 Анализ: ПОЛНОЕ OCR (игнорирует промпт)")
                    elif is_specific_answer:
                        print("🎯 Анализ: СПЕЦИФИЧЕСКИЙ ОТВЕТ (учитывает промпт)")
                    else:
                        print("❓ Анализ: НЕОПРЕДЕЛЕННЫЙ ОТВЕТ")
                    
                else:
                    print("❌ Ошибка обработки")
                    analysis = {
                        "prompt": prompt,
                        "error": "Processing failed",
                        "success": False
                    }
                
                results.append(analysis)
                
            except Exception as e:
                print(f"❌ Исключение: {e}")
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
        
        # Сохраняем результаты
        with open("dots_ocr_chat_behavior_analysis.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Анализ результатов
        print("\n" + "=" * 60)
        print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("=" * 60)
        
        successful_tests = [r for r in results if r.get("success")]
        full_ocr_responses = [r for r in successful_tests if r.get("is_full_ocr")]
        specific_responses = [r for r in successful_tests if r.get("is_specific_answer")]
        
        print(f"✅ Успешных тестов: {len(successful_tests)}/{len(results)}")
        print(f"🔍 Полное OCR: {len(full_ocr_responses)} тестов")
        print(f"🎯 Специфические ответы: {len(specific_responses)} тестов")
        
        if len(full_ocr_responses) > len(specific_responses):
            print("\n❌ ПРОБЛЕМА ПОДТВЕРЖДЕНА:")
            print("   dots.ocr игнорирует произвольные промпты и всегда выполняет полное OCR")
        elif len(specific_responses) > 0:
            print("\n✅ ХОРОШИЕ НОВОСТИ:")
            print("   dots.ocr может отвечать на специфические вопросы")
        else:
            print("\n❓ НЕОПРЕДЕЛЕННЫЙ РЕЗУЛЬТАТ:")
            print("   Требуется дополнительный анализ")
        
        return results
        
    except ImportError:
        print("❌ vLLM адаптер недоступен")
        return None
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def test_transformers_prompt_behavior():
    """Тестируем поведение dots.ocr с разными промптами в Transformers режиме."""
    print("\n🔍 ТЕСТИРОВАНИЕ ПОВЕДЕНИЯ dots.ocr В TRANSFORMERS РЕЖИМЕ")
    print("=" * 60)
    
    try:
        from models.model_loader import ModelLoader
        
        # Пробуем загрузить dots.ocr модель
        available_dots_models = []
        config = ModelLoader.load_config()
        
        for model_key in config.get('models', {}).keys():
            if 'dots' in model_key.lower():
                available_dots_models.append(model_key)
        
        for model_key in ModelLoader.MODEL_REGISTRY.keys():
            if 'dots' in model_key.lower() and model_key not in available_dots_models:
                available_dots_models.append(model_key)
        
        if not available_dots_models:
            print("❌ Нет доступных dots.ocr моделей в Transformers режиме")
            return None
        
        print(f"📋 Доступные модели: {available_dots_models}")
        
        # Пробуем загрузить первую доступную модель
        model_key = available_dots_models[0]
        print(f"📥 Загружаем модель: {model_key}")
        
        try:
            model = ModelLoader.load_model(model_key)
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            return None
        
        # Создаем тестовое изображение
        test_image = create_simple_test_image()
        
        # Тестируем разные промпты
        test_prompts = [
            "Extract all text from this image",
            "What do you see in this image?",
            "What is the number in this image?",
            "Is there any text in this image?",
        ]
        
        results = []
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Тест {i}: {prompt}")
            print("-" * 40)
            
            try:
                start_time = time.time()
                
                # Пробуем разные методы
                if hasattr(model, 'chat'):
                    response = model.chat(test_image, prompt)
                    method = "chat"
                elif hasattr(model, 'process_image'):
                    response = model.process_image(test_image, prompt=prompt)
                    method = "process_image"
                else:
                    response = model.process_image(test_image)
                    method = "process_image_no_prompt"
                
                processing_time = time.time() - start_time
                
                print(f"✅ Успех ({processing_time:.2f}с, метод: {method})")
                print(f"📄 Ответ: {response[:150]}{'...' if len(response) > 150 else ''}")
                
                results.append({
                    "prompt": prompt,
                    "response": response,
                    "method": method,
                    "processing_time": processing_time,
                    "success": True
                })
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
        
        return results
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return None

def analyze_prompt_processing():
    """Анализируем как dots.ocr обрабатывает промпты."""
    print("🔬 АНАЛИЗ ОБРАБОТКИ ПРОМПТОВ В dots.ocr")
    print("=" * 60)
    
    # Проверяем официальную документацию dots.ocr
    print("📚 Официальные промпты dots.ocr:")
    
    official_prompts = {
        "prompt_layout_all_en": "Extract text, layout, and structure from this document image.",
        "prompt_layout_only_en": "Detect layout elements and their positions in this document.",
        "prompt_ocr": "Extract all text content from this image.",
        "prompt_grounding_ocr": "Extract text from the specified region in this image."
    }
    
    for name, prompt in official_prompts.items():
        print(f"  • {name}: {prompt}")
    
    print("\n🤔 ВОЗМОЖНЫЕ ПРИЧИНЫ ПРОБЛЕМЫ:")
    print("1. dots.ocr оптимизирована для OCR задач, а не для общего чата")
    print("2. Модель может игнорировать произвольные промпты")
    print("3. vLLM сервер может использовать фиксированный промпт")
    print("4. Нужно использовать специальные промпты для dots.ocr")
    
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("1. Проверить конфигурацию vLLM сервера")
    print("2. Использовать официальные промпты dots.ocr")
    print("3. Добавить логирование промптов в vLLM адаптер")
    print("4. Рассмотреть использование других VLM для чата")

def main():
    """Основная функция отладки."""
    print("🐛 ОТЛАДКА ПОВЕДЕНИЯ dots.ocr В РЕЖИМЕ ЧАТА")
    print("=" * 80)
    
    # Тест 1: vLLM режим
    vllm_results = test_vllm_prompt_behavior()
    
    # Тест 2: Transformers режим
    transformers_results = test_transformers_prompt_behavior()
    
    # Тест 3: Анализ промптов
    analyze_prompt_processing()
    
    # Итоговый отчет
    print("\n" + "=" * 80)
    print("📋 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 80)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "vllm_results": vllm_results,
        "transformers_results": transformers_results,
        "analysis": {
            "vllm_available": vllm_results is not None,
            "transformers_available": transformers_results is not None,
            "issue_confirmed": False
        }
    }
    
    if vllm_results:
        successful_vllm = [r for r in vllm_results if r.get("success")]
        full_ocr_vllm = [r for r in successful_vllm if r.get("is_full_ocr")]
        
        if len(full_ocr_vllm) > len(successful_vllm) // 2:
            report["analysis"]["issue_confirmed"] = True
            print("❌ ПРОБЛЕМА ПОДТВЕРЖДЕНА: dots.ocr игнорирует произвольные промпты")
        else:
            print("✅ Проблема не подтверждена или частично решена")
    
    # Сохраняем отчет
    with open("dots_ocr_chat_debug_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен в dots_ocr_chat_debug_report.json")

if __name__ == "__main__":
    main()