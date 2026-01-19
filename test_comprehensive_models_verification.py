#!/usr/bin/env python3
"""
Комплексная проверка всех моделей на соответствие официальной документации
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import json

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_document():
    """Создаем тестовый документ для OCR"""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        small_font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=font)
    
    # Основной текст
    draw.text((50, 80), "Номер документа: 123456789", fill='black', font=small_font)
    draw.text((50, 110), "Дата выдачи: 19.01.2026", fill='black', font=small_font)
    draw.text((50, 140), "Статус: АКТИВЕН", fill='black', font=small_font)
    
    # Таблица
    draw.text((50, 180), "Таблица данных:", fill='black', font=small_font)
    draw.rectangle([50, 200, 550, 280], outline='black', width=2)
    draw.line([50, 230, 550, 230], fill='black', width=1)
    draw.line([200, 200, 200, 280], fill='black', width=1)
    draw.line([350, 200, 350, 280], fill='black', width=1)
    
    draw.text((60, 210), "Параметр", fill='black', font=small_font)
    draw.text((210, 210), "Значение", fill='black', font=small_font)
    draw.text((360, 210), "Единица", fill='black', font=small_font)
    
    draw.text((60, 240), "Температура", fill='black', font=small_font)
    draw.text((210, 240), "25.5", fill='black', font=small_font)
    draw.text((360, 240), "°C", fill='black', font=small_font)
    
    draw.text((60, 260), "Влажность", fill='black', font=small_font)
    draw.text((210, 260), "65", fill='black', font=small_font)
    draw.text((360, 260), "%", fill='black', font=small_font)
    
    # Формула
    draw.text((50, 310), "Формула: E = mc²", fill='black', font=small_font)
    
    return img

def test_model_performance(model_name, expected_keywords=None):
    """Тестирует производительность и качество модели"""
    print(f"\n🚀 ТЕСТ МОДЕЛИ: {model_name}")
    print("=" * 50)
    
    if expected_keywords is None:
        expected_keywords = ["ТЕСТОВЫЙ", "ДОКУМЕНТ", "123456789", "19.01.2026", "АКТИВЕН", "Температура", "25.5"]
    
    try:
        from models.model_loader import ModelLoader
        
        # Проверяем GPU
        if torch.cuda.is_available():
            print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"✅ VRAM: {vram_gb:.2f}GB")
        else:
            print("❌ GPU недоступна")
            return {"status": "error", "error": "No GPU"}
        
        # Загружаем модель
        print("📥 Загружаем модель...")
        start_load = time.time()
        
        model = ModelLoader.load_model(model_name)
        load_time = time.time() - start_load
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Создаем тестовое изображение
        print("🖼️ Создаем тестовый документ...")
        image = create_test_document()
        
        # Обрабатываем изображение
        print("🔍 Обрабатываем изображение...")
        start_process = time.time()
        
        if hasattr(model, 'process_image'):
            result = model.process_image(image)
        elif hasattr(model, 'chat'):
            result = model.chat(image, "Извлеки весь текст из этого изображения")
        else:
            result = "Метод обработки не найден"
        
        process_time = time.time() - start_process
        
        print(f"✅ Обработка завершена за {process_time:.3f}s")
        print(f"📝 Результат ({len(result)} символов):")
        print(f"   {result[:200]}{'...' if len(result) > 200 else ''}")
        
        # Анализируем качество OCR
        found_keywords = 0
        for keyword in expected_keywords:
            if keyword.upper() in result.upper():
                found_keywords += 1
        
        quality_score = (found_keywords / len(expected_keywords)) * 100
        print(f"🎯 Качество OCR: {found_keywords}/{len(expected_keywords)} ключевых слов ({quality_score:.1f}%)")
        
        # Проверяем на мусорный вывод
        is_garbage = False
        garbage_indicators = ["Champion", "kaps", "ADDR", "ĠĠĠ", "ĊĊĊ"]
        for indicator in garbage_indicators:
            if indicator in result:
                is_garbage = True
                break
        
        if is_garbage:
            print("⚠️ ОБНАРУЖЕН МУСОРНЫЙ ВЫВОД!")
        
        # Выгружаем модель
        print("🔄 Выгружаем модель...")
        model.unload()
        
        # Результат
        status = "excellent" if quality_score >= 80 and not is_garbage else \
                "good" if quality_score >= 60 and not is_garbage else \
                "poor" if not is_garbage else "garbage"
        
        result_data = {
            "status": status,
            "load_time": load_time,
            "process_time": process_time,
            "output_length": len(result),
            "quality_score": quality_score,
            "found_keywords": found_keywords,
            "total_keywords": len(expected_keywords),
            "is_garbage": is_garbage,
            "output_sample": result[:500]
        }
        
        print(f"🏆 СТАТУС: {status.upper()}")
        return result_data
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

def main():
    """Основная функция тестирования"""
    print("🔬 КОМПЛЕКСНАЯ ПРОВЕРКА ВСЕХ МОДЕЛЕЙ")
    print("=" * 60)
    
    # Список моделей для тестирования
    models_to_test = [
        "qwen_vl_2b",      # Эталонная модель
        "got_ocr_hf",      # Проблемная модель
        "qwen3_vl_2b",     # Многоязычная модель
        "dots_ocr",        # Документ-парсер
        "phi3_vision",     # Microsoft модель
        "deepseek_ocr",    # Экспериментальная
        "got_ocr_ucas"     # Альтернативная GOT-OCR
    ]
    
    results = {}
    
    for model_name in models_to_test:
        try:
            result = test_model_performance(model_name)
            results[model_name] = result
            
            # Пауза между тестами для очистки памяти
            time.sleep(2)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except KeyboardInterrupt:
            print("\n⏹️ Тестирование прервано пользователем")
            break
        except Exception as e:
            print(f"\n❌ Критическая ошибка при тестировании {model_name}: {e}")
            results[model_name] = {"status": "critical_error", "error": str(e)}
    
    # Сводный отчет
    print("\n" + "=" * 60)
    print("📊 СВОДНЫЙ ОТЧЕТ")
    print("=" * 60)
    
    working_models = []
    problematic_models = []
    failed_models = []
    
    for model_name, result in results.items():
        status = result.get("status", "unknown")
        
        if status in ["excellent", "good"]:
            working_models.append(model_name)
            load_time = result.get("load_time", 0)
            process_time = result.get("process_time", 0)
            quality = result.get("quality_score", 0)
            print(f"✅ {model_name:15} | {load_time:6.2f}s загрузка | {process_time:6.3f}s обработка | {quality:5.1f}% качество")
        elif status == "poor":
            problematic_models.append(model_name)
            print(f"⚠️ {model_name:15} | Низкое качество OCR")
        elif status == "garbage":
            problematic_models.append(model_name)
            print(f"🗑️ {model_name:15} | Мусорный вывод")
        else:
            failed_models.append(model_name)
            error = result.get("error", "Unknown error")
            print(f"❌ {model_name:15} | Ошибка: {error}")
    
    print(f"\n📈 ИТОГИ:")
    print(f"✅ Рабочие модели: {len(working_models)}/{len(models_to_test)} ({len(working_models)/len(models_to_test)*100:.1f}%)")
    print(f"⚠️ Проблемные модели: {len(problematic_models)}")
    print(f"❌ Нерабочие модели: {len(failed_models)}")
    
    # Сохраняем результаты
    with open("comprehensive_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в comprehensive_test_results.json")
    
    return results

if __name__ == "__main__":
    results = main()