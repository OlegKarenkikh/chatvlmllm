#!/usr/bin/env python3
"""Специальный тест для модели dots.ocr с исправлениями."""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import time
import json

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def create_test_document():
    """Создать тестовый документ с текстом."""
    # Создаем изображение с текстом
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Пытаемся использовать системный шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        title_font = ImageFont.truetype("arial.ttf", 32)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
            title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 50), "ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=title_font)
    
    # Основной текст
    text_lines = [
        "1. Первый пункт документа",
        "2. Второй пункт с важной информацией",
        "3. Третий пункт содержит данные",
        "",
        "Дата: 17 января 2026",
        "Номер: DOC-2026-001",
        "Статус: Активный",
        "",
        "Описание:",
        "Этот документ создан для тестирования",
        "системы распознавания текста dots.ocr",
        "и проверки качества извлечения данных."
    ]
    
    y_pos = 120
    for line in text_lines:
        if line.strip():
            draw.text((50, y_pos), line, fill='black', font=font)
        y_pos += 35
    
    # Добавляем рамку
    draw.rectangle([30, 30, width-30, height-30], outline='black', width=2)
    
    return image


def test_dots_ocr():
    """Тест модели dots.ocr с исправлениями."""
    print("🧪 СПЕЦИАЛЬНЫЙ ТЕСТ DOTS.OCR")
    print("=" * 50)
    
    try:
        # Проверка кеша
        is_cached, cache_msg = ModelLoader.check_model_cache("dots_ocr")
        print(f"Кеш: {cache_msg}")
        
        if not is_cached:
            print("❌ Модель не в кеше")
            return False
        
        # Создание тестового документа
        print("📄 Создание тестового документа...")
        test_image = create_test_document()
        test_image.save("test_document.png")
        print("✅ Тестовый документ создан: test_document.png")
        
        # Загрузка модели
        print("\n🚀 Загрузка модели dots.ocr...")
        start_time = time.time()
        
        try:
            model = ModelLoader.load_model("dots_ocr")
            load_time = time.time() - start_time
            print(f"✅ Модель загружена за {load_time:.2f}с")
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False
        
        # Тест различных режимов
        modes = [
            ("ocr_only", "Только извлечение текста"),
            ("layout_all", "Полный анализ макета"),
            ("layout_only", "Только структура")
        ]
        
        results = {}
        
        for mode, description in modes:
            print(f"\n🔍 Тест режима '{mode}' - {description}")
            try:
                start_time = time.time()
                result = model.process_image(test_image, mode=mode)
                process_time = time.time() - start_time
                
                print(f"✅ Обработка за {process_time:.2f}с")
                print(f"📊 Результат ({len(result)} символов):")
                
                # Показываем первые 200 символов
                preview = result[:200] + "..." if len(result) > 200 else result
                print(f"   {preview}")
                
                results[mode] = {
                    "result": result,
                    "time": process_time,
                    "length": len(result)
                }
                
            except Exception as e:
                print(f"❌ Ошибка в режиме {mode}: {e}")
                results[mode] = {"error": str(e)}
        
        # Тест чата
        print(f"\n💬 Тест чата с изображением...")
        try:
            start_time = time.time()
            chat_result = model.chat(test_image, "Извлеките все данные из этого документа в структурированном виде")
            chat_time = time.time() - start_time
            
            print(f"✅ Чат за {chat_time:.2f}с")
            print(f"📊 Ответ ({len(chat_result)} символов):")
            preview = chat_result[:300] + "..." if len(chat_result) > 300 else chat_result
            print(f"   {preview}")
            
            results["chat"] = {
                "result": chat_result,
                "time": chat_time,
                "length": len(chat_result)
            }
            
        except Exception as e:
            print(f"❌ Ошибка чата: {e}")
            results["chat"] = {"error": str(e)}
        
        # Выгрузка модели
        ModelLoader.unload_model("dots_ocr")
        print("\n🔄 Модель выгружена")
        
        # Сохранение результатов
        with open("dots_ocr_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("💾 Результаты сохранены в dots_ocr_test_results.json")
        
        # Итоги
        print(f"\n📊 ИТОГИ ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        successful = sum(1 for r in results.values() if "error" not in r)
        total = len(results)
        
        print(f"✅ Успешных тестов: {successful}/{total}")
        
        if successful > 0:
            print("🎉 dots.ocr частично работает!")
            
            # Рекомендации
            best_mode = None
            best_time = float('inf')
            
            for mode, result in results.items():
                if "error" not in result and result.get("time", float('inf')) < best_time:
                    best_time = result["time"]
                    best_mode = mode
            
            if best_mode:
                print(f"🚀 Лучший режим: {best_mode} ({best_time:.2f}с)")
        
        return successful > 0
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False


def main():
    """Основная функция."""
    success = test_dots_ocr()
    
    if success:
        print(f"\n🎯 РЕКОМЕНДАЦИИ:")
        print(f"   • Используйте режим 'ocr_only' для быстрого извлечения текста")
        print(f"   • Используйте режим 'layout_all' для полного анализа")
        print(f"   • Проверьте файл dots_ocr_test_results.json для деталей")
        print(f"\n🖼️ Тестовое изображение: test_document.png")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)