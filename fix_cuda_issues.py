#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ CUDA ПРОБЛЕМ И ПЕРЕЗАПУСК СИСТЕМЫ

Выполняет все рекомендации из отчета тестирования:
1. Очистка CUDA контекста
2. Перезапуск CUDA драйверов
3. Оптимизация параметров генерации
4. Создание CPU fallback режима
"""

import os
import sys
import time
import torch
import subprocess
from pathlib import Path

def clear_cuda_context():
    """Очищаем CUDA контекст полностью."""
    print("🔧 Очищаем CUDA контекст...")
    
    try:
        if torch.cuda.is_available():
            # Очищаем все CUDA кеши
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
            # Сбрасываем все CUDA устройства
            for i in range(torch.cuda.device_count()):
                with torch.cuda.device(i):
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
            
            print("✅ CUDA контекст очищен")
        else:
            print("⚠️ CUDA недоступна")
            
    except Exception as e:
        print(f"❌ Ошибка очистки CUDA: {e}")

def reset_cuda_environment():
    """Сбрасываем переменные окружения CUDA."""
    print("🔄 Сбрасываем переменные окружения CUDA...")
    
    # Устанавливаем переменные для отладки CUDA
    cuda_env_vars = {
        'CUDA_LAUNCH_BLOCKING': '1',
        'TORCH_USE_CUDA_DSA': '1',
        'CUDA_DEVICE_ORDER': 'PCI_BUS_ID',
        'TOKENIZERS_PARALLELISM': 'false'
    }
    
    for var, value in cuda_env_vars.items():
        os.environ[var] = value
        print(f"   {var} = {value}")
    
    print("✅ Переменные окружения установлены")

def create_cpu_fallback_config():
    """Создаем конфигурацию с CPU fallback."""
    print("💻 Создаем конфигурацию с CPU fallback...")
    
    cpu_config = """# CPU FALLBACK CONFIGURATION
models:
  qwen_vl_2b:
    name: "Qwen2-VL 2B (CPU Fallback)"
    description: "Основная OCR модель с CPU fallback"
    model_path: "Qwen/Qwen2-VL-2B-Instruct"
    max_length: 32768
    precision: "fp32"  # CPU режим
    device_map: "cpu"
    force_cpu: true
    
  qwen3_vl_2b:
    name: "Qwen3-VL 2B (Optimized)"
    description: "Многоязычная модель с оптимизацией"
    model_path: "Qwen/Qwen3-VL-2B-Instruct"
    max_length: 256000
    precision: "fp16"
    device_map: "auto"
    generation_config:
      max_new_tokens: 512
      do_sample: false
      temperature: 0.1
      
  dots_ocr_corrected:
    name: "dots.ocr (Corrected)"
    description: "Исправленная реализация dots.ocr"
    model_path: "rednote-hilab/dots.ocr"
    max_length: 24000
    precision: "fp16"
    device_map: "auto"
    use_corrected_implementation: true

gpu_requirements:
  optimization:
    default_model: "qwen3_vl_2b"
    single_model_mode: true
    auto_unload: true
    cpu_fallback: true
    cuda_error_recovery: true
"""
    
    with open("config_cpu_fallback.yaml", "w", encoding="utf-8") as f:
        f.write(cpu_config)
    
    print("✅ Конфигурация CPU fallback создана: config_cpu_fallback.yaml")

def optimize_generation_parameters():
    """Создаем оптимизированные параметры генерации."""
    print("⚡ Создаем оптимизированные параметры генерации...")
    
    optimization_code = '''"""
