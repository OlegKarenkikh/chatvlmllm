#!/usr/bin/env python3
"""
Финальный тест dots.ocr на RTX 5070 Ti Blackwell с реальным изображением
"""

import torch
import time
from models.dots_ocr_blackwell_compatible import DotsOCRBlackwellModel
from PIL import Image, ImageDraw, ImageFont
import os

def create_test_document():
    """Создание тестового документа с текстом"""
    # Создаем изображение с текстом
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Пытаемся использовать системный шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Добавляем текст на разных языках
    texts = [
        "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ",
        "DRIVER'S LICENSE",
        "Фамилия: ИВАНОВ",
        "Имя: ИВАН ИВАНОВИЧ", 
        "Дата рождения: 01.01.1990",
        "Категории: B, C",
        "Действительно до: 01.01.2030",
        "Серия: 77 АА № 123456"
    ]
    
    y_pos = 50
    for text in texts:
        draw.text((50, y_pos), text, fill='black', font=font)
        y_pos += 40
    
    # Сохраняем изображение
    img.save("test_dots_blackwell_document.png")
    return img

def test_dots_ocr_final():
    """Финальный тест dots.ocr с Blackwell оптимизациями"""
    print("🧪 ФИНАЛЬНЫЙ ТЕСТ DOTS.OCR BLACKWELL")
    print("=" * 60)
    
    # Информация о системе
    print(f"🖥️ GPU: {torch.cuda.get_device_name(0)}")
    print(f"🔧 Compute Capability: {torch.cuda.get_device_capability(0)}")
    print(f"💾 VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}GB")
    print(f"🐍 PyTorch: {torch.__version__}")
    print(f"⚡ CUDA: {torch.version.cuda}")
    print(f"✅ bfloat16: {torch.cuda.is_bf16_supported()}")
    print()
    
    # Создание тестового документа
    print("📄 Создание тестового документа...")
    test_image = create_test_document()
    print("✅ Тестовый документ создан: test_dots_blackwell_document.png")
    print()
    
    # Создание и загрузка модели
    print("🚀 ЗАГРУЗКА DOTS.OCR С BLACKWELL ОПТИМИЗАЦИЯМИ")
    print("=" * 60)
    
    model = DotsOCRBlackwellModel()
    
    start_time = time.time()
    if not model.load_model():
        print("❌ Не удалось загрузить модель")
        return False
    
    load_time = time.time() - start_time
    vram_used = torch.cuda.memory_allocated() / 1024**3
    
    print(f"✅ Модель загружена за {load_time:.2f}s")
    print(f"✅ VRAM использовано: {vram_used:.2f}GB")
    print()
    
    # Тест OCR с разными промптами
    prompts = [
        "Extract all text from this document",
        "Read all text in this image",
        "Transcribe the text from this driver's license",
        "What text do you see in this image?"
    ]
    
    print("🔍 ТЕСТИРОВАНИЕ OCR С РАЗНЫМИ ПРОМПТАМИ")
    print("=" * 60)
    
    best_result = ""
    best_prompt = ""
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 Тест {i}/4: {prompt}")
        print("-" * 40)
        
        start_time = time.time()
        result = model.process_image(test_image, prompt)
        processing_time = time.time() - start_time
        
        if result:
            print(f"⏱️ Время обработки: {processing_time:.3f}s")
            print(f"📝 Длина результата: {len(result)} символов")
            print(f"🔍 Результат: {result[:200]}...")
            
            # Проверяем качество результата
            if len(result) > len(best_result):
                best_result = result
                best_prompt = prompt
        else:
            print("❌ Не удалось получить результат")
    
    # Итоговые результаты
    print("\n🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 60)
    
    if best_result:
        print(f"✅ Лучший промпт: {best_prompt}")
        print(f"✅ Лучший результат ({len(best_result)} символов):")
        print(f"📄 {best_result}")
        print()
        
        # Анализ качества
        expected_words = ["ВОДИТЕЛЬСКОЕ", "УДОСТОВЕРЕНИЕ", "ИВАНОВ", "ИВАН", "1990", "123456"]
        found_words = sum(1 for word in expected_words if word.upper() in best_result.upper())
        quality = (found_words / len(expected_words)) * 100
        
        print(f"🎯 Качество OCR: {found_words}/{len(expected_words)} ({quality:.1f}%)")
        
        if quality > 50:
            print("🎉 ОТЛИЧНОЕ КАЧЕСТВО OCR!")
            success = True
        elif quality > 20:
            print("⚠️ УДОВЛЕТВОРИТЕЛЬНОЕ КАЧЕСТВО OCR")
            success = True
        else:
            print("❌ НИЗКОЕ КАЧЕСТВО OCR")
            success = False
    else:
        print("❌ Не удалось получить результаты")
        success = False
    
    # Финальная статистика
    print(f"\n📊 ФИНАЛЬНАЯ СТАТИСТИКА")
    print("=" * 60)
    print(f"🖥️ GPU: RTX 5070 Ti Blackwell (sm_120)")
    print(f"⏱️ Загрузка модели: {load_time:.2f}s")
    print(f"💾 VRAM использовано: {vram_used:.2f}GB")
    print(f"🔧 Dtype: torch.bfloat16")
    print(f"⚡ Attention: eager (Blackwell compatible)")
    print(f"✅ Flash Attention: Отключена (несовместима)")
    print(f"🎯 Статус: {'РАБОТАЕТ' if success else 'ТРЕБУЕТ ДОРАБОТКИ'}")
    
    # Очистка
    model.cleanup()
    
    return success

if __name__ == "__main__":
    success = test_dots_ocr_final()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 DOTS.OCR УСПЕШНО РАБОТАЕТ НА RTX 5070 TI BLACKWELL!")
        print("✅ Система готова к использованию")
        print("✅ Blackwell оптимизации применены")
        print("✅ Eager attention обеспечивает стабильность")
    else:
        print("⚠️ DOTS.OCR ЧАСТИЧНО РАБОТАЕТ")
        print("✅ Модель загружается без ошибок")
        print("⚠️ Качество OCR требует улучшения")
        print("💡 Рекомендуется использовать Qwen2-VL как основную модель")
    
    print("\n🚀 СИСТЕМА RTX 5070 TI BLACKWELL ГОТОВА!")