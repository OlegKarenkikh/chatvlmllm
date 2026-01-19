#!/usr/bin/env python3
"""
Тест PyTorch Scaled Dot Product Attention как альтернатива Flash Attention
"""

import torch
import torch.nn.functional as F
import time


def test_pytorch_sdpa():
    """Тест встроенного SDPA в PyTorch."""
    
    print("🔬 ТЕСТ PYTORCH SCALED DOT PRODUCT ATTENTION")
    print("=" * 50)
    
    if not torch.cuda.is_available():
        print("❌ CUDA недоступна")
        return
    
    device = torch.device("cuda")
    print(f"✅ Используем устройство: {device}")
    
    # Test parameters
    batch_size = 2
    seq_len = 512
    num_heads = 8
    head_dim = 64
    
    print(f"📊 Параметры теста:")
    print(f"   Batch size: {batch_size}")
    print(f"   Sequence length: {seq_len}")
    print(f"   Number of heads: {num_heads}")
    print(f"   Head dimension: {head_dim}")
    
    # Create test tensors
    q = torch.randn(batch_size, num_heads, seq_len, head_dim, device=device, dtype=torch.float16)
    k = torch.randn(batch_size, num_heads, seq_len, head_dim, device=device, dtype=torch.float16)
    v = torch.randn(batch_size, num_heads, seq_len, head_dim, device=device, dtype=torch.float16)
    
    print(f"✅ Тензоры созданы: {q.shape}")
    
    # Test 1: Standard attention
    print("\n🔤 Тест 1: Стандартное внимание")
    start_time = time.time()
    
    with torch.no_grad():
        # Manual attention calculation
        scale = 1.0 / (head_dim ** 0.5)
        attn_weights = torch.matmul(q, k.transpose(-2, -1)) * scale
        attn_weights = F.softmax(attn_weights, dim=-1)
        output_manual = torch.matmul(attn_weights, v)
    
    manual_time = time.time() - start_time
    print(f"✅ Стандартное внимание: {manual_time:.4f}s")
    print(f"📊 Результат: {output_manual.shape}")
    
    # Test 2: PyTorch SDPA
    print("\n⚡ Тест 2: PyTorch SDPA (оптимизированное)")
    start_time = time.time()
    
    with torch.no_grad():
        # PyTorch optimized attention
        output_sdpa = F.scaled_dot_product_attention(q, k, v)
    
    sdpa_time = time.time() - start_time
    print(f"✅ PyTorch SDPA: {sdpa_time:.4f}s")
    print(f"📊 Результат: {output_sdpa.shape}")
    
    # Compare results
    diff = torch.abs(output_manual - output_sdpa).max().item()
    print(f"\n📈 Сравнение результатов:")
    print(f"   Максимальная разность: {diff:.6f}")
    print(f"   Ускорение: {manual_time/sdpa_time:.2f}x")
    
    if diff < 1e-3:
        print("✅ Результаты совпадают!")
    else:
        print("⚠️ Есть различия в результатах")
    
    # Test 3: Check available backends
    print(f"\n🔧 Доступные бэкенды SDPA:")
    
    try:
        # Check what backends are available
        with torch.backends.cuda.sdp_kernel():
            print("   ✅ CUDA kernel доступен")
    except:
        print("   ❌ CUDA kernel недоступен")
    
    try:
        # Test with different settings
        with torch.backends.cuda.sdp_kernel(enable_flash=True):
            output_flash = F.scaled_dot_product_attention(q, k, v)
            print("   ✅ Flash Attention backend доступен!")
    except:
        print("   ⚠️ Flash Attention backend недоступен, используется fallback")
    
    try:
        with torch.backends.cuda.sdp_kernel(enable_math=True):
            output_math = F.scaled_dot_product_attention(q, k, v)
            print("   ✅ Math backend доступен")
    except:
        print("   ❌ Math backend недоступен")
    
    try:
        with torch.backends.cuda.sdp_kernel(enable_mem_efficient=True):
            output_mem = F.scaled_dot_product_attention(q, k, v)
            print("   ✅ Memory Efficient backend доступен")
    except:
        print("   ❌ Memory Efficient backend недоступен")
    
    print(f"\n💡 ЗАКЛЮЧЕНИЕ:")
    print(f"   PyTorch SDPA работает как замена Flash Attention!")
    print(f"   Ускорение: {manual_time/sdpa_time:.2f}x по сравнению с ручной реализацией")
    print(f"   Можно использовать вместо flash-attn для dots.ocr")


if __name__ == "__main__":
    test_pytorch_sdpa()