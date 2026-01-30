#!/usr/bin/env python3
"""
Скрипт для исправления критических CUDA ошибок в системе ChatVLMLLM
Анализ логов показал серьезные проблемы, требующие немедленного исправления
"""

import json
import yaml
from datetime import datetime
import os

def analyze_log_errors():
    """Анализ ошибок из лога"""
    
    errors_found = {
        "critical_cuda_errors": [
            {
                "error": "CUDA error: device-side assert triggered",
                "frequency": "Очень высокая (множественные записи)",
                "severity": "КРИТИЧЕСКАЯ",
                "models_affected": ["qwen_vl_2b", "qwen3_vl_2b", "dots_ocr"],
                "impact": "Полный отказ системы при обработке изображений",
                "context": "Происходит при попытке инференса моделей"
            }
        ],
        "flash_attention_errors": [
            {
                "error": "FlashAttention2 has been toggled on, but it cannot be used due to the following error: the package flash_attn seems to be not installed",
                "frequency": "Высокая",
                "severity": "ВЫСОКАЯ", 
                "models_affected": ["qwen_vl_2b", "qwen3_vl_2b"],
                "impact": "Модели не могут загрузиться с Flash Attention",
                "solution": "Отключить Flash Attention в конфигурации"
            }
        ],
        "quantization_errors": [
            {
                "error": "Qwen3VLForConditionalGeneration.__init__() got an unexpected keyword argument 'load_in_8bit'",
                "frequency": "Средняя",
                "severity": "ВЫСОКАЯ",
                "models_affected": ["qwen3_vl_2b", "dots_ocr"],
                "impact": "Модели не поддерживают 8-bit квантизацию",
                "solution": "Отключить load_in_8bit для этих моделей"
            }
        ],
        "transformers_version_errors": [
            {
                "error": "transformers library with Qwen2-VL support is required. Install with: pip install transformers>=4.37.0",
                "frequency": "Средняя",
                "severity": "СРЕДНЯЯ",
                "models_affected": ["qwen_vl_2b"],
                "impact": "Модель не может загрузиться из-за версии transformers",
                "solution": "Обновить transformers или использовать fallback"
            }
        ]
    }
    
    return errors_found

def create_emergency_config():
    """Создание аварийной конфигурации для исправления ошибок"""
    
    emergency_config = {
        "models": {
            "qwen_vl_2b": {
                "name": "Qwen2-VL 2B (Emergency Mode)",
                "model_path": "Qwen/Qwen2-VL-2B-Instruct",
                "precision": "fp16",
                "attn_implementation": "eager",  # ПРИНУДИТЕЛЬНО eager вместо flash_attention
                "use_flash_attention": False,    # ОТКЛЮЧЕНО
                "device_map": "auto",
                "trust_remote_code": True,
                "max_new_tokens": 2048,         # Уменьшено для стабильности
                "context_length": 4096,
                "load_in_8bit": False,          # ОТКЛЮЧЕНО
                "load_in_4bit": False,          # ОТКЛЮЧЕНО
                "torch_dtype": "float16"
            },
            "qwen3_vl_2b": {
                "name": "Qwen3-VL 2B (Emergency Mode)",
                "model_path": "Qwen/Qwen3-VL-2B-Instruct", 
                "precision": "fp16",
                "attn_implementation": "eager",  # ПРИНУДИТЕЛЬНО eager
                "use_flash_attention": False,    # ОТКЛЮЧЕНО
                "device_map": "auto",
                "trust_remote_code": True,
                "max_new_tokens": 2048,         # Уменьшено
                "context_length": 4096,
                "load_in_8bit": False,          # ОТКЛЮЧЕНО
                "load_in_4bit": False,          # ОТКЛЮЧЕНО
                "torch_dtype": "float16"
            },
            "dots_ocr": {
                "name": "dots.ocr (Emergency Mode)",
                "model_path": "rednote-hilab/dots.ocr",
                "precision": "fp16",
                "attn_implementation": "eager",  # ПРИНУДИТЕЛЬНО eager
                "use_flash_attention": False,    # ОТКЛЮЧЕНО
                "device_map": "auto",
                "trust_remote_code": True,
                "max_new_tokens": 1024,         # Сильно уменьшено
                "context_length": 2048,
                "load_in_8bit": False,          # ОТКЛЮЧЕНО
                "load_in_4bit": False,          # ОТКЛЮЧЕНО
                "torch_dtype": "float16"
            }
        },
        "performance": {
            "blackwell_optimizations": {
                "enable_tf32": False,           # ОТКЛЮЧЕНО для стабильности
                "enable_cudnn_benchmark": False, # ОТКЛЮЧЕНО
                "use_bfloat16": False,          # ОТКЛЮЧЕНО
                "enable_sdpa": False,           # ОТКЛЮЧЕНО
                "force_eager_attention": True   # ПРИНУДИТЕЛЬНО
            },
            "generation_settings": {
                "default_max_tokens": 1024,    # Сильно уменьшено
                "max_context_length": 2048,    # Уменьшено
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            },
            "memory_management": {
                "clear_cache_before_load": True,
                "force_gc_collection": True,
                "max_memory_per_gpu": "8GB"    # Ограничение памяти
            }
        },
        "emergency_mode": {
            "enabled": True,
            "reason": "Critical CUDA errors detected in logs",
            "timestamp": datetime.now().isoformat(),
            "disabled_features": [
                "flash_attention",
                "8bit_quantization", 
                "4bit_quantization",
                "tf32_optimization",
                "cudnn_benchmark",
                "sdpa_attention"
            ]
        }
    }
    
    return emergency_config