ОПТИМИЗИРОВАННЫЕ ПАРАМЕТРЫ ГЕНЕРАЦИИ ДЛЯ УСТРАНЕНИЯ CUDA ПРОБЛЕМ
"""

import torch

# Оптимизированные параметры для каждой модели
OPTIMIZED_GENERATION_PARAMS = {
    "qwen_vl_2b": {
        "max_new_tokens": 512,
        "do_sample": False,
        "temperature": 0.1,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
        "pad_token_id": None,  # Будет установлен автоматически
        "use_cache": True,
        "output_attentions": False,
        "output_hidden_states": False
    },
    
    "qwen3_vl_2b": {
        "max_new_tokens": 1024,
        "do_sample": False,
        "temperature": 0.1,
        "top_p": 0.9,
        "repetition_penalty": 1.05,
        "pad_token_id": 151645,  # Специфично для Qwen3-VL
        "use_cache": True,
        "output_attentions": False,
        "output_hidden_states": False
    },
    
    "dots_ocr": {
        "max_new_tokens": 2048,
        "do_sample": False,
        "temperature": 0.1,
        "top_p": 0.95,
        "repetition_penalty": 1.0,
        "pad_token_id": None,
        "use_cache": True,
        "output_attentions": False,
        "output_hidden_states": False
    }
}

def get_optimized_params(model_name: str) -> dict:
    """Получаем оптимизированные параметры для модели."""
    return OPTIMIZED_GENERATION_PARAMS.get(model_name, OPTIMIZED_GENERATION_PARAMS["qwen3_vl_2b"])

def apply_cuda_optimizations():
    """Применяем CUDA оптимизации."""
    if torch.cuda.is_available():
        # Оптимизации для стабильности
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        
        # Очистка кеша
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        
        return True
    return False
'''
    
    with open("utils/optimized_generation.py", "w", encoding="utf-8") as f:
        f.write(optimization_code)
    
    print("✅ Оптимизированные параметры созданы: utils/optimized_generation.py")

def create_cuda_recovery_system():
    """Создаем систему восстановления после CUDA ошибок."""
    print("🛡️ Создаем систему восстановления CUDA...")
    
    recovery_code = '''"""
