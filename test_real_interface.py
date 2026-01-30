#!/usr/bin/env python3
"""Тест реального интерфейса с тем же изображением."""

import sys
from pathlib import Path
from PIL import Image
import time

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def test_with_real_image():
    """Тест с реальным изображением из интерфейса."""
    print("🧪 ТЕСТ С РЕАЛЬНЫМ ИЗОБРАЖЕНИЕМ")
    print("=" * 50)
    
    # Попробуем загрузить изображение, которое пользователь загружает
    image_path = "prava_obr-1.jpg"  # Из скриншота видно это имя файла
    
    try:
        # Попробуем найти изображение
        if Path(image_path).exists():
            image = Image.open(image_path)
            print(f"✅ Загружено изображение: {image_path}")
        else:
            # Создадим тестовое изображение водительских прав
            print("⚠️ Создаем тестовое изображение...")
            from PIL import ImageDraw, ImageFont
            
            image = Image.new('RGB', (600, 400), color='white')
            draw = ImageDraw.Draw(image)
            
            try:
                font = ImageFont.truetype("arial.ttf", 16)
                title_font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            # Текст как на водительских правах
            draw.text((50, 30), "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ", fill='black', font=title_font)
            draw.text((50, 70), "1. ВАКАРИНЦЕВ", fill='black', font=font)
            draw.text((50, 95), "2. АНДРЕЙ ПАВЛОВИЧ", fill='black', font=font)
            draw.text((50, 120), "3. 13.09.1995", fill='black', font=font)
            draw.text((50, 145), "4а) 03.01.2014  4b) 03.01.2024", fill='black', font=font)
            draw.text((50, 170), "4c) ГИБДД 2747", fill='black', font=font)
            draw.text((50, 195), "5. 0166860", fill='black', font=font)
            draw.text((50, 220), "8. АЛТАЙСКИЙ КРАЙ", fill='black', font=font)
            
            image.save("test_real_image.png")
            print("✅ Создано тестовое изображение: test_real_image.png")
        
        print(f"📊 Размер изображения: {image.size}")
        print(f"📊 Режим: {image.mode}")
        
        # Тест с got_ocr_hf (как в интерфейсе)
        selected_model = "got_ocr_hf"
        
        print(f"\n🚀 Тест модели {selected_model}...")
        start_time = time.time()
        
        # Загрузка модели
        model = ModelLoader.load_model(selected_model)
        load_time = time.time() - start_time
        print(f"✅ Модель загружена за {load_time:.2f}с")
        
        # Обработка (точно как в интерфейсе)
        start_time = time.time()
        
        if hasattr(model, 'extract_text'):
            print("   Используем extract_text")
            text = model.extract_text(image)
        elif hasattr(model, 'process_image'):
            print("   Используем process_image")
            text = model.process_image(image)
        else:
            print("   Используем chat")
            text = model.chat(image, "Извлеките весь текст из этого документа, сохраняя структуру и форматирование.")
        
        processing_time = time.time() - start_time
        
        print(f"✅ Обработка за {processing_time:.2f}с")
        
        # Анализ результата
        print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТА:")
        print(f"   Тип: {type(text)}")
        print(f"   Длина: {len(text)} символов")
        print(f"   Пустой: {not text or text.strip() == ''}")
        print(f"   Только RUS: {'RUS' in text and len(text.strip()) < 10}")
        
        # Показать результат
        print(f"\n📄 ПОЛНЫЙ РЕЗУЛЬТАТ:")
        print("=" * 50)
        print(repr(text))
        print("=" * 50)
        print(text)
        print("=" * 50)
        
        # Вычисление уверенности (как в интерфейсе)
        confidence = min(0.95, max(0.7, len(text.strip()) / 100))
        print(f"\n📊 Уверенность: {confidence:.1%}")
        
        # Выгрузка
        ModelLoader.unload_model(selected_model)
        print("\n🔄 Модель выгружена")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_with_real_image()
    sys.exit(0 if success else 1)