def create_cuda_recovery_script():
    """Создание скрипта для восстановления CUDA"""
    
    recovery_script = """#!/usr/bin/env python3
'''
CUDA Recovery Script - Экстренное восстановление GPU состояния
'''

import torch
import gc
import os
import time

def emergency_cuda_recovery():
    '''Экстренное восстановление CUDA'''
    
    print("🚨 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ CUDA...")
    
    try:
        # 1. Принудительная очистка всех CUDA кешей
        if torch.cuda.is_available():
            print("🔄 Очистка CUDA кешей...")
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            torch.cuda.ipc_collect()
            
            # Сброс всех CUDA контекстов
            for i in range(torch.cuda.device_count()):
                with torch.cuda.device(i):
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
        
        # 2. Принудительная сборка мусора
        print("🗑️ Принудительная сборка мусора...")
        for _ in range(3):
            gc.collect()
            time.sleep(0.5)
        
        # 3. Установка переменных окружения для отладки
        print("🔧 Установка отладочных переменных...")
        os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
        os.environ['TORCH_USE_CUDA_DSA'] = '1'
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
        
        # 4. Проверка состояния GPU
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            print(f"✅ Обнаружено GPU устройств: {device_count}")
            
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                memory_allocated = torch.cuda.memory_allocated(i) / 1024**3
                memory_reserved = torch.cuda.memory_reserved(i) / 1024**3
                memory_total = props.total_memory / 1024**3
                
                print(f"GPU {i}: {props.name}")
                print(f"  Память: {memory_allocated:.2f}GB выделено, {memory_reserved:.2f}GB зарезервировано, {memory_total:.2f}GB всего")
                
                # Попытка создать тестовый тензор
                try:
                    test_tensor = torch.randn(100, 100, device=f'cuda:{i}')
                    del test_tensor
                    torch.cuda.empty_cache()
                    print(f"  ✅ GPU {i} работает корректно")
                except Exception as e:
                    print(f"  ❌ GPU {i} ошибка: {e}")
        
        print("✅ Восстановление CUDA завершено")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка восстановления CUDA: {e}")
        return False

if __name__ == "__main__":
    emergency_cuda_recovery()
"""
    
    return recovery_script

