#!/usr/bin/env python3
"""
ТЕСТ BLACKWELL ОПТИМИЗАЦИЙ
"""

import torch
import time
from transformers import AutoModelForImageTextToText, AutoProcessor

def test_blackwell_optimizations():
    """Тестируем оптимизации для Blackwell."""
    print("🧪 ТЕСТ BLACKWELL ОПТИМИЗАЦИЙ")
    print("=" * 50)
    
    # Проверяем GPU
    if not torch.cuda.is_available():
        print("❌ CUDA недоступна")
        return False
    
    gpu_name = torch.cuda.get_device_name(0)
    compute_cap = torch.cuda.get_device_capability(0)
    print(f"GPU: {gpu_name}")
    print(f"Compute Capability: {compute_cap}")
    
    # Включаем Blackwell оптимизации
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.enable_flash_sdp(True)
    
    print("✅ Blackwell оптимизации включены")
    
    # Тест bfloat16
    try:
        print("\n🔍 Тест bfloat16 операций...")
        start = time.time()
        
        x = torch.randn(1024, 1024, device='cuda', dtype=torch.bfloat16)
        y = torch.randn(1024, 1024, device='cuda', dtype=torch.bfloat16)
        
        for _ in range(100):
            z = torch.matmul(x, y)
        
        torch.cuda.synchronize()
        elapsed = time.time() - start
        
        print(f"✅ bfloat16 матричные операции: {elapsed:.3f}s")
        
    except Exception as e:
        print(f"❌ Ошибка bfloat16: {e}")
        return False
    
    # Тест загрузки модели
    try:
        print("\n🔍 Тест загрузки модели с Blackwell оптимизациями...")
        start = time.time()
        
        # Используем eager attention (совместимо с Blackwell)
        model = AutoModelForImageTextToText.from_pretrained(
            "Qwen/Qwen2-VL-2B-Instruct",
            torch_dtype=torch.bfloat16,
            attn_implementation="eager",  # НЕ flash_attention_2
            device_map="auto",
            trust_remote_code=True
        )
        
        load_time = time.time() - start
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Проверяем dtype модели
        first_param = next(model.parameters())
        print(f"✅ Dtype модели: {first_param.dtype}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        return False

if __name__ == "__main__":
    success = test_blackwell_optimizations()
    print(f"\n{'✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ' if success else '❌ ЕСТЬ ПРОБЛЕМЫ'}")
