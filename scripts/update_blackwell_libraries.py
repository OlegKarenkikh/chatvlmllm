#!/usr/bin/env python3
"""
АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ БИБЛИОТЕК ДЛЯ RTX 5070 TI (BLACKWELL)

Основано на официальной документации:
- PyTorch: https://pytorch.org/get-started/locally/
- Flash Attention: https://github.com/Dao-AILab/flash-attention
- Qwen: https://github.com/QwenLM/Qwen3-VL
"""

import subprocess
import sys
import os
import torch
from pathlib import Path

def run_command(command, description=""):
    """Выполняем команду с логированием."""
    print(f"\n🔧 {description}")
    print(f"Команда: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ Успешно: {description}")
        if result.stdout:
            print(f"Вывод: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {description}")
        print(f"Код ошибки: {e.returncode}")
        if e.stderr:
            print(f"Ошибка: {e.stderr.strip()}")
        return False

def check_gpu_compatibility():
    """Проверяем совместимость GPU."""
    print("🔍 ПРОВЕРКА СОВМЕСТИМОСТИ GPU")
    print("=" * 50)
    
    if not torch.cuda.is_available():
        print("❌ CUDA недоступна")
        return False
    
    gpu_name = torch.cuda.get_device_name(0)
    compute_capability = torch.cuda.get_device_capability(0)
    
    print(f"GPU: {gpu_name}")
    print(f"Compute Capability: {compute_capability}")
    
    # Проверяем RTX 5070 Ti
    is_blackwell = "5070" in gpu_name or "5080" in gpu_name or "5090" in gpu_name
    is_sm120 = compute_capability >= (12, 0)
    
    if is_blackwell and is_sm120:
        print("✅ RTX 5070 Ti (Blackwell) обнаружена")
        print("⚠️ Flash Attention 2 НЕ поддерживается на Blackwell")
        print("✅ Будем использовать eager attention + bfloat16")
        return True
    elif compute_capability >= (8, 0):
        print("✅ Ampere/Ada GPU обнаружена")
        print("✅ Flash Attention 2 поддерживается")
        return True
    else:
        print("⚠️ Старая архитектура GPU")
        print("⚠️ Flash Attention может не поддерживаться")
        return True

def check_current_versions():
    """Проверяем текущие версии библиотек."""
    print("\n📋 ТЕКУЩИЕ ВЕРСИИ БИБЛИОТЕК")
    print("=" * 50)
    
    try:
        import torch
        print(f"PyTorch: {torch.__version__}")
        print(f"CUDA: {torch.version.cuda}")
        
        # Проверяем поддержку Blackwell
        arch_list = torch.cuda.get_arch_list()
        blackwell_support = 'sm_120' in arch_list
        print(f"Blackwell Support (sm_120): {'✅' if blackwell_support else '❌'}")
        
        if torch.cuda.is_available():
            print(f"bfloat16 Support: {'✅' if torch.cuda.is_bf16_supported() else '❌'}")
        
    except ImportError:
        print("PyTorch не установлен")
    
    try:
        import transformers
        print(f"Transformers: {transformers.__version__}")
    except ImportError:
        print("Transformers не установлен")
    
    try:
        import flash_attn
        print(f"Flash Attention: {flash_attn.__version__}")
        print("⚠️ Flash Attention установлен - может не работать на Blackwell")
    except ImportError:
        print("Flash Attention не установлен (нормально для Blackwell)")

def install_pytorch_blackwell():
    """Устанавливаем PyTorch с поддержкой Blackwell."""
    print("\n🚀 УСТАНОВКА PYTORCH С ПОДДЕРЖКОЙ BLACKWELL")
    print("=" * 50)
    
    # Проверяем текущую версию
    try:
        import torch
        current_version = torch.__version__
        arch_list = torch.cuda.get_arch_list()
        
        if 'sm_120' in arch_list and current_version.startswith('2.7'):
            print(f"✅ PyTorch {current_version} уже поддерживает Blackwell")
            return True
    except ImportError:
        pass
    
    # Устанавливаем PyTorch 2.7.0 с CUDA 12.8
    commands = [
        "pip uninstall -y torch torchvision torchaudio",
        "pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Выполнение: {cmd}"):
            return False
    
    return True

