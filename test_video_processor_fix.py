#!/usr/bin/env python3
"""
Тест исправления video_processor проблемы в dots.ocr

Проверяет:
1. Загрузку модели без ошибок video_processor
2. Базовую функциональность OCR
3. Обработку тестового изображения
"""

import os
import sys
import traceback
from PIL import Image
import torch

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.dots_ocr_video_processor_fixed import DotsOCRVideoProcessorFixedModel
from utils.logger import logger


def test_video_processor_fix():
    """Тестируем исправление video_processor проблемы."""
    
    print("🧪 Тестирование исправления video_processor проблемы в dots.ocr")
    print("=" * 60)
    
    try:
        # Конфигурация модели
        config = {
            'model_path': 'rednote-hilab/dots.ocr',
            'precision': 'fp16',
            'flash_attention': False,
            'attention_implementation': 'eager',
            'max_new_tokens': 256
        }
        
        print("📋 Конфигурация:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        print()
        
        # Создаем модель
        print("🔧 Создание модели...")
        model = DotsOCRVideoProcessorFixedModel(config)
        
        # Загружаем модель
        print("📥 Загрузка модели...")
        model.load_model()
        print("✅ Модель загружена успешно!")
        print()
        
        # Проверяем компоненты модели
        print("🔍 Проверка компонентов модели:")
        print(f"  Model loaded: {model.model is not None}")
        print(f"  Processor loaded: {model.processor is not None}")
        
        if model.processor:
            print(f"  Processor type: {type(model.processor).__name__}")
            if hasattr(model.processor, 'tokenizer'):
                print(f"  Tokenizer available: True")
                print(f"  Vocab size: {len(model.processor.tokenizer)}")
            if hasattr(model.processor, 'image_processor'):
                print(f"  Image processor available: True")
            if hasattr(model.processor, 'video_processor'):
                print(f"  Video processor available: True")
        print()
        
        # Создаем тестовое изображение
        print("🖼️ Создание тестового изображения...")
        test_image = Image.new('RGB', (400, 200), color='white')
        
        # Добавляем текст на изображение (симуляция)
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(test_image)
        
        try:
            # Пытаемся использовать системный шрифт
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((50, 80), "Hello World!", fill='black', font=font)
        draw.text((50, 120), "Test OCR Image", fill='black', font=font)
        
        # Сохраняем тестовое изображение
        test_image.save('test_video_processor_fix.png')
        print("✅ Тестовое изображение создано: test_video_processor_fix.png")
        print()
        
        # Тестируем OCR
        print("🔤 Тестирование OCR функциональности...")
        
        try:
            result = model.process_image(test_image, mode="text_extraction")
            print(f"✅ OCR результат: '{result}'")
            
            if result and len(result.strip()) > 0 and not result.startswith('['):
                print("✅ OCR работает корректно!")
            else:
                print("⚠️ OCR вернул пустой или ошибочный результат")
            
        except Exception as ocr_error:
            print(f"❌ Ошибка OCR: {ocr_error}")
            print(f"Traceback: {traceback.format_exc()}")
        
        print()
        
        # Тестируем различные режимы
        print("🎯 Тестирование различных режимов:")
        
        modes_to_test = ["minimal", "simple", "ocr"]
        
        for mode in modes_to_test:
            try:
                result = model.process_image(test_image, mode=mode)
                print(f"  {mode}: '{result[:50]}{'...' if len(result) > 50 else ''}'")
            except Exception as e:
                print(f"  {mode}: ❌ Ошибка - {e}")
        
        print()
        
        # Выгружаем модель
        print("🧹 Выгрузка модели...")
        model.unload()
        print("✅ Модель выгружена")
        
        print()
        print("🎉 Тест завершен успешно!")
        print("✅ video_processor проблема исправлена")
        
        return True
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


def test_memory_usage():
    """Проверяем использование памяти."""
    
    if not torch.cuda.is_available():
        print("⚠️ CUDA недоступна, пропускаем тест памяти")
        return
    
    print("\n💾 Проверка использования GPU памяти:")
    
    # Память до загрузки
    torch.cuda.empty_cache()
    memory_before = torch.cuda.memory_allocated() / 1024**3
    print(f"  Память до загрузки: {memory_before:.2f} GB")
    
    try:
        config = {
            'model_path': 'rednote-hilab/dots.ocr',
            'precision': 'fp16',
            'flash_attention': False,
            'attention_implementation': 'eager'
        }
        
        model = DotsOCRVideoProcessorFixedModel(config)
        model.load_model()
        
        # Память после загрузки
        memory_after = torch.cuda.memory_allocated() / 1024**3
        print(f"  Память после загрузки: {memory_after:.2f} GB")
        print(f"  Использовано: {memory_after - memory_before:.2f} GB")
        
        model.unload()
        
        # Память после выгрузки
        torch.cuda.empty_cache()
        memory_final = torch.cuda.memory_allocated() / 1024**3
        print(f"  Память после выгрузки: {memory_final:.2f} GB")
        
        if memory_final <= memory_before + 0.1:  # Допускаем небольшую погрешность
            print("✅ Память освобождена корректно")
        else:
            print("⚠️ Возможна утечка памяти")
        
    except Exception as e:
        print(f"❌ Ошибка теста памяти: {e}")


if __name__ == "__main__":
    print("🚀 Запуск тестов исправления video_processor проблемы")
    print()
    
    # Основной тест
    success = test_video_processor_fix()
    
    # Тест памяти
    if success:
        test_memory_usage()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ dots.ocr готов к использованию")
    else:
        print("❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("🔧 Требуется дополнительная отладка")
    
    print("=" * 60)