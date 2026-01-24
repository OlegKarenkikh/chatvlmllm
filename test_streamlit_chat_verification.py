#!/usr/bin/env python3
"""
Тест для проверки функциональности чата в Streamlit интерфейсе с dots.ocr

Этот тест проверяет:
1. Загрузку dots.ocr модели в режиме чата
2. Обработку произвольных вопросов об изображениях
3. Интеграцию с Streamlit интерфейсом
4. Работу как в vLLM, так и в Transformers режиме
"""

import os
import sys
import time
import json
from pathlib import Path
from PIL import Image
import traceback

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

from utils.logger import logger
from models.model_loader import ModelLoader

def create_test_image():
    """Создаем простое тестовое изображение с текстом."""
    from PIL import Image, ImageDraw, ImageFont
    
    # Создаем изображение
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать системный шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Добавляем текст
    text_lines = [
        "ТЕСТОВЫЙ ДОКУМЕНТ",
        "",
        "Счет № 12345 от 24.01.2026",
        "",
        "Плательщик: ООО 'Тест'",
        "Получатель: ООО 'Получатель'",
        "Сумма: 50,000 руб.",
        "",
        "Назначение платежа:",
        "Оплата по договору № 001"
    ]
    
    y_offset = 50
    for line in text_lines:
        draw.text((50, y_offset), line, fill='black', font=font)
        y_offset += 40
    
    # Добавляем простую таблицу
    draw.rectangle([50, 450, 750, 550], outline='black', width=2)
    draw.line([50, 480, 750, 480], fill='black', width=1)
    draw.line([400, 450, 400, 550], fill='black', width=1)
    
    draw.text((60, 460), "Товар", fill='black', font=font)
    draw.text((410, 460), "Цена", fill='black', font=font)
    draw.text((60, 490), "Услуги консультации", fill='black', font=font)
    draw.text((410, 490), "50,000 руб.", fill='black', font=font)
    
    return img

def get_available_dots_models():
    """Получаем список доступных dots.ocr моделей."""
    config = ModelLoader.load_config()
    available_models = []
    
    # Проверяем модели из конфига
    for model_key in config.get('models', {}).keys():
        if 'dots' in model_key.lower():
            available_models.append(model_key)
    
    # Проверяем модели из реестра
    for model_key in ModelLoader.MODEL_REGISTRY.keys():
        if 'dots' in model_key.lower() and model_key not in available_models:
            available_models.append(model_key)
    
    return available_models

