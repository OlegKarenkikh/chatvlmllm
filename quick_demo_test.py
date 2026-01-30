#!/usr/bin/env python3
"""
Быстрая демонстрация возможностей dots.ocr
"""

from PIL import Image, ImageDraw, ImageFont
import time
from dots_ocr_client import DotsOCRClient

def create_demo_document():
    """Создание демонстрационного документа"""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 18)
        font_large = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
        font_large = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "ДЕМОНСТРАЦИЯ DOTS.OCR", fill='black', font=font_large)
    
    # Содержимое
    content = """
Система успешно распознает:
• Русский и English текст
• Числа: 123,456.78 руб.
• Даты: 24.01.2026
• Телефоны: +7 (495) 123-45-67
• Email: demo@example.com
• Проценты: 85.7% точность

Время обработки: ~1.8 секунды
Скорость: 26.6 слов/сек
Модель: rednote-hilab/dots.ocr
"""
    
    y_pos = 80
    for line in content.strip().split('\n'):
        draw.text((50, y_pos), line, fill='black', font=font)
        y_pos += 22
    
    img.save("demo_document.png")
    print("✅ Демо-документ создан: demo_document.png")

def run_demo():
    """Запуск демонстрации"""
    print("🚀 БЫСТРАЯ ДЕМОНСТРАЦИЯ DOTS.OCR")
    print("=" * 40)
    
    # Создание документа
    create_demo_document()
    
    # Инициализация клиента
    client = DotsOCRClient()
    
    # Проверка сервера
    if not client.health_check():
        print("❌ Сервер недоступен!")
        return
    
    print("✅ Сервер готов")
    print()
    
    # OCR обработка
    print("🔄 Обработка демо-документа...")
    start_time = time.time()
    
    result = client.process_image("demo_document.png")
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    if result["success"]:
        text = result["text"]
        word_count = len(text.split())
        speed = word_count / processing_time if processing_time > 0 else 0
        
        print(f"✅ Обработка завершена за {processing_time:.1f}с")
        print(f"📊 Распознано {word_count} слов")
        print(f"🚀 Скорость: {speed:.1f} слов/сек")
        print()
        print("📝 РЕЗУЛЬТАТ OCR:")
        print("-" * 30)
        print(text)
        print("-" * 30)
        
        # Анализ качества
        has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in text)
        has_latin = any(char.isascii() and char.isalpha() for char in text)
        has_numbers = any(char.isdigit() for char in text)
        
        print()
        print("🎯 АНАЛИЗ КАЧЕСТВА:")
        print(f"   Кириллица: {'✅' if has_cyrillic else '❌'}")
        print(f"   Латиница: {'✅' if has_latin else '❌'}")
        print(f"   Числа: {'✅' if has_numbers else '❌'}")
        print(f"   Длина текста: {len(text)} символов")
        
    else:
        print(f"❌ Ошибка: {result['error']}")

if __name__ == "__main__":
    run_demo()