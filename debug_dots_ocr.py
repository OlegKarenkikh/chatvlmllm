#!/usr/bin/env python3
"""Отладка модели dots.ocr."""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import torch

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def debug_dots_ocr():
    """Отладка dots.ocr."""
    print("🔍 ОТЛАДКА DOTS.OCR")
    print("=" * 40)
    
    try:
        # Создание простого изображения
        image = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(image)
        draw.text((50, 50), "TEST TEXT", fill='black')
        draw.text((50, 100), "Тестовый текст", fill='black')
        
        print("✅ Тестовое изображение создано")
        
        # Загрузка модели
        model = ModelLoader.load_model("dots_ocr")
        print("✅ Модель загружена")
        
        # Отладка процессора
        print("\n🔍 Отладка процессора...")
        
        if isinstance(model.processor, dict):
            print("📝 Используется fallback процессор")
            tokenizer = model.processor['tokenizer']
            image_processor = model.processor['image_processor']
            
            # Тест токенизатора
            text = "Extract all text from this image..."
            text_inputs = tokenizer(text, return_tensors="pt")
            print(f"✅ Токенизатор: input_ids shape = {text_inputs['input_ids'].shape}")
            
            # Тест обработчика изображений
            try:
                image_inputs = image_processor(image, return_tensors="pt")
                print(f"✅ Image processor результат: {type(image_inputs)}")
                if image_inputs:
                    for key, value in image_inputs.items():
                        if torch.is_tensor(value):
                            print(f"   {key}: {value.shape if value is not None else 'None'}")
                        else:
                            print(f"   {key}: {type(value)}")
                else:
                    print("❌ Image processor вернул None")
            except Exception as e:
                print(f"❌ Ошибка image processor: {e}")
                
        else:
            print("📝 Используется стандартный процессор")
            
            # Тест стандартного процессора
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": "Extract text"}
                ]
            }]
            
            try:
                text = model.processor.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                print(f"✅ Chat template: {len(text)} символов")
                
                # Тест обработки изображения
                try:
                    inputs = model.processor(
                        text=[text],
                        images=[image],
                        padding=True,
                        return_tensors="pt"
                    )
                    print(f"✅ Processor результат: {type(inputs)}")
                    if inputs:
                        for key, value in inputs.items():
                            if torch.is_tensor(value):
                                print(f"   {key}: {value.shape if value is not None else 'None'}")
                            else:
                                print(f"   {key}: {type(value)}")
                    else:
                        print("❌ Processor вернул None")
                        
                except Exception as e:
                    print(f"❌ Ошибка processor: {e}")
                    
            except Exception as e:
                print(f"❌ Ошибка chat template: {e}")
        
        # Выгрузка
        ModelLoader.unload_model("dots_ocr")
        print("\n🔄 Модель выгружена")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_dots_ocr()