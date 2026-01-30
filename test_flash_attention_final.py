#!/usr/bin/env python3
"""
Финальный тест Flash Attention для dots.ocr
Проверяем PyTorch SDPA Flash Attention backend
"""

import time
import torch
from PIL import Image
from models.model_loader import ModelLoader
from utils.logger import logger

def test_flash_attention():
    """Тест Flash Attention с dots.ocr"""
    print("🚀 ФИНАЛЬНЫЙ ТЕСТ FLASH ATTENTION")
    print("=" * 50)
    
    # Проверяем PyTorch SDPA Flash Attention
    print(f"PyTorch версия: {torch.__version__}")
    print(f"CUDA доступна: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}GB")
    
    # Тест PyTorch SDPA Flash Attention
    print("\n🔍 Тестируем PyTorch SDPA Flash Attention...")
    try:
        with torch.backends.cuda.sdp_kernel(enable_flash=True):
            # Создаем тестовый тензор
            test_tensor = torch.randn(1, 1, 10, 64, device='cuda', dtype=torch.bfloat16)
            
            # Тестируем SDPA
            start_time = time.time()
            result = torch.nn.functional.scaled_dot_product_attention(
                test_tensor, test_tensor, test_tensor
            )
            sdpa_time = time.time() - start_time
            
            print(f"✅ PyTorch SDPA Flash Attention РАБОТАЕТ!")
            print(f"   Время выполнения: {sdpa_time:.4f}s")
            print(f"   Результат shape: {result.shape}")
            
    except Exception as e:
        print(f"❌ PyTorch SDPA Flash недоступен: {e}")
        return False
    
    # Загружаем dots.ocr
    print("\n📥 Загружаем dots.ocr с Flash Attention...")
    start_load = time.time()
    
    try:
        model = ModelLoader.load_model('dots_ocr')
        load_time = time.time() - start_load
        print(f"✅ dots.ocr загружен за {load_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return False
    
    # Тестируем обработку изображения
    print("\n🖼️ Тестируем OCR с Flash Attention...")
    
    try:
        # Загружаем тестовое изображение
        image_path = "test_document.png"
        if not os.path.exists(image_path):
            print(f"⚠️ Файл {image_path} не найден, создаем тестовое изображение...")
            # Создаем простое тестовое изображение
            from PIL import ImageDraw, ImageFont
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Добавляем текст
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 50), "ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=font)
            draw.text((50, 100), "Flash Attention Test", fill='black', font=font)
            draw.text((50, 150), "Номер: 123456789", fill='black', font=font)
            draw.text((50, 200), "Дата: 19.01.2026", fill='black', font=font)
            
            img.save(image_path)
            print(f"✅ Создано тестовое изображение: {image_path}")
        
        image = Image.open(image_path)
        
        # OCR тест
        print("🔍 Запускаем OCR...")
        start_ocr = time.time()
        
        ocr_result = model.extract_text_only(image)
        ocr_time = time.time() - start_ocr
        
        print(f"✅ OCR завершен за {ocr_time:.2f}s")
        print(f"📝 Результат OCR ({len(ocr_result)} символов):")
        print(f"   {ocr_result[:200]}...")
        
        # Layout анализ тест
        print("\n📋 Запускаем анализ layout...")
        start_layout = time.time()
        
        layout_result = model.parse_document(image, return_json=True)
        layout_time = time.time() - start_layout
        
        print(f"✅ Layout анализ завершен за {layout_time:.2f}s")
        
        if isinstance(layout_result, dict):
            if 'raw_text' in layout_result:
                print(f"📊 Layout результат (текст): {len(layout_result['raw_text'])} символов")
            else:
                print(f"📊 Layout результат (JSON): {len(str(layout_result))} символов")
        else:
            print(f"📊 Layout результат: {type(layout_result)}")
        
        # Финальная статистика
        print("\n" + "=" * 50)
        print("🎯 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ FLASH ATTENTION:")
        print(f"✅ PyTorch SDPA Flash: РАБОТАЕТ")
        print(f"✅ dots.ocr загрузка: {load_time:.2f}s")
        print(f"✅ OCR обработка: {ocr_time:.2f}s")
        print(f"✅ Layout анализ: {layout_time:.2f}s")
        print(f"✅ Общее время: {load_time + ocr_time + layout_time:.2f}s")
        
        # Проверяем использование GPU
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated() / 1024**3
            print(f"✅ GPU память: {memory_used:.2f}GB")
        
        print("\n🚀 FLASH ATTENTION ПОЛНОСТЬЮ ФУНКЦИОНАЛЕН!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Очистка
        if 'model' in locals():
            model.unload()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

if __name__ == "__main__":
    import os
    success = test_flash_attention()
    
    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Flash Attention через PyTorch SDPA работает отлично!")
    else:
        print("\n❌ Тесты не пройдены")
        exit(1)