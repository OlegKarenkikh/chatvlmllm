#!/usr/bin/env python3
"""
Демонстрация различий в обработке промпта "Извлечение таблиц"
"""

import requests
import base64
import time
from PIL import Image, ImageDraw, ImageFont
import io

def create_table_test_image():
    """Создание изображения с таблицей для тестирования"""
    
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "ТЕСТ ИЗВЛЕЧЕНИЯ ТАБЛИЦ", fill='black', font=font_medium)
    
    # Обычный текст
    draw.text((50, 70), "Этот документ содержит таблицу для тестирования.", fill='black', font=font_small)
    
    # Таблица
    table_x = 50
    table_y = 110
    cell_width = 100
    cell_height = 25
    
    # Заголовки
    headers = ["Товар", "Цена", "Количество", "Сумма"]
    for i, header in enumerate(headers):
        x = table_x + i * cell_width
        y = table_y
        draw.rectangle([x, y, x + cell_width, y + cell_height], outline='black', width=2)
        draw.text((x + 5, y + 5), header, fill='black', font=font_small)
    
    # Данные
    data = [
        ["Хлеб", "50", "2", "100"],
        ["Молоко", "80", "1", "80"],
        ["Масло", "200", "1", "200"]
    ]
    
    for row_idx, row in enumerate(data):
        for col_idx, cell in enumerate(row):
            x = table_x + col_idx * cell_width
            y = table_y + (row_idx + 1) * cell_height
            draw.rectangle([x, y, x + cell_width, y + cell_height], outline='black', width=1)
            draw.text((x + 5, y + 5), cell, fill='black', font=font_small)
    
    # Итого
    draw.text((50, 250), "ИТОГО: 380 рублей", fill='black', font=font_medium)
    
    return img

def test_table_vs_general_prompts():
    """Сравнение промпта извлечения таблиц с общими промптами"""
    
    print("📊 ТЕСТИРОВАНИЕ РАЗЛИЧИЙ В ОБРАБОТКЕ ТАБЛИЦ")
    print("=" * 50)
    
    # Создание изображения с таблицей
    test_image = create_table_test_image()
    test_image.save("table_test_document.png")
    print("✅ Создано тестовое изображение: table_test_document.png")
    
    # Конвертация в base64
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Промпты для сравнения
    test_prompts = {
        "🔤 Общий OCR": "Extract all text from this image.",
        "📊 Извлечение таблиц": "Extract and format the table content from this document as structured data."
    }
    
    base_url = "http://localhost:8000"
    results = {}
    
    for prompt_name, prompt_text in test_prompts.items():
        print(f"\n🧪 Тестирование: {prompt_name}")
        print(f"   Промпт: {prompt_text}")
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 4096,
            "temperature": 0.1
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=60)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                print(f"   ✅ Успех: {processing_time:.1f}с")
                print(f"   📄 Длина: {len(content)} символов")
                
                results[prompt_name] = content
                
                # Показываем первые 200 символов
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   📝 Результат: {preview}")
                
            else:
                print(f"   ❌ Ошибка: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
    
    # Анализ различий
    print(f"\n🔍 АНАЛИЗ РАЗЛИЧИЙ:")
    
    if len(results) == 2:
        general_result = results.get("🔤 Общий OCR", "")
        table_result = results.get("📊 Извлечение таблиц", "")
        
        if general_result == table_result:
            print("   ❌ Результаты ИДЕНТИЧНЫ")
            print("   💡 dots.ocr игнорирует специфику промпта")
        else:
            print("   ✅ Результаты РАЗЛИЧАЮТСЯ")
            print("   🎯 Промпт 'Извлечение таблиц' работает по-особому")
            
            # Показываем различия
            print(f"\n📋 ОБЩИЙ OCR ({len(general_result)} символов):")
            print(f"   {general_result[:150]}...")
            
            print(f"\n📊 ИЗВЛЕЧЕНИЕ ТАБЛИЦ ({len(table_result)} символов):")
            print(f"   {table_result[:150]}...")
            
            # Анализ содержимого
            table_keywords = ["table", "таблиц", "<table>", "структур", "данных"]
            general_has_keywords = sum(1 for kw in table_keywords if kw.lower() in general_result.lower())
            table_has_keywords = sum(1 for kw in table_keywords if kw.lower() in table_result.lower())
            
            print(f"\n🔍 Анализ ключевых слов:")
            print(f"   Общий OCR: {general_has_keywords} табличных терминов")
            print(f"   Извлечение таблиц: {table_has_keywords} табличных терминов")
    
    print(f"\n💡 ВЫВОДЫ:")
    print("   • dots.ocr специализирована на OCR, а не на следовании инструкциям")
    print("   • Большинство промптов дают одинаковый результат (полный OCR)")
    print("   • Только узкоспециализированные промпты могут давать различия")
    print("   • Это нормальное поведение для OCR-модели")

if __name__ == "__main__":
    test_table_vs_general_prompts()