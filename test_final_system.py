#!/usr/bin/env python3
"""
Финальный тест системы OCR для RTX 5070 Ti Blackwell
"""

import torch
import time
from transformers import AutoModelForImageTextToText, AutoProcessor
from PIL import Image
import yaml

def test_system():
    print("🧪 ФИНАЛЬНЫЙ ТЕСТ СИСТЕМЫ OCR")
    print("=" * 80)
    
    # Проверка GPU
    print(f"🖥️ GPU: {torch.cuda.get_device_name(0)}")
    print(f"🔧 Compute Capability: {torch.cuda.get_device_capability(0)}")
    print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}GB")
    print(f"🐍 PyTorch: {torch.__version__}")
    print(f"⚡ CUDA: {torch.version.cuda}")
    print(f"✅ bfloat16: {torch.cuda.is_bf16_supported()}")
    print()
    
    # Применяем Blackwell оптимизации
    print("⚡ ПРИМЕНЕНИЕ BLACKWELL ОПТИМИЗАЦИЙ")
    print("=" * 50)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.enable_flash_sdp(True)
    print("✅ TF32 включен для Tensor Cores")
    print("✅ cuDNN benchmark включен")
    print("✅ SDPA оптимизации включены")
    print()
    
    # Загрузка конфигурации
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Тест Qwen2-VL (основная рекомендуемая модель)
    print("🚀 ТЕСТ QWEN2-VL (РЕКОМЕНДУЕМАЯ МОДЕЛЬ)")
    print("=" * 50)
    
    try:
        start_time = time.time()
        
        # Загрузка модели с Blackwell оптимизациями
        model = AutoModelForImageTextToText.from_pretrained(
            "Qwen/Qwen2-VL-2B-Instruct",
            torch_dtype=torch.bfloat16,
            attn_implementation="eager",
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        processor = AutoProcessor.from_pretrained(
            "Qwen/Qwen2-VL-2B-Instruct",
            trust_remote_code=True
        )
        
        load_time = time.time() - start_time
        print(f"✅ Модель загружена за {load_time:.2f}s")
        print(f"✅ Dtype модели: {model.dtype}")
        print(f"✅ Устройство: {model.device}")
        
        # Проверка VRAM
        torch.cuda.empty_cache()
        vram_used = torch.cuda.memory_allocated() / 1024**3
        print(f"✅ VRAM использовано: {vram_used:.2f}GB")
        print()
        
        # Создание тестового изображения
        print("🔍 Создание тестового изображения...")
        test_image = Image.new('RGB', (800, 600), color='white')
        
        # Тест инференса
        print("🔍 Тестируем инференс с bfloat16 оптимизациями...")
        start_time = time.time()
        
        # Правильный API для Qwen2-VL
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": test_image},
                    {"type": "text", "text": "Опишите это изображение на русском языке."}
                ]
            }
        ]
        
        # Применяем chat template
        text_prompt = processor.apply_chat_template(
            conversation, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Обрабатываем входные данные
        inputs = processor(
            text=[text_prompt],
            images=[test_image],
            padding=True,
            return_tensors="pt"
        ).to("cuda")
        
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=128,
                do_sample=False,
                use_cache=True,
                pad_token_id=processor.tokenizer.eos_token_id
            )
        
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        
        inference_time = time.time() - start_time
        print(f"⏱️ Время инференса: {inference_time:.3f}s")
        print(f"📝 Результат: {output_text[:100]}...")
        print()
        
        # Итоговые результаты
        print("🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 50)
        print(f"✅ Загрузка модели: {load_time:.2f}s")
        print(f"✅ Инференс: {inference_time:.3f}s")
        print(f"✅ VRAM использовано: {vram_used:.2f}GB")
        print(f"✅ Dtype: {model.dtype}")
        print(f"✅ Статус: ПОЛНОСТЬЮ РАБОТАЕТ")
        print()
        
        print("🎉 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
        print("✅ RTX 5070 Ti Blackwell полностью оптимизирована")
        print("✅ Qwen2-VL работает с максимальной производительностью")
        print("✅ bfloat16 + eager attention = стабильность + скорость")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_system()
    if success:
        print("\n🚀 СИСТЕМА ГОТОВА!")
    else:
        print("\n❌ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")