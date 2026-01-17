#!/usr/bin/env python3
"""Тест dots.ocr по официальному примеру."""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import torch

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))


def test_dots_official():
    """Тест по официальному примеру."""
    print("🧪 ТЕСТ DOTS.OCR ПО ОФИЦИАЛЬНОМУ ПРИМЕРУ")
    print("=" * 50)
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, AutoImageProcessor
        
        # Создание тестового изображения
        image = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(image)
        draw.text((50, 50), "TEST DOCUMENT", fill='black')
        draw.text((50, 100), "Line 1: Important information", fill='black')
        draw.text((50, 130), "Line 2: More data here", fill='black')
        
        print("✅ Тестовое изображение создано")
        
        model_path = "rednote-hilab/dots.ocr"
        
        # Загрузка компонентов
        print("🚀 Загрузка модели...")
        
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        print("✅ Токенизатор загружен")
        
        try:
            image_processor = AutoImageProcessor.from_pretrained(model_path, trust_remote_code=True)
            print("✅ Image processor загружен")
        except Exception as e:
            print(f"⚠️ Ошибка image processor: {e}")
            # Попробуем Qwen2VLImageProcessor
            from transformers import Qwen2VLImageProcessor
            image_processor = Qwen2VLImageProcessor.from_pretrained(model_path)
            print("✅ Qwen2VL Image processor загружен")
        
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
            attn_implementation="eager"  # Отключаем Flash Attention
        )
        print("✅ Модель загружена")
        
        # Подготовка входных данных
        print("\n🔍 Подготовка входных данных...")
        
        # Промпт
        prompt = "Please output the layout information from the PDF image, including bbox, category, and text."
        
        # Обработка изображения
        try:
            image_inputs = image_processor(image, return_tensors="pt")
            print(f"✅ Image inputs: {list(image_inputs.keys())}")
            
            for key, value in image_inputs.items():
                if torch.is_tensor(value):
                    print(f"   {key}: {value.shape}")
                else:
                    print(f"   {key}: {type(value)}")
        except Exception as e:
            print(f"❌ Ошибка обработки изображения: {e}")
            return False
        
        # Обработка текста
        text_inputs = tokenizer(prompt, return_tensors="pt")
        print(f"✅ Text inputs: {list(text_inputs.keys())}")
        
        # Объединение входных данных
        inputs = {
            **text_inputs,
            **image_inputs
        }
        
        # Перемещение на устройство
        device = next(model.parameters()).device
        inputs = {k: v.to(device) if torch.is_tensor(v) else v for k, v in inputs.items()}
        
        print(f"✅ Входные данные подготовлены, устройство: {device}")
        
        # Генерация
        print("\n🚀 Генерация...")
        
        try:
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=1000,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Декодирование
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            print("✅ Генерация успешна!")
            print(f"📊 Результат ({len(generated_text)} символов):")
            print("-" * 40)
            print(generated_text[:500] + "..." if len(generated_text) > 500 else generated_text)
            print("-" * 40)
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_dots_official()
    sys.exit(0 if success else 1)