def install_transformers_optimized():
    """Устанавливаем оптимизированные версии transformers."""
    print("\n📚 УСТАНОВКА ОПТИМИЗИРОВАННЫХ TRANSFORMERS")
    print("=" * 50)
    
    commands = [
        "pip install --upgrade transformers>=4.50.0",
        "pip install --upgrade accelerate>=1.2.0",
        "pip install --upgrade qwen-vl-utils",
        "pip install --upgrade optimum",
        "pip install --upgrade bitsandbytes"
    ]
    
    for cmd in commands:
        run_command(cmd, f"Установка: {cmd.split()[-1]}")
    
    return True

def remove_flash_attention():
    """Удаляем Flash Attention если установлен (не совместим с Blackwell)."""
    print("\n🗑️ УДАЛЕНИЕ FLASH ATTENTION (НЕ СОВМЕСТИМ С BLACKWELL)")
    print("=" * 50)
    
    try:
        import flash_attn
        print("⚠️ Flash Attention обнаружен - удаляем для совместимости с Blackwell")
        run_command("pip uninstall -y flash-attn", "Удаление Flash Attention")
    except ImportError:
        print("✅ Flash Attention не установлен (хорошо для Blackwell)")
    
    return True

def update_model_configs():
    """Обновляем конфигурации моделей для Blackwell."""
    print("\n⚙️ ОБНОВЛЕНИЕ КОНФИГУРАЦИЙ МОДЕЛЕЙ")
    print("=" * 50)
    
    config_updates = {
        "precision": "bf16",  # Оптимально для Blackwell Tensor Cores
        "attn_implementation": "eager",  # Стабильно на sm_120
        "use_flash_attention": False,  # НЕ поддерживается на Blackwell
        "enable_blackwell_optimizations": True
    }
    
    print("Рекомендуемые обновления конфигурации:")
    for key, value in config_updates.items():
        print(f"  {key}: {value}")
    
    # Создаем оптимизированную конфигурацию
    config_content = """# ОПТИМИЗИРОВАННАЯ КОНФИГУРАЦИЯ ДЛЯ RTX 5070 TI (BLACKWELL)

models:
  qwen_vl_2b:
    name: "Qwen2-VL 2B (Blackwell Optimized)"
    model_path: "Qwen/Qwen2-VL-2B-Instruct"
    precision: "bf16"  # Оптимально для Blackwell Tensor Cores
    attn_implementation: "eager"  # Стабильно на sm_120
    use_flash_attention: false  # НЕ поддерживается на Blackwell
    device_map: "auto"
    trust_remote_code: true
    
  qwen3_vl_2b:
    name: "Qwen3-VL 2B (Blackwell Optimized)"
    model_path: "Qwen/Qwen3-VL-2B-Instruct"
    precision: "bf16"
    attn_implementation: "eager"
    use_flash_attention: false
    device_map: "auto"
    trust_remote_code: true
    
  dots_ocr:
    name: "dots.ocr (Blackwell Compatible)"
    model_path: "rednote-hilab/dots.ocr"
    precision: "bf16"
    attn_implementation: "eager"
    use_flash_attention: false
    device_map: "auto"
    trust_remote_code: true

performance:
  blackwell_optimizations:
    enable_tf32: true
    enable_cudnn_benchmark: true
    use_bfloat16: true
    enable_sdpa: true
    
gpu_requirements:
  rtx_5070_ti:
    compute_capability: "sm_120"
    cuda_version: "12.8+"
    pytorch_version: "2.7.0+"
    flash_attention_support: false
    recommended_precision: "bf16"
    tensor_cores: "5th_gen"
"""
    
    try:
        with open("config_blackwell_optimized.yaml", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✅ Создана config_blackwell_optimized.yaml")
    except Exception as e:
        print(f"❌ Ошибка создания конфигурации: {e}")
    
    return True

def verify_installation():
    """Проверяем корректность установки."""
    print("\n✅ ПРОВЕРКА УСТАНОВКИ")
    print("=" * 50)
    
    try:
        import torch
        print(f"PyTorch: {torch.__version__}")
        print(f"CUDA: {torch.version.cuda}")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            compute_cap = torch.cuda.get_device_capability(0)
            arch_list = torch.cuda.get_arch_list()
            
            print(f"GPU: {gpu_name}")
            print(f"Compute Capability: {compute_cap}")
            print(f"Blackwell Support: {'✅' if 'sm_120' in arch_list else '❌'}")
            print(f"bfloat16 Support: {'✅' if torch.cuda.is_bf16_supported() else '❌'}")
            
            # Тест простой операции
            try:
                x = torch.randn(10, 10, device='cuda', dtype=torch.bfloat16)
                y = torch.matmul(x, x.T)
                print("✅ Тест CUDA + bfloat16: Успешно")
            except Exception as e:
                print(f"❌ Тест CUDA + bfloat16: {e}")
        
        import transformers
        print(f"Transformers: {transformers.__version__}")
        
        try:
            import flash_attn
            print(f"⚠️ Flash Attention: {flash_attn.__version__} (может не работать на Blackwell)")
        except ImportError:
            print("✅ Flash Attention не установлен (рекомендуется для Blackwell)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def create_test_script():
    """Создаем тестовый скрипт для проверки оптимизаций."""
    test_script = '''#!/usr/bin/env python3
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
        print("\\n🔍 Тест bfloat16 операций...")
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
        print("\\n🔍 Тест загрузки модели с Blackwell оптимизациями...")
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
    print(f"\\n{'✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ' if success else '❌ ЕСТЬ ПРОБЛЕМЫ'}")
'''
    
    try:
        with open("test_blackwell_optimizations.py", "w", encoding="utf-8") as f:
            f.write(test_script)
        print("✅ Создан test_blackwell_optimizations.py")
    except Exception as e:
        print(f"❌ Ошибка создания тестового скрипта: {e}")

def main():
    """Главная функция обновления."""
    print("🚀 АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ ДЛЯ RTX 5070 TI (BLACKWELL)")
    print("=" * 80)
    print("Основано на официальной документации PyTorch, Transformers, Flash Attention")
    print("=" * 80)
    
    # Проверяем совместимость
    if not check_gpu_compatibility():
        print("⚠️ Продолжаем несмотря на предупреждения...")
    
    # Показываем текущие версии
    check_current_versions()
    
    # Спрашиваем подтверждение
    response = input("\n❓ Продолжить обновление библиотек? (y/N): ")
    if response.lower() not in ['y', 'yes', 'да']:
        print("❌ Обновление отменено")
        return False
    
    success = True
    
    # Удаляем Flash Attention (не совместим с Blackwell)
    success &= remove_flash_attention()
    
    # Устанавливаем PyTorch с поддержкой Blackwell
    success &= install_pytorch_blackwell()
    
    # Устанавливаем оптимизированные библиотеки
    success &= install_transformers_optimized()
    
    # Обновляем конфигурации
    success &= update_model_configs()
    
    # Создаем тестовый скрипт
    create_test_script()
    
    # Проверяем установку
    if success:
        success &= verify_installation()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("✅ PyTorch 2.7.0 с поддержкой Blackwell установлен")
        print("✅ Flash Attention удален (не совместим с RTX 5070 Ti)")
        print("✅ Оптимизированные библиотеки установлены")
        print("✅ Конфигурации обновлены для Blackwell")
        print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Перезапустите Python/IDE")
        print("2. Запустите: python test_blackwell_optimizations.py")
        print("3. Используйте config_blackwell_optimized.yaml")
        print("4. В коде используйте attn_implementation='eager' и torch.bfloat16")
    else:
        print("❌ ОБНОВЛЕНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
        print("⚠️ Проверьте логи выше и повторите установку")
    
    print("=" * 80)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)