#!/usr/bin/env python3
"""
Создание лучшего тестового изображения для dots.ocr
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_clear_test_document():
    """Создание четкого тестового документа"""
    
    # Создаем изображение высокого разрешения
    img = Image.new('RGB', (1200, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Пытаемся найти хороший шрифт
    font_size = 36
    try:
        # Windows шрифты
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf", 
            "C:/Windows/Fonts/times.ttf"
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        
        if font is None:
            font = ImageFont.load_default()
            
    except:
        font = ImageFont.load_default()
    
    # Простой и четкий текст
    texts = [
        "ТЕСТОВЫЙ ДОКУМЕНТ",
        "",
        "Test Document in English",
        "",
        "Номер: 123456789",
        "Number: 123456789", 
        "",
        "Дата: 24 января 2026",
        "Date: January 24, 2026",
        "",
        "Статус: АКТИВНЫЙ",
        "Status: ACTIVE"
    ]
    
    # Рисуем текст с хорошими отступами
    y_position = 80
    for text in texts:
        if text:  # Пропускаем пустые строки
            draw.text((100, y_position), text, fill='black', font=font)
        y_position += 50
    
    # Добавляем четкую рамку
    draw.rectangle([50, 50, 1150, 750], outline='black', width=3)
    
    # Сохраняем в высоком качестве
    img.save('clear_test_document.png', quality=95, optimize=True)
    print("✅ Создан четкий тестовый документ: clear_test_document.png")
    
    return 'clear_test_document.png'

def create_simple_text_image():
    """Создание очень простого изображения с текстом"""
    
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    
    # Очень простой текст
    text = "HELLO WORLD 123"
    
    # Центрируем текст
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (800 - text_width) // 2
    y = (200 - text_height) // 2
    
    draw.text((x, y), text, fill='black', font=font)
    
    img.save('simple_test.png', quality=95)
    print("✅ Создано простое изображение: simple_test.png")
    
    return 'simple_test.png'

if __name__ == "__main__":
    print("🖼️ Создание тестовых изображений для dots.ocr...")
    
    clear_doc = create_clear_test_document()
    simple_img = create_simple_text_image()
    
    print(f"📄 Четкий документ: {clear_doc}")
    print(f"📝 Простой текст: {simple_img}")
    print("🎯 Готово для тестирования!")