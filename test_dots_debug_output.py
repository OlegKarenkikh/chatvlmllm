#!/usr/bin/env python3
"""
Отладка вывода dots.ocr
"""

import os
import sys
import time
import torch
from pathlib import Path
from PIL import Image

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Set environment variable
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from models.model_loader import ModelLoader
from utils.logger import logger


def debug_dots_output():
    """Отладка вывода dots.ocr."""
    
    print("🔍 ОТЛАДКА ВЫВОДА DOTS.OCR")
    print("=" * 40)
    
    try:
        # Load model
        print("📥 Загрузка модели...")
        model_wrapper = ModelLoader.load_model('dots_ocr')
        
        # Get the actual model and processor
        model = model_wrapper.model
        processor = model_wrapper.processor
        
        print("✅ Модель загружена")
        
        # Test with simple image
        image_path = "test_document.png"
        if not Path(image_path).exists():
            print(f"❌ Файл {image_path} не найден")
            return
        
        image = Image.open(image_path)
        print(f"📷 Изображение: {image.size}, режим: {image.mode}")
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
            print("🔄 Конвертировано в RGB")
        
        # Test simple prompt
        simple_prompt = "Extract all text from this image."
        print(f"\n📝 Тестируем простой промпт: {simple_prompt}")
        
        # Manual inference like in Modal
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": simple_prompt}
                ]
            }
        ]
        
        print("🔧 Подготовка inference...")
        
        # Preparation for inference
        text = processor.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        print(f"📄 Chat template: {text[:200]}...")
        
        # Process vision info
        from qwen_vl_utils import process_vision_info
        image_inputs, video_inputs = process_vision_info(messages)
        
        print(f"🖼️ Image inputs: {len(image_inputs) if image_inputs else 0}")
        print(f"🎥 Video inputs: {len(video_inputs) if video_inputs else 0}")
        
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        
        inputs = inputs.to("cuda")
        print("✅ Inputs подготовлены и перенесены на GPU")
        
        # Generate with detailed settings
        print("🚀 Запуск генерации...")
        
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs, 
                max_new_tokens=1000,  # Уменьшено для отладки
                do_sample=False,
                temperature=1.0,
                pad_token_id=processor.tokenizer.eos_token_id
            )
        
        print("✅ Генерация завершена")
        
        # Decode output
        generated_ids_trimmed = [
            out_ids[len(in_ids):] 
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        (output_text,) = processor.batch_decode(
            generated_ids_trimmed, 
            skip_special_tokens=True, 
            clean_up_tokenization_spaces=False
        )
        
        print(f"\n📤 RAW OUTPUT:")
        print(f"Длина: {len(output_text)}")
        print(f"Содержимое: '{output_text}'")
        print(f"Repr: {repr(output_text)}")
        
        if output_text.strip():
            print("✅ Модель генерирует текст!")
            
            # Try to parse as JSON
            try:
                import json
                parsed = json.loads(output_text)
                print(f"✅ Валидный JSON: {type(parsed)}")
                if isinstance(parsed, list):
                    print(f"📊 Элементов: {len(parsed)}")
                elif isinstance(parsed, dict):
                    print(f"📊 Ключи: {list(parsed.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ Не JSON: {e}")
                print("💡 Возможно, нужен другой промпт")
        else:
            print("❌ Пустой вывод!")
            print("💡 Проблема с промптом или изображением")
        
        # Unload model
        ModelLoader.unload_model('dots_ocr')
        print("\n✅ Отладка завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    debug_dots_output()