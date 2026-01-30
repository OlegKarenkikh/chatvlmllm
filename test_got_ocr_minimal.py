#!/usr/bin/env python3
"""
Минимальный тест got_ocr_hf с принудительным ограничением
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_minimal_document():
    """Создаем минимальный документ для OCR"""
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), "TEST DOC", fill='black', font=font)
    draw.text((10, 30), "ID: 12345", fill='black', font=font)
    draw.text((10, 50), "OK", fill='black', font=font)
    
    return img

def test_got_ocr_minimal():
    """Минимальный тест got_ocr_hf"""
    print("🚀 МИНИМАЛЬНЫЙ ТЕСТ GOT-OCR HF")
    print("=" * 40)
    
    try:
        from transformers import AutoProcessor, AutoModelForImageTextToText
        
        print("📥 Загружаем модель напрямую...")
        start_time = time.time()
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"✅ Устройство: {device}")
        
        # Загружаем модель напрямую (как в официальной документации)
        model = AutoModelForImageTextToText.from_pretrained(
            "stepfun-ai/GOT-OCR-2.0-hf", 
            device_map=device,
            torch_dtype=torch.float16
        )
        processor = AutoProcessor.from_pretrained("stepfun-ai/GOT-OCR-2.0-hf")
        
        load_time = time.time() - start_time
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Создаем минимальное изображение
        print("🖼️ Создаем минимальный документ...")
        image = create_minimal_document()
        
        # Обрабатываем с минимальными параметрами
        print("🔍 Выполняем OCR с минимальными параметрами...")
        start_process = time.time()
        
        inputs = processor(image, return_tensors="pt").to(device)
        
        # МИНИМАЛЬНЫЕ параметры генерации
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=50,  # ОЧЕНЬ МАЛО токенов
                num_beams=1,
                early_stopping=True,
                pad_token_id=processor.tokenizer.eos_token_id,
                eos_token_id=processor.tokenizer.eos_token_id,
            )
        
        result = processor.decode(
            generated_ids[0, inputs["input_ids"].shape[1]:], 
            skip_special_tokens=True
        )
        
        process_time = time.time() - start_process
        
        print(f"✅ OCR завершен за {process_time:.3f}s")
        print(f"📝 Результат ({len(result)} символов): {result}")
        
        # Проверяем качество
        keywords = ["TEST", "DOC", "12345", "OK"]
        found = sum(1 for kw in keywords if kw in result.upper())
        quality = (found / len(keywords)) * 100
        
        print(f"🎯 Качество: {found}/{len(keywords)} слов ({quality:.1f}%)")
        
        # Очищаем память
        del model
        del processor
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print(f"🎉 ТЕСТ ЗАВЕРШЕН")
        print(f"⚡ Время: загрузка {load_time:.2f}s, обработка {process_time:.3f}s")
        
        return quality >= 50
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_got_ocr_minimal()
    print(f"\n{'✅ УСПЕХ' if success else '❌ НЕУДАЧА'}")
    exit(0 if success else 1)