#!/usr/bin/env python3
"""GPU setup and verification script for ChatVLMLLM."""

import sys
import subprocess
from pathlib import Path

try:
    import torch
except ImportError:
    print("❌ PyTorch не установлен!")
    print("Установите: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)


def check_cuda():
    """Check CUDA availability and version."""
    print("=" * 60)
    print("Проверка CUDA")
    print("=" * 60)
    
    if not torch.cuda.is_available():
        print("❌ CUDA недоступна!")
        print("\nВозможные причины:")
        print("1. Не установлены NVIDIA драйверы")
        print("2. PyTorch установлен без поддержки CUDA")
        print("3. GPU не поддерживает CUDA")
        print("\nРекомендации:")
        print("- Установите NVIDIA драйверы: https://www.nvidia.com/Download/index.aspx")
        print("- Переустановите PyTorch с CUDA: pip install torch --index-url https://download.pytorch.org/whl/cu121")
        return False
    
    print(f"✓ CUDA доступна: {torch.version.cuda}")
    print(f"✓ cuDNN версия: {torch.backends.cudnn.version()}")
    print(f"✓ Количество GPU: {torch.cuda.device_count()}")
    
    return True


def check_gpu_info():
    """Display detailed GPU information."""
    print("\n" + "=" * 60)
    print("Информация о GPU")
    print("=" * 60)
    
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        print(f"\nGPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"  VRAM: {props.total_memory / 1024**3:.2f} GB")
        print(f"  Compute Capability: {props.major}.{props.minor}")
        print(f"  Multiprocessors: {props.multi_processor_count}")
        print(f"  CUDA Cores: ~{props.multi_processor_count * 128}")
        
        # Memory usage
        allocated = torch.cuda.memory_allocated(i) / 1024**3
        reserved = torch.cuda.memory_reserved(i) / 1024**3
        print(f"  Используется: {allocated:.2f} GB")
        print(f"  Зарезервировано: {reserved:.2f} GB")
        print(f"  Свободно: {(props.total_memory / 1024**3) - reserved:.2f} GB")


def check_flash_attention():
    """Check Flash Attention installation."""
    print("\n" + "=" * 60)
    print("Проверка Flash Attention")
    print("=" * 60)
    
    try:
        import flash_attn
        print(f"✓ Flash Attention установлена")
        print(f"  Версия: {flash_attn.__version__}")
        
        # Test Flash Attention 2
        try:
            from flash_attn import flash_attn_func
            print("✓ Flash Attention 2 доступна")
            return True
        except ImportError:
            print("⚠️ Flash Attention 2 недоступна")
            return False
            
    except ImportError:
        print("❌ Flash Attention не установлена")
        print("\nУстановка:")
        print("  pip install flash-attn --no-build-isolation")
        print("\nПримечание: Требуется:")
        print("  - CUDA 11.6+")
        print("  - PyTorch 1.12+")
        print("  - Компилятор C++ (MSVC на Windows, GCC на Linux)")
        return False


def check_bitsandbytes():
    """Check BitsAndBytes for quantization."""
    print("\n" + "=" * 60)
    print("Проверка BitsAndBytes (квантизация)")
    print("=" * 60)
    
    try:
        import bitsandbytes as bnb
        print(f"✓ BitsAndBytes установлена")
        print(f"  Версия: {bnb.__version__}")
        
        # Check CUDA support
        if hasattr(bnb, 'cextension'):
            print("✓ CUDA расширения доступны")
            return True
        else:
            print("⚠️ CUDA расширения недоступны")
            return False
            
    except ImportError:
        print("❌ BitsAndBytes не установлена")
        print("\nУстановка:")
        print("  pip install bitsandbytes")
        print("\nВозможности:")
        print("  - INT8 квантизация (экономия 50% VRAM)")
        print("  - INT4 квантизация (экономия 75% VRAM)")
        return False


def benchmark_gpu():
    """Run simple GPU benchmark."""
    print("\n" + "=" * 60)
    print("Бенчмарк GPU")
    print("=" * 60)
    
    if not torch.cuda.is_available():
        print("Пропущено: CUDA недоступна")
        return
    
    print("Выполняется тест производительности...")
    
    # Matrix multiplication benchmark
    size = 4096
    device = torch.device("cuda:0")
    
    # Warm-up
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)
    _ = torch.matmul(a, b)
    torch.cuda.synchronize()
    
    # Benchmark
    import time
    start = time.time()
    for _ in range(10):
        c = torch.matmul(a, b)
        torch.cuda.synchronize()
    elapsed = time.time() - start
    
    tflops = (2 * size**3 * 10) / elapsed / 1e12
    print(f"\nРезультаты (матричное умножение {size}x{size}):")
    print(f"  Время: {elapsed:.3f} секунд")
    print(f"  Производительность: {tflops:.2f} TFLOPS")
    
    # Memory bandwidth test
    size_mb = 1024  # 1GB
    data = torch.randn(size_mb * 1024 * 256, device=device)
    torch.cuda.synchronize()
    
    start = time.time()
    for _ in range(10):
        _ = data * 2
        torch.cuda.synchronize()
    elapsed = time.time() - start
    
    bandwidth = (size_mb * 10) / elapsed
    print(f"\nПропускная способность памяти:")
    print(f"  {bandwidth:.2f} GB/s")


def recommend_settings():
    """Recommend optimal settings based on GPU."""
    print("\n" + "=" * 60)
    print("Рекомендации по настройкам")
    print("=" * 60)
    
    if not torch.cuda.is_available():
        print("\nРежим CPU:")
        print("  - precision: fp32")
        print("  - use_flash_attention: false")
        print("  - batch_size: 1")
        print("  - Рекомендуемая модель: qwen_vl_2b")
        return
    
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    gpu_name = torch.cuda.get_device_name(0)
    
    print(f"\nОбнаружена GPU: {gpu_name}")
    print(f"Доступно VRAM: {vram:.2f} GB")
    print("\nРекомендуемые настройки config.yaml:\n")
    
    if vram < 6:
        print("⚠️ Мало видеопамяти (<6GB)")
        print("models:")
        print("  qwen_vl_2b:")
        print("    precision: int4")
        print("    use_flash_attention: false")
        print("    device_map: auto")
        print("\nОжидаемое потребление VRAM: ~1.2GB")
    elif vram < 8:
        print("Конфигурация для 6-8GB VRAM:")
        print("models:")
        print("  qwen_vl_2b:")
        print("    precision: int8")
        print("    use_flash_attention: true")
        print("    device_map: auto")
        print("\nОжидаемое потребление VRAM: ~2.4GB")
    elif vram < 12:
        print("Конфигурация для 8-12GB VRAM:")
        print("models:")
        print("  qwen_vl_2b:")
        print("    precision: fp16")
        print("    use_flash_attention: true")
        print("  qwen3_vl_2b:")
        print("    precision: int8")
        print("    use_flash_attention: true")
        print("\nОжидаемое потребление VRAM: ~7.1GB (обе модели)")
    else:
        print("Оптимальная конфигурация для 12GB+ VRAM:")
        print("models:")
        print("  qwen_vl_2b:")
        print("    precision: fp16")
        print("    use_flash_attention: true")
        print("  qwen3_vl_2b:")
        print("    precision: fp16")
        print("    use_flash_attention: true")
        print("\nОжидаемое потребление VRAM: ~9.1GB (обе модели)")


def main():
    """Main setup and verification routine."""
    print("\n" + "#" * 60)
    print("# ChatVLMLLM - GPU Setup & Verification")
    print("#" * 60 + "\n")
    
    # Check CUDA
    cuda_ok = check_cuda()
    
    if cuda_ok:
        # GPU info
        check_gpu_info()
        
        # Check optional components
        flash_ok = check_flash_attention()
        bnb_ok = check_bitsandbytes()
        
        # Benchmark
        try:
            benchmark_gpu()
        except Exception as e:
            print(f"\n⚠️ Ошибка бенчмарка: {e}")
    
    # Recommendations
    recommend_settings()
    
    # Summary
    print("\n" + "=" * 60)
    print("Итоговый статус")
    print("=" * 60)
    
    status = []
    status.append(("CUDA", "✓" if cuda_ok else "❌"))
    
    if cuda_ok:
        try:
            import flash_attn
            status.append(("Flash Attention", "✓"))
        except ImportError:
            status.append(("Flash Attention", "⚠️"))
        
        try:
            import bitsandbytes
            status.append(("BitsAndBytes", "✓"))
        except ImportError:
            status.append(("BitsAndBytes", "⚠️"))
    
    for name, state in status:
        print(f"{name:20s}: {state}")
    
    print("\n" + "#" * 60)
    if cuda_ok:
        print("Система готова к работе с GPU! 🚀")
    else:
        print("Система будет работать на CPU (медленно) ⚠️")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    main()