def create_model_loader_fixes():
    """Создание исправлений для загрузчика моделей"""
    
    fixes = {
        "model_loader_patches": {
            "force_eager_attention": True,
            "disable_flash_attention": True,
            "disable_quantization": True,
            "enable_cuda_recovery": True,
            "max_retries": 3,
            "fallback_to_cpu": True
        },
        "error_handling": {
            "cuda_device_assert": {
                "action": "clear_cache_and_retry",
                "max_retries": 2,
                "fallback": "cpu_mode"
            },
            "flash_attention_error": {
                "action": "disable_flash_attention",
                "fallback_attention": "eager"
            },
            "quantization_error": {
                "action": "disable_quantization",
                "fallback_precision": "fp16"
            },
            "transformers_version_error": {
                "action": "use_compatible_model",
                "fallback_model": "qwen3_vl_2b"
            }
        }
    }
    
    return fixes

def main():
    """Главная функция исправления ошибок"""
    
    print("🚨 КРИТИЧЕСКИЕ ОШИБКИ ОБНАРУЖЕНЫ В ЛОГАХ!")
    print("=" * 60)
    
    # Анализ ошибок
    errors = analyze_log_errors()
    
    print("📊 АНАЛИЗ ОШИБОК:")
    for category, error_list in errors.items():
        print(f"\n🔴 {category.upper()}:")
        for error in error_list:
            print(f"  • {error['error'][:80]}...")
            print(f"    Частота: {error['frequency']}")
            print(f"    Критичность: {error['severity']}")
            print(f"    Модели: {', '.join(error['models_affected'])}")
    
    print("\n" + "=" * 60)
    print("🔧 СОЗДАНИЕ ИСПРАВЛЕНИЙ...")
    
    # Создание аварийной конфигурации
    emergency_config = create_emergency_config()
    with open("config_emergency.yaml", "w", encoding="utf-8") as f:
        yaml.dump(emergency_config, f, default_flow_style=False, allow_unicode=True)
    print("✅ Создана аварийная конфигурация: config_emergency.yaml")
    
    # Создание скрипта восстановления CUDA
    recovery_script = create_cuda_recovery_script()
    with open("cuda_emergency_recovery.py", "w", encoding="utf-8") as f:
        f.write(recovery_script)
    print("✅ Создан скрипт восстановления CUDA: cuda_emergency_recovery.py")
    
    # Создание исправлений загрузчика
    fixes = create_model_loader_fixes()
    with open("model_loader_emergency_fixes.json", "w", encoding="utf-8") as f:
        json.dump(fixes, f, indent=2, ensure_ascii=False)
    print("✅ Созданы исправления загрузчика: model_loader_emergency_fixes.json")
    
    # Создание отчета
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "КРИТИЧЕСКИЕ ОШИБКИ ОБНАРУЖЕНЫ",
        "errors_analyzed": errors,
        "fixes_created": [
            "config_emergency.yaml",
            "cuda_emergency_recovery.py", 
            "model_loader_emergency_fixes.json"
        ],
        "immediate_actions_required": [
            "1. Запустить cuda_emergency_recovery.py",
            "2. Заменить config.yaml на config_emergency.yaml",
            "3. Перезапустить систему в аварийном режиме",
            "4. Протестировать модели по одной",
            "5. Обновить драйверы CUDA если необходимо"
        ],
        "root_causes": [
            "CUDA device-side assert - критическая ошибка GPU",
            "Flash Attention не установлен или несовместим",
            "8-bit квантизация не поддерживается моделями",
            "Версия transformers несовместима с некоторыми моделями"
        ]
    }
    
    with open("CRITICAL_ERRORS_ANALYSIS_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("🚨 КРИТИЧЕСКИЙ ОТЧЕТ СОЗДАН!")
    print("📄 Файл: CRITICAL_ERRORS_ANALYSIS_REPORT.json")
    print("\n⚠️  НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ:")
    print("1. 🔧 Запустите: python cuda_emergency_recovery.py")
    print("2. 📝 Замените config.yaml на config_emergency.yaml")
    print("3. 🔄 Перезапустите систему")
    print("4. 🧪 Протестируйте каждую модель отдельно")
    print("\n💡 Система находится в критическом состоянии!")
    print("   Рекомендуется использовать только аварийный режим!")

if __name__ == "__main__":
    main()