#!/usr/bin/env python3
"""
Быстрый тест dots.ocr без flash attention
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


def test_dots_without_flash_attention():
    """Тест dots.ocr без flash attention."""
    
    print("🔧 ТЕСТ DOTS.OCR БЕЗ FLASH ATTENTION")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Load model
        print("📥 Загрузка модели dots.ocr...")
        model_wrapper = ModelLoader.load_model('dots_ocr')
        
        load_time = time.time() - start_time
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Check flash attention status
        try:
            import flash_attn
            print("✅ Flash Attention доступен")
        except ImportError:
            print("⚠️ Flash Attention НЕ установлен - используем eager")
        
        # Test with simple image
        image_path = "test_document.png"
        if not Path(image_path).exists():
            print(f"❌ Файл {image_path} не найден")
            return
        
        image = Image.open(image_path)
        print(f"📷 Изображение загружено: {image.size}")
        
        # Test OCR mode
        print("\n🔤 Тест OCR режима...")
        ocr_start = time.time()
        
        try:
            result = model_wrapper.extract_text_only(image)
            ocr_time = time.time() - ocr_start
            
            print(f"✅ OCR завершен за {ocr_time:.2f}s")
            print(f"📝 Результат: {len(str(result))} символов")
            
            if isinstance(result, str) and len(result) > 10:
                print("✅ OCR работает корректно!")
            else:
                print(f"⚠️ Результат: {result}")
                
        except Exception as e:
            print(f"❌ Ошибка OCR: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
        
        # Test layout analysis (quick)
        print("\n📋 Тест Layout анализа...")
        layout_start = time.time()
        
        try:
            result = model_wrapper.parse_document(image, return_json=True)
            layout_time = time.time() - layout_start
            
            print(f"✅ Layout анализ завершен за {layout_time:.2f}s")
            
            if isinstance(result, dict):
                print(f"📊 Тип результата: {type(result)}")
                if isinstance(result, list):
                    print(f"📊 Найдено элементов: {len(result)}")
                else:
                    print(f"📊 Ключи: {list(result.keys())}")
                print("✅ Layout анализ работает!")
            else:
                print(f"⚠️ Результат: {result}")
                
        except Exception as e:
            print(f"❌ Ошибка Layout: {e}")
        
        # Unload model
        ModelLoader.unload_model('dots_ocr')
        
        total_time = time.time() - start_time
        print(f"\n⏱️ Общее время теста: {total_time:.2f}s")
        print("✅ Тест завершен!")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    test_dots_without_flash_attention()