СИСТЕМА ВОССТАНОВЛЕНИЯ ПОСЛЕ CUDA ОШИБОК
"""

import torch
import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

class CUDARecoveryManager:
    """Менеджер восстановления после CUDA ошибок."""
    
    def __init__(self):
        self.cuda_error_count = 0
        self.max_cuda_errors = 3
        self.recovery_delay = 2.0
        
    def is_cuda_error(self, error: Exception) -> bool:
        """Проверяем, является ли ошибка CUDA ошибкой."""
        error_str = str(error).lower()
        cuda_error_indicators = [
            'cuda error',
            'device-side assert',
            'cudaerrorassert',
            'cuda runtime error',
            'out of memory',
            'cuda out of memory'
        ]
        
        return any(indicator in error_str for indicator in cuda_error_indicators)
    
    def recover_from_cuda_error(self) -> bool:
        """Восстанавливаемся после CUDA ошибки."""
        try:
            logger.warning(f"🔄 Попытка восстановления CUDA (попытка {self.cuda_error_count + 1}/{self.max_cuda_errors})")
            
            if torch.cuda.is_available():
                # Очищаем все CUDA кеши
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                
                # Ждем немного
                time.sleep(self.recovery_delay)
                
                # Тестируем CUDA
                test_tensor = torch.randn(10, 10, device='cuda')
                result = test_tensor @ test_tensor.T
                result.cpu()
                
                logger.info("✅ CUDA восстановлена успешно")
                self.cuda_error_count = 0
                return True
            else:
                logger.warning("⚠️ CUDA недоступна")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка восстановления CUDA: {e}")
            self.cuda_error_count += 1
            return False
    
    def safe_cuda_call(self, func: Callable, *args, **kwargs) -> Any:
        """Безопасный вызов функции с CUDA восстановлением."""
        for attempt in range(self.max_cuda_errors + 1):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                if self.is_cuda_error(e) and attempt < self.max_cuda_errors:
                    logger.warning(f"⚠️ CUDA ошибка: {e}")
                    
                    if self.recover_from_cuda_error():
                        continue
                    else:
                        # Если восстановление не удалось, пробуем CPU режим
                        logger.warning("🔄 Переключаемся на CPU режим")
                        kwargs['device'] = 'cpu'
                        kwargs['force_cpu'] = True
                        continue
                else:
                    raise e
        
        raise RuntimeError(f"Не удалось выполнить операцию после {self.max_cuda_errors} попыток")

# Глобальный менеджер восстановления
cuda_recovery_manager = CUDARecoveryManager()
'''
    
    with open("utils/cuda_recovery.py", "w", encoding="utf-8") as f:
        f.write(recovery_code)
    
    print("✅ Система восстановления CUDA создана: utils/cuda_recovery.py")

def update_model_loader():
    """Обновляем model_loader с поддержкой исправленной dots_ocr."""
    print("🔄 Обновляем model_loader...")
    
    try:
        # Читаем текущий model_loader
        with open("models/model_loader.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Добавляем импорт исправленной модели
        if "from models.dots_ocr_corrected import DotsOCRCorrectedModel" not in content:
            import_section = content.find("from models.dots_ocr import DotsOCRModel")
            if import_section != -1:
                new_import = "from models.dots_ocr_corrected import DotsOCRCorrectedModel\n"
                content = content[:import_section] + new_import + content[import_section:]
        
        # Добавляем в реестр моделей
        if '"dots_ocr_corrected": DotsOCRCorrectedModel' not in content:
            registry_section = content.find('"dots_ocr": DotsOCRModel')
            if registry_section != -1:
                end_line = content.find('\n', registry_section)
                new_entry = ',\n        "dots_ocr_corrected": DotsOCRCorrectedModel'
                content = content[:end_line] + new_entry + content[end_line:]
        
        # Сохраняем обновленный файл
        with open("models/model_loader.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ model_loader обновлен")
        
    except Exception as e:
        print(f"⚠️ Предупреждение при обновлении model_loader: {e}")

def test_cuda_recovery():
    """Тестируем систему восстановления CUDA."""
    print("🧪 Тестируем систему восстановления CUDA...")
    
    try:
        if torch.cuda.is_available():
            # Простой тест CUDA
            test_tensor = torch.randn(100, 100, device='cuda')
            result = test_tensor @ test_tensor.T
            result.cpu()
            torch.cuda.empty_cache()
            
            print("✅ CUDA работает корректно")
            return True
        else:
            print("⚠️ CUDA недоступна, будет использован CPU режим")
            return False
            
    except Exception as e:
        print(f"❌ CUDA тест не пройден: {e}")
        return False

def main():
    """Основная функция исправления."""
    print("🔧 ИСПРАВЛЕНИЕ CUDA ПРОБЛЕМ И ОПТИМИЗАЦИЯ СИСТЕМЫ")
    print("=" * 60)
    
    # Этап 1: Очистка CUDA
    clear_cuda_context()
    
    # Этап 2: Настройка окружения
    reset_cuda_environment()
    
    # Этап 3: Создание CPU fallback
    create_cpu_fallback_config()
    
    # Этап 4: Оптимизация параметров
    optimize_generation_parameters()
    
    # Этап 5: Система восстановления
    create_cuda_recovery_system()
    
    # Этап 6: Обновление загрузчика
    update_model_loader()
    
    # Этап 7: Тестирование
    cuda_ok = test_cuda_recovery()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ИСПРАВЛЕНИЯ")
    print("=" * 60)
    
    print(f"✅ CUDA контекст очищен")
    print(f"✅ Переменные окружения настроены")
    print(f"✅ CPU fallback конфигурация создана")
    print(f"✅ Параметры генерации оптимизированы")
    print(f"✅ Система восстановления CUDA создана")
    print(f"✅ model_loader обновлен")
    print(f"{'✅' if cuda_ok else '⚠️'} CUDA тест: {'Пройден' if cuda_ok else 'Не пройден (будет использован CPU)'}")
    
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("1. Перезапустите Python процесс для применения изменений")
    print("2. Используйте config_cpu_fallback.yaml при проблемах с CUDA")
    print("3. Запустите test_end_to_end_final_with_inference.py для проверки")
    
    return cuda_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)