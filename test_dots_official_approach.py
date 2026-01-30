#!/usr/bin/env python3
"""
Тест dots.ocr с официальным подходом из документации
"""

import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from PIL import Image
import time

def test_official_dots_approach():
    """Тест с официальным подходом dots.ocr"""
    print("🧪 ТЕСТ ОФИЦИАЛЬНОГО ПОДХОДА DOTS.OCR")
    print("=" * 50)
    
    # Информация о системе
    print(f"🖥️ GPU: {torch.cuda.get_device_name(0)}")
    print(f"🐍 PyTorch: {torch.__version__}")
    print(f"⚡ CUDA: {torch.version.cuda}")
    print()
    
    try:
        # Загрузка модели (официальный способ)
        print("🔄 Загружаем dots.ocr (официальный способ)...")
        start_time = time.time()
        
        model = AutoModelForCausalLM.from_pretrained(
            "rednote-hilab/dots.ocr",
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        
        processor = AutoProcessor.from_pretrained(
            "rednote-hilab/dots.ocr",
            trust_remote_code=True
        )
        
        load_time = time.time() - start_time
        print(f"✅ Модель загружена за {load_time:.2f}s")
        print()
        
        # Тест с простым изображением
        print("🔍 Тестируем с простым изображением...")
        
        # Создаем простое изображение с текстом
        image = Image.new('RGB', (400, 100), color='white')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 30), "HELLO WORLD", fill='black', font=font)
        image.save('test_simple_hello.png')
        
        # Официальный способ обработки
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": "Extract all text from this image"}
                ]
            }
        ]
        
        # Применение chat template
        text = processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        print(f"📝 Chat template: {text[:200]}...")
        
        # Подготовка входных данных
        inputs = processor(
            text=[text],
            images=[image],
            padding=True,
            return_tensors="pt"
        ).to("cuda")
        
        print(f"🔧 Input shape: {inputs.input_ids.shape}")
        print(f"🖼️ Image tensor shape: {inputs.pixel_values.shape if hasattr(inputs, 'pixel_values') else 'No pixel_values'}")
        
        # Генерация (минимальные параметры)
        print("🚀 Генерируем ответ...")
        start_gen = time.time()
        
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
                pad_token_id=processor.tokenizer.eos_token_id
            )
        
        gen_time = time.time() - start_gen
        print(f"⏱️ Генерация заняла: {gen_time:.3f}s")
        
        # Декодирование
        generated_ids_trimmed = [
            out_ids[len(in_ids):] 
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )[0]
        
        print(f"📋 Результат: '{output_text}'")
        print(f"📏 Длина: {len(output_text)} символов")
        
        if output_text.strip():
            print("✅ УСПЕХ! dots.ocr работает")
            return True
        else:
            print("❌ Пустой результат")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_prompts():
    """Тест с разными промптами"""
    print("\n🧪 ТЕСТ РАЗНЫХ ПРОМПТОВ")
    print("=" * 30)
    
    try:
        model = AutoModelForCausalLM.from_pretrained(
            "rednote-hilab/dots.ocr",
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        
        processor = AutoProcessor.from_pretrained(
            "rednote-hilab/dots.ocr",
            trust_remote_code=True
        )
        
        # Простое изображение
        image = Image.open('test_simple_hello.png')
        
        # Разные промпты
        prompts = [
            "OCR",
            "Read text",
            "What text is in this image?",
            "Extract all text",
            "Transcribe the text in the image"
        ]
        
        for prompt in prompts:
            print(f"\n🔍 Промпт: '{prompt}'")
            
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }]
            
            text = processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            inputs = processor(
                text=[text],
                images=[image],
                padding=True,
                return_tensors="pt"
            ).to("cuda")
            
            with torch.no_grad():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    do_sample=False,
                    pad_token_id=processor.tokenizer.eos_token_id
                )
            
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            print(f"📝 Результат: '{output_text.strip()}'")
            
            if "HELLO" in output_text.upper():
                print("✅ Текст найден!")
            else:
                print("❌ Текст не найден")
                
    except Exception as e:
        print(f"❌ Ошибка в тесте промптов: {e}")

if __name__ == "__main__":
    success = test_official_dots_approach()
    
    if success:
        test_different_prompts()
        print("\n🎉 DOTS.OCR РАБОТАЕТ С ОФИЦИАЛЬНЫМ ПОДХОДОМ!")
    else:
        print("\n❌ DOTS.OCR НЕ РАБОТАЕТ ДАЖЕ С ОФИЦИАЛЬНЫМ ПОДХОДОМ")
        print("💡 Возможные причины:")
        print("   - Несовместимость версий PyTorch/transformers")
        print("   - Проблемы с CUDA/flash-attention")
        print("   - Неправильная модель или процессор")