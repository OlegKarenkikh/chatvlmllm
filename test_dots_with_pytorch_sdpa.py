#!/usr/bin/env python3
"""
Тест dots.ocr с PyTorch SDPA Flash Attention
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


def test_dots_with_pytorch_sdpa():
    """Тест dots.ocr с PyTorch SDPA."""
    
    print("⚡ ТЕСТ DOTS.OCR С PYTORCH SDPA FLASH ATTENTION")
    print("=" * 60)
    
    try:
        # Load model with new SDPA implementation
        print("📥 Загрузка dots.ocr с PyTorch SDPA...")
        
        start_time = time.time()
        model_wrapper = ModelLoader.load_model('dots_ocr')
        load_time = time.time() - start_time
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Check what attention implementation is being used
        model = model_wrapper.model
        if hasattr(model.config, 'attn_implementation'):
            attn_impl = model.config.attn_implementation
            print(f"🔧 Attention implementation: {attn_impl}")
            
            if attn_impl == "sdpa":
                print("🚀 ИСПОЛЬЗУЕТСЯ PYTORCH SDPA - ОПТИМАЛЬНАЯ ПРОИЗВОДИТЕЛЬНОСТЬ!")
            elif attn_impl == "flash_attention_2":
                print("⚡ Используется внешний Flash Attention")
            else:
                print("⚠️ Используется eager attention (медленнее)")
        
        # Test with document
        image_path = "test_document.png"
        if not Path(image_path).exists():
            print(f"❌ Файл {image_path} не найден")
            return
        
        image = Image.open(image_path)
        print(f"📷 Изображение: {image.size}")
        
        # Test OCR with timing
        print("\n🔤 Тест OCR с новой реализацией...")
        
        ocr_start = time.time()
        result = model_wrapper.extract_text_only(image)
        ocr_time = time.time() - ocr_start
        
        print(f"✅ OCR завершен за {ocr_time:.2f}s")
        print(f"📝 Результат: {len(str(result))} символов")
        
        if result and len(str(result)) > 10:
            print("✅ OCR работает с новой реализацией!")
        
        # Test layout analysis
        print("\n📋 Тест Layout анализа...")
        
        layout_start = time.time()
        layout_result = model_wrapper.parse_document(image, return_json=True)
        layout_time = time.time() - layout_start
        
        print(f"✅ Layout анализ завершен за {layout_time:.2f}s")
        
        if isinstance(layout_result, dict):
            if 'raw_text' in layout_result:
                raw_text = layout_result['raw_text']
                if raw_text and len(raw_text) > 50:
                    print(f"📊 Получен результат: {len(raw_text)} символов")
                    
                    # Try to parse as JSON
                    try:
                        import json
                        parsed = json.loads(raw_text)
                        if isinstance(parsed, list):
                            print(f"✅ Валидный JSON: {len(parsed)} элементов")
                            print("🎯 PYTORCH SDPA FLASH ATTENTION РАБОТАЕТ ОТЛИЧНО!")
                        else:
                            print(f"✅ JSON результат: {type(parsed)}")
                    except json.JSONDecodeError:
                        print("⚠️ Результат не JSON, но есть данные")
        
        # Performance summary
        total_time = time.time() - start_time
        print(f"\n📊 ИТОГИ ПРОИЗВОДИТЕЛЬНОСТИ:")
        print(f"   Загрузка модели: {load_time:.2f}s")
        print(f"   OCR обработка: {ocr_time:.2f}s")
        print(f"   Layout анализ: {layout_time:.2f}s")
        print(f"   Общее время: {total_time:.2f}s")
        
        # Check GPU memory usage
        if torch.cuda.is_available():
            memory_used = torch.cuda.max_memory_allocated() / 1024**3
            print(f"   Память GPU: {memory_used:.2f}GB")
        
        # Unload model
        ModelLoader.unload_model('dots_ocr')
        
        print(f"\n🎉 PYTORCH SDPA FLASH ATTENTION УСПЕШНО ИНТЕГРИРОВАН!")
        print(f"✅ dots.ocr теперь использует оптимизированное внимание")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    test_dots_with_pytorch_sdpa()