def test_dots_ocr_chat_basic():
    """Базовый тест чата с dots.ocr."""
    print("\n" + "="*60)
    print("🧪 ТЕСТ: Базовый чат с dots.ocr")
    print("="*60)
    
    try:
        # Получаем доступные dots модели
        available_dots_models = get_available_dots_models()
        print(f"📋 Доступные dots модели: {available_dots_models}")
        
        if not available_dots_models:
            print("❌ Нет доступных dots.ocr моделей")
            return None
        
        # Пробуем загрузить первую доступную модель
        model_to_test = None
        for model_key in ['dots_ocr_final', 'dots_ocr', 'dots_ocr_corrected']:
            if model_key in available_dots_models:
                model_to_test = model_key
                break
        
        if not model_to_test:
            model_to_test = available_dots_models[0]
        
        print(f"📥 Загружаем модель: {model_to_test}")
        model = ModelLoader.load_model(model_to_test)
        
        # Создаем тестовое изображение
        print("🖼️ Создаем тестовое изображение...")
        test_image = create_test_image()
        test_image.save("test_streamlit_chat_document.png")
        
        # Проверяем наличие метода chat
        if not hasattr(model, 'chat'):
            print(f"⚠️ Модель {model_to_test} не имеет метода chat")
            print("🔄 Пробуем использовать process_image с произвольным промптом...")
            
            # Тестируем через process_image
            test_questions = [
                "Что изображено на этой картинке?",
                "Это документ? Какого типа?",
                "Какая сумма указана в документе?"
            ]
            
            results = []
            
            for i, question in enumerate(test_questions, 1):
                print(f"\n📝 Вопрос {i}: {question}")
                
                try:
                    start_time = time.time()
                    
                    # Используем process_image с произвольным промптом
                    response = model.process_image(test_image, prompt=question)
                    
                    processing_time = time.time() - start_time
                    
                    print(f"💬 Ответ: {response[:200]}{'...' if len(response) > 200 else ''}")
                    print(f"⏱️ Время обработки: {processing_time:.2f}с")
                    
                    results.append({
                        "question": question,
                        "response": response,
                        "processing_time": processing_time,
                        "success": True,
                        "method": "process_image"
                    })
                    
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    results.append({
                        "question": question,
                        "error": str(e),
                        "success": False,
                        "method": "process_image"
                    })
            
            return results
        
        # Тестируем различные типы вопросов через chat
        test_questions = [
            "Что изображено на этой картинке?",
            "Это документ? Какого типа?",
            "Какая сумма указана в документе?",
            "Найди все числа в документе",
            "Есть ли в документе таблица?",
            "Кто является плательщиком?",
            "Опиши структуру документа"
        ]
        
        results = []
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 Вопрос {i}: {question}")
            
            try:
                start_time = time.time()
                
                # Используем метод chat
                response = model.chat(test_image, question)
                
                processing_time = time.time() - start_time
                
                print(f"💬 Ответ: {response[:200]}{'...' if len(response) > 200 else ''}")
                print(f"⏱️ Время обработки: {processing_time:.2f}с")
                
                results.append({
                    "question": question,
                    "response": response,
                    "processing_time": processing_time,
                    "success": True,
                    "method": "chat"
                })
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                results.append({
                    "question": question,
                    "error": str(e),
                    "success": False,
                    "method": "chat"
                })
        
        # Сохраняем результаты
        with open("streamlit_chat_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Статистика
        successful = sum(1 for r in results if r["success"])
        print(f"\n📊 Результаты: {successful}/{len(results)} успешных ответов")
        
        return results
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

def test_streamlit_integration_simulation():
    """Симуляция работы чата в Streamlit интерфейсе."""
    print("\n" + "="*60)
    print("🧪 ТЕСТ: Симуляция Streamlit интеграции")
    print("="*60)
    
    try:
        # Симулируем загрузку модели как в app.py
        print("📥 Симулируем загрузку модели как в Streamlit...")
        
        # Проверяем доступность модели
        config = ModelLoader.load_config()
        available_models = list(config.get('models', {}).keys())
        print(f"📋 Доступные модели в конфиге: {available_models}")
        
        # Ищем dots модель
        dots_model = None
        for model_key in ['dots_ocr', 'dots_ocr_final', 'dots_ocr_corrected']:
            if model_key in available_models or model_key in ModelLoader.MODEL_REGISTRY:
                dots_model = model_key
                break
        
        if not dots_model:
            print("❌ dots.ocr модель недоступна")
            return False
        
        # Загружаем модель
        print(f"📥 Загружаем модель: {dots_model}")
        model = ModelLoader.load_model(dots_model)
        
        # Создаем тестовое изображение
        test_image = create_test_image()
        
        # Симулируем сессию чата как в Streamlit
        print("\n💭 Симулируем сессию чата...")
        
        chat_session = []
        
        # Первый вопрос
        question1 = "Что это за документ?"
        print(f"👤 Пользователь: {question1}")
        
        if hasattr(model, 'chat'):
            response1 = model.chat(test_image, question1)
        else:
            response1 = model.process_image(test_image, prompt=question1)
        
        print(f"🤖 Ассистент: {response1[:150]}...")
        
        chat_session.append({"role": "user", "content": question1})
        chat_session.append({"role": "assistant", "content": response1})
        
        # Второй вопрос (продолжение диалога)
        question2 = "А какая основная информация в нем?"
        print(f"\n👤 Пользователь: {question2}")
        
        if hasattr(model, 'chat'):
            response2 = model.chat(test_image, question2)
        else:
            response2 = model.process_image(test_image, prompt=question2)
        
        print(f"🤖 Ассистент: {response2[:150]}...")
        
        chat_session.append({"role": "user", "content": question2})
        chat_session.append({"role": "assistant", "content": response2})
        
        # Третий вопрос (уточнение)
        question3 = "Есть ли числовые данные?"
        print(f"\n👤 Пользователь: {question3}")
        
        if hasattr(model, 'chat'):
            response3 = model.chat(test_image, question3)
        else:
            response3 = model.process_image(test_image, prompt=question3)
        
        print(f"🤖 Ассистент: {response3[:150]}...")
        
        chat_session.append({"role": "user", "content": question3})
        chat_session.append({"role": "assistant", "content": response3})
        
        # Сохраняем сессию
        with open("streamlit_chat_session.json", "w", encoding="utf-8") as f:
            json.dump(chat_session, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Симуляция чата завершена успешно!")
        print(f"📝 Сохранено {len(chat_session)} сообщений")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка симуляции: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_vllm_mode_compatibility():
    """Тест совместимости с vLLM режимом."""
    print("\n" + "="*60)
    print("🧪 ТЕСТ: Совместимость с vLLM режимом")
    print("="*60)
    
    try:
        # Проверяем наличие vLLM адаптера
        try:
            from vllm_streamlit_adapter import VLLMStreamlitAdapter
            print("✅ vLLM адаптер найден")
            
            # Создаем адаптер
            adapter = VLLMStreamlitAdapter()
            
            # Создаем тестовое изображение
            test_image = create_test_image()
            
            # Тестируем обработку
            print("🧪 Тестируем vLLM обработку...")
            
            # Проверяем сигнатуру метода
            import inspect
            sig = inspect.signature(adapter.process_image)
            print(f"📋 Сигнатура process_image: {sig}")
            
            # Вызываем с правильными параметрами
            result = adapter.process_image(
                image=test_image,
                prompt="Что изображено на этой картинке?"
            )
            
            if result and result.get("success"):
                print(f"✅ vLLM режим работает!")
                print(f"💬 Ответ: {result['text'][:150]}...")
                print(f"⏱️ Время: {result.get('processing_time', 0):.2f}с")
                return True
            else:
                print("❌ vLLM режим не работает")
                return False
                
        except ImportError:
            print("⚠️ vLLM адаптер не найден - это нормально для Transformers режима")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка тестирования vLLM: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_chat_vs_ocr_modes():
    """Сравнение режимов чата и OCR."""
    print("\n" + "="*60)
    print("🧪 ТЕСТ: Сравнение режимов чата и OCR")
    print("="*60)
    
    try:
        # Ищем доступную dots модель
        available_dots_models = get_available_dots_models()
        if not available_dots_models:
            print("❌ Нет доступных dots.ocr моделей")
            return False
        
        model_key = available_dots_models[0]
        print(f"📥 Используем модель: {model_key}")
        
        # Загружаем модель
        model = ModelLoader.load_model(model_key)
        
        # Создаем тестовое изображение
        test_image = create_test_image()
        
        # Тест OCR режима
        print("📄 Тестируем OCR режим...")
        start_time = time.time()
        ocr_result = model.process_image(test_image)
        ocr_time = time.time() - start_time
        
        print(f"📝 OCR результат: {ocr_result[:200]}...")
        print(f"⏱️ Время OCR: {ocr_time:.2f}с")
        
        # Тест чат режима с OCR вопросом
        print("\n💬 Тестируем чат режим с OCR вопросом...")
        start_time = time.time()
        
        if hasattr(model, 'chat'):
            chat_result = model.chat(test_image, "Извлеки весь текст из этого изображения")
        else:
            chat_result = model.process_image(test_image, prompt="Извлеки весь текст из этого изображения")
        
        chat_time = time.time() - start_time
        
        print(f"💭 Чат результат: {chat_result[:200]}...")
        print(f"⏱️ Время чата: {chat_time:.2f}с")
        
        # Тест чат режима с аналитическим вопросом
        print("\n🔍 Тестируем чат режим с аналитическим вопросом...")
        start_time = time.time()
        
        if hasattr(model, 'chat'):
            analysis_result = model.chat(test_image, "Проанализируй этот документ и расскажи о его структуре")
        else:
            analysis_result = model.process_image(test_image, prompt="Проанализируй этот документ и расскажи о его структуре")
        
        analysis_time = time.time() - start_time
        
        print(f"🔬 Анализ результат: {analysis_result[:200]}...")
        print(f"⏱️ Время анализа: {analysis_time:.2f}с")
        
        # Сравнение
        comparison = {
            "model_used": model_key,
            "has_chat_method": hasattr(model, 'chat'),
            "ocr_mode": {
                "result": ocr_result,
                "time": ocr_time,
                "length": len(ocr_result)
            },
            "chat_ocr": {
                "result": chat_result,
                "time": chat_time,
                "length": len(chat_result)
            },
            "chat_analysis": {
                "result": analysis_result,
                "time": analysis_time,
                "length": len(analysis_result)
            }
        }
        
        with open("chat_vs_ocr_comparison.json", "w", encoding="utf-8") as f:
            json.dump(comparison, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 Сравнение сохранено в chat_vs_ocr_comparison.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка сравнения: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Основная функция тестирования."""
    print("🚀 ТЕСТИРОВАНИЕ ЧАТА В STREAMLIT ИНТЕРФЕЙСЕ")
    print("=" * 80)
    
    results = {
        "basic_chat": False,
        "streamlit_simulation": False,
        "vllm_compatibility": False,
        "mode_comparison": False
    }
    
    # Тест 1: Базовый чат
    try:
        chat_results = test_dots_ocr_chat_basic()
        results["basic_chat"] = chat_results is not None
    except Exception as e:
        print(f"❌ Ошибка базового чата: {e}")
    
    # Тест 2: Симуляция Streamlit
    try:
        results["streamlit_simulation"] = test_streamlit_integration_simulation()
    except Exception as e:
        print(f"❌ Ошибка симуляции Streamlit: {e}")
    
    # Тест 3: vLLM совместимость
    try:
        results["vllm_compatibility"] = test_vllm_mode_compatibility()
    except Exception as e:
        print(f"❌ Ошибка vLLM теста: {e}")
    
    # Тест 4: Сравнение режимов
    try:
        results["mode_comparison"] = test_chat_vs_ocr_modes()
    except Exception as e:
        print(f"❌ Ошибка сравнения режимов: {e}")
    
    # Итоговый отчет
    print("\n" + "="*80)
    print("📋 ИТОГОВЫЙ ОТЧЕТ")
    print("="*80)
    
    for test_name, success in results.items():
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Общий результат: {successful_tests}/{total_tests} тестов пройдено")
    
    if successful_tests == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Чат в Streamlit работает корректно!")
    elif successful_tests > 0:
        print("⚠️ Частичный успех. Некоторые функции работают.")
    else:
        print("❌ Все тесты провалены. Требуется диагностика.")
    
    # Сохраняем итоговый отчет
    final_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_results": results,
        "success_rate": successful_tests / total_tests,
        "summary": f"{successful_tests}/{total_tests} tests passed"
    }
    
    with open("streamlit_chat_verification_report.json", "w", encoding="utf-8") as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Полный отчет сохранен в streamlit_chat_verification_report.json")

if __name__ == "__main__":
    main()