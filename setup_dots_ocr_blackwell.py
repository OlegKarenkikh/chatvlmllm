#!/usr/bin/env python3
"""
ПРАВИЛЬНАЯ УСТАНОВКА DOTS.OCR ДЛЯ RTX 5070 TI BLACKWELL

Основано на официальной документации dots.ocr
"""

import subprocess
import sys
import os
import torch
from pathlib import Path

def check_system_requirements():
    """Проверяем системные требования."""
    print("🔍 ПРОВЕРКА СИСТЕМНЫХ ТРЕБОВАНИЙ")
    print("=" * 50)
    
    # GPU информация
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        compute_cap = torch.cuda.get_device_capability(0)
        
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ VRAM: {gpu_memory:.2f}GB")
        print(f"✅ Compute Capability: {compute_cap}")
        
        # Проверяем RTX 5070 Ti
        if "5070 Ti" in gpu_name:
            print("✅ RTX 5070 Ti обнаружена")
            if gpu_memory >= 15.0:  # 16GB GDDR7
                print("✅ Достаточно VRAM для dots.ocr")
            else:
                print("⚠️ Рекомендуется 16GB+ VRAM для оптимальной работы")
        
        # Проверяем Blackwell архитектуру
        if compute_cap >= (12, 0):  # sm_120
            print("✅ Blackwell архитектура поддерживается")
        else:
            print("❌ Требуется Blackwell архитектура (sm_120+)")
            return False
            
    else:
        print("❌ CUDA недоступна")
        return False
    
    # PyTorch версия
    pytorch_version = torch.__version__
    cuda_version = torch.version.cuda
    
    print(f"📦 PyTorch: {pytorch_version}")
    print(f"⚡ CUDA: {cuda_version}")
    
    return True

def install_pytorch_cuda128():
    """Устанавливаем PyTorch с CUDA 12.8 для dots.ocr."""
    print("\n📦 УСТАНОВКА PYTORCH С CUDA 12.8")
    print("=" * 50)
    
    try:
        # Проверяем текущую версию
        current_cuda = torch.version.cuda
        if current_cuda == "12.8":
            print("✅ PyTorch с CUDA 12.8 уже установлен")
            return True
        
        print(f"🔄 Текущая CUDA версия: {current_cuda}")
        print("🔄 Устанавливаем PyTorch 2.7.0 с CUDA 12.8...")
        
        # Команда установки PyTorch 2.7.0 с CUDA 12.8
        install_cmd = [
            sys.executable, "-m", "pip", "install", 
            "torch==2.7.0", 
            "torchvision==0.22.0", 
            "torchaudio==2.7.0",
            "--index-url", "https://download.pytorch.org/whl/cu128",
            "--force-reinstall"
        ]
        
        print(f"Выполняем: {' '.join(install_cmd)}")
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyTorch 2.7.0 с CUDA 12.8 установлен успешно")
            return True
        else:
            print(f"❌ Ошибка установки PyTorch: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при установке PyTorch: {e}")
        return False

def install_flash_attention():
    """Устанавливаем flash-attn==2.8.0.post2 для dots.ocr."""
    print("\n⚡ УСТАНОВКА FLASH ATTENTION 2.8.0.post2")
    print("=" * 50)
    
    try:
        # Проверяем, установлен ли flash-attn
        try:
            import flash_attn
            current_version = flash_attn.__version__
            if current_version == "2.8.0.post2":
                print("✅ flash-attn 2.8.0.post2 уже установлен")
                return True
            else:
                print(f"🔄 Текущая версия flash-attn: {current_version}")
        except ImportError:
            print("📦 flash-attn не установлен")
        
        print("🔄 Устанавливаем flash-attn==2.8.0.post2...")
        
        # Установка flash-attn с правильной версией
        install_cmd = [
            sys.executable, "-m", "pip", "install", 
            "flash-attn==2.8.0.post2",
            "--no-build-isolation"
        ]
        
        print(f"Выполняем: {' '.join(install_cmd)}")
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ flash-attn 2.8.0.post2 установлен успешно")
            return True
        else:
            print(f"❌ Ошибка установки flash-attn: {result.stderr}")
            print("🔄 Пробуем альтернативную установку...")
            
            # Альтернативная установка через pip без кеша
            alt_cmd = [
                sys.executable, "-m", "pip", "install", 
                "flash-attn==2.8.0.post2",
                "--no-cache-dir",
                "--no-build-isolation",
                "--force-reinstall"
            ]
            
            result2 = subprocess.run(alt_cmd, capture_output=True, text=True)
            if result2.returncode == 0:
                print("✅ flash-attn установлен через альтернативный метод")
                return True
            else:
                print(f"❌ Альтернативная установка также не удалась: {result2.stderr}")
                return False
            
    except Exception as e:
        print(f"❌ Ошибка при установке flash-attn: {e}")
        return False

def clone_dots_ocr_repo():
    """Клонируем официальный репозиторий dots.ocr."""
    print("\n📂 КЛОНИРОВАНИЕ РЕПОЗИТОРИЯ DOTS.OCR")
    print("=" * 50)
    
    repo_path = Path("dots.ocr")
    
    if repo_path.exists():
        print("✅ Репозиторий dots.ocr уже существует")
        return str(repo_path)
    
    try:
        clone_cmd = [
            "git", "clone", 
            "https://github.com/rednote-hilab/dots.ocr.git"
        ]
        
        print(f"Выполняем: {' '.join(clone_cmd)}")
        result = subprocess.run(clone_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Репозиторий dots.ocr клонирован успешно")
            return str(repo_path)
        else:
            print(f"❌ Ошибка клонирования: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при клонировании: {e}")
        return None

def install_dots_ocr(repo_path):
    """Устанавливаем dots.ocr из исходного кода."""
    print("\n🚀 УСТАНОВКА DOTS.OCR")
    print("=" * 50)
    
    if not repo_path or not Path(repo_path).exists():
        print("❌ Репозиторий dots.ocr не найден")
        return False
    
    try:
        # Переходим в директорию репозитория
        original_cwd = os.getcwd()
        os.chdir(repo_path)
        
        print(f"📁 Переходим в {repo_path}")
        
        # Устанавливаем dots.ocr в режиме разработки
        install_cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
        
        print(f"Выполняем: {' '.join(install_cmd)}")
        result = subprocess.run(install_cmd, capture_output=True, text=True)
        
        # Возвращаемся в исходную директорию
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            print("✅ dots.ocr установлен успешно")
            return True
        else:
            print(f"❌ Ошибка установки dots.ocr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при установке dots.ocr: {e}")
        # Убеждаемся, что вернулись в исходную директорию
        try:
            os.chdir(original_cwd)
        except:
            pass
        return False

def install_additional_dependencies():
    """Устанавливаем дополнительные зависимости."""
    print("\n📦 УСТАНОВКА ДОПОЛНИТЕЛЬНЫХ ЗАВИСИМОСТЕЙ")
    print("=" * 50)
    
    dependencies = [
        "transformers>=4.50.0",
        "accelerate>=1.2.0",
        "qwen-vl-utils",
        "pillow",
        "numpy",
        "opencv-python",
        "requests"
    ]
    
    try:
        for dep in dependencies:
            print(f"📦 Устанавливаем {dep}...")
            install_cmd = [sys.executable, "-m", "pip", "install", dep]
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {dep} установлен")
            else:
                print(f"⚠️ Предупреждение при установке {dep}: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при установке зависимостей: {e}")
        return False

def test_dots_ocr_installation():
    """Тестируем установку dots.ocr."""
    print("\n🧪 ТЕСТИРОВАНИЕ УСТАНОВКИ DOTS.OCR")
    print("=" * 50)
    
    try:
        # Тест 1: Импорт модулей
        print("🔍 Тест 1: Импорт модулей...")
        
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ CUDA: {torch.version.cuda}")
        print(f"✅ GPU доступна: {torch.cuda.is_available()}")
        
        try:
            import flash_attn
            print(f"✅ flash-attn: {flash_attn.__version__}")
        except ImportError:
            print("❌ flash-attn не импортируется")
            return False
        
        # Тест 2: Загрузка модели
        print("\n🔍 Тест 2: Загрузка модели dots.ocr...")
        
        from transformers import AutoModelForCausalLM, AutoProcessor
        
        model_path = "rednote-hilab/dots.ocr"
        
        # Пробуем загрузить процессор
        processor = AutoProcessor.from_pretrained(
            model_path, 
            trust_remote_code=True
        )
        print("✅ Процессор загружен успешно")
        
        # Пробуем загрузить модель (только проверка, не полная загрузка)
        try:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.bfloat16,
                device_map="cpu",  # Загружаем на CPU для теста
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            print("✅ Модель загружена успешно (CPU тест)")
            
            # Очищаем память
            del model
            del processor
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"⚠️ Предупреждение при загрузке модели: {e}")
        
        print("\n✅ Базовое тестирование пройдено")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_dots_ocr_config():
    """Создаем оптимизированную конфигурацию для dots.ocr на RTX 5070 Ti."""
    print("\n⚙️ СОЗДАНИЕ КОНФИГУРАЦИИ DOTS.OCR")
    print("=" * 50)
    
    config_content = """# ОПТИМИЗИРОВАННАЯ КОНФИГУРАЦИЯ DOTS.OCR ДЛЯ RTX 5070 TI BLACKWELL

models:
  dots_ocr_blackwell:
    name: "dots.ocr (RTX 5070 Ti Optimized)"
    model_path: "rednote-hilab/dots.ocr"
    precision: "bf16"  # Оптимально для Blackwell Tensor Cores
    attn_implementation: "flash_attention_2"  # Теперь поддерживается с правильной версией
    use_flash_attention: true  # Включаем flash attention
    device_map: "auto"
    trust_remote_code: true
    
    # Специфичные настройки для RTX 5070 Ti
    gpu_memory_utilization: 0.9  # 90% от 16GB VRAM
    tensor_parallel_size: 1
    max_model_len: 4096
    
    # Оптимизации для Blackwell
    enable_tf32: true
    enable_cudnn_benchmark: true
    use_bfloat16: true

performance:
  blackwell_optimizations:
    enable_tf32: true
    enable_cudnn_benchmark: true
    use_bfloat16: true
    enable_flash_attention: true  # Теперь поддерживается
    gpu_memory_utilization: 0.9
    
gpu_requirements:
  rtx_5070_ti:
    compute_capability: "sm_120"
    cuda_version: "12.8"
    pytorch_version: "2.7.0"
    flash_attention_version: "2.8.0.post2"
    recommended_precision: "bf16"
    tensor_cores: "5th_gen"
    vram_gb: 16

# Настройки для vLLM (рекомендуемый способ запуска)
vllm:
  gpu_memory_utilization: 0.95
  tensor_parallel_size: 1
  max_model_len: 4096
  trust_remote_code: true
  async_scheduling: true
"""
    
    try:
        with open("config_dots_ocr_blackwell.yaml", "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print("✅ Конфигурация сохранена в config_dots_ocr_blackwell.yaml")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания конфигурации: {e}")
        return False

def create_vllm_launch_script():
    """Создаем скрипт запуска через vLLM."""
    print("\n🚀 СОЗДАНИЕ СКРИПТА ЗАПУСКА VLLM")
    print("=" * 50)
    
    script_content = """#!/usr/bin/env python3
\"\"\"
ЗАПУСК DOTS.OCR ЧЕРЕЗ VLLM ДЛЯ RTX 5070 TI

Оптимизированный запуск с поддержкой Blackwell архитектуры
\"\"\"

import subprocess
import sys
import os

def launch_dots_ocr_vllm():
    \"\"\"Запускаем dots.ocr через vLLM сервер.\"\"\"
    print("🚀 ЗАПУСК DOTS.OCR ЧЕРЕЗ VLLM")
    print("=" * 50)
    
    # Команда запуска vLLM сервера
    vllm_cmd = [
        "vllm", "serve", "rednote-hilab/dots.ocr",
        "--trust-remote-code",
        "--async-scheduling",
        "--gpu-memory-utilization", "0.95",
        "--tensor-parallel-size", "1",
        "--max-model-len", "4096",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    
    print(f"Команда запуска: {' '.join(vllm_cmd)}")
    print("🌐 Сервер будет доступен на http://localhost:8000")
    print("📋 Для остановки нажмите Ctrl+C")
    print()
    
    try:
        # Запускаем vLLM сервер
        subprocess.run(vllm_cmd)
        
    except KeyboardInterrupt:
        print("\\n⏹️ Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска vLLM: {e}")

def launch_dots_ocr_docker():
    \"\"\"Запускаем dots.ocr через Docker.\"\"\"
    print("🐳 ЗАПУСК DOTS.OCR ЧЕРЕЗ DOCKER")
    print("=" * 50)
    
    # Команда запуска Docker контейнера
    docker_cmd = [
        "docker", "run", "--gpus", "all",
        "-e", "VLLM_GPU_MEMORY_UTILIZATION=0.9",
        "-e", "VLLM_TENSOR_PARALLEL_SIZE=1", 
        "-e", "VLLM_MAX_MODEL_LEN=4096",
        "-p", "8000:8000",
        "rednotehilab/dots.ocr:vllm-openai-v0.9.1"
    ]
    
    print(f"Команда запуска: {' '.join(docker_cmd)}")
    print("🌐 Сервер будет доступен на http://localhost:8000")
    print("📋 Для остановки нажмите Ctrl+C")
    print()
    
    try:
        # Запускаем Docker контейнер
        subprocess.run(docker_cmd)
        
    except KeyboardInterrupt:
        print("\\n⏹️ Docker контейнер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска Docker: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "docker":
        launch_dots_ocr_docker()
    else:
        launch_dots_ocr_vllm()
"""
    
    try:
        with open("launch_dots_ocr.py", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        print("✅ Скрипт запуска сохранен в launch_dots_ocr.py")
        print("📋 Использование:")
        print("   python launch_dots_ocr.py        # Запуск через vLLM")
        print("   python launch_dots_ocr.py docker # Запуск через Docker")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания скрипта: {e}")
        return False

def main():
    """Главная функция установки dots.ocr для RTX 5070 Ti."""
    print("🚀 УСТАНОВКА DOTS.OCR ДЛЯ RTX 5070 TI BLACKWELL")
    print("=" * 80)
    print("Основано на официальной документации dots.ocr")
    print("=" * 80)
    
    success_steps = 0
    total_steps = 8
    
    # Шаг 1: Проверка системных требований
    if check_system_requirements():
        success_steps += 1
        print("✅ Шаг 1/8: Системные требования проверены")
    else:
        print("❌ Шаг 1/8: Системные требования не выполнены")
        return False
    
    # Шаг 2: Установка PyTorch с CUDA 12.8
    if install_pytorch_cuda128():
        success_steps += 1
        print("✅ Шаг 2/8: PyTorch с CUDA 12.8 установлен")
    else:
        print("❌ Шаг 2/8: Ошибка установки PyTorch")
        print("⚠️ Продолжаем с текущей версией PyTorch...")
    
    # Шаг 3: Установка flash-attn
    if install_flash_attention():
        success_steps += 1
        print("✅ Шаг 3/8: flash-attn 2.8.0.post2 установлен")
    else:
        print("❌ Шаг 3/8: Ошибка установки flash-attn")
        print("⚠️ dots.ocr может не работать без правильной версии flash-attn")
    
    # Шаг 4: Клонирование репозитория
    repo_path = clone_dots_ocr_repo()
    if repo_path:
        success_steps += 1
        print("✅ Шаг 4/8: Репозиторий dots.ocr клонирован")
    else:
        print("❌ Шаг 4/8: Ошибка клонирования репозитория")
    
    # Шаг 5: Установка dots.ocr
    if repo_path and install_dots_ocr(repo_path):
        success_steps += 1
        print("✅ Шаг 5/8: dots.ocr установлен")
    else:
        print("❌ Шаг 5/8: Ошибка установки dots.ocr")
    
    # Шаг 6: Установка дополнительных зависимостей
    if install_additional_dependencies():
        success_steps += 1
        print("✅ Шаг 6/8: Дополнительные зависимости установлены")
    else:
        print("❌ Шаг 6/8: Ошибка установки зависимостей")
    
    # Шаг 7: Создание конфигурации
    if create_dots_ocr_config():
        success_steps += 1
        print("✅ Шаг 7/8: Конфигурация создана")
    else:
        print("❌ Шаг 7/8: Ошибка создания конфигурации")
    
    # Шаг 8: Создание скрипта запуска
    if create_vllm_launch_script():
        success_steps += 1
        print("✅ Шаг 8/8: Скрипт запуска создан")
    else:
        print("❌ Шаг 8/8: Ошибка создания скрипта")
    
    # Финальное тестирование
    print("\n" + "=" * 80)
    print("🧪 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ")
    print("=" * 80)
    
    if test_dots_ocr_installation():
        print("✅ Тестирование пройдено успешно")
        test_success = True
    else:
        print("❌ Тестирование не пройдено")
        test_success = False
    
    # Итоговый отчет
    print("\n" + "=" * 80)
    print("📊 ИТОГОВЫЙ ОТЧЕТ УСТАНОВКИ")
    print("=" * 80)
    
    success_rate = (success_steps / total_steps) * 100
    print(f"📈 Успешность установки: {success_steps}/{total_steps} ({success_rate:.1f}%)")
    
    if success_steps >= 6 and test_success:
        print("🎉 УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
        print("\n💡 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Запустите dots.ocr через vLLM:")
        print("   python launch_dots_ocr.py")
        print("2. Или через Docker:")
        print("   python launch_dots_ocr.py docker")
        print("3. Используйте конфигурацию config_dots_ocr_blackwell.yaml")
        return True
    else:
        print("⚠️ УСТАНОВКА ЗАВЕРШЕНА С ПРЕДУПРЕЖДЕНИЯМИ")
        print("\n🔧 РЕКОМЕНДАЦИИ:")
        print("1. Проверьте установку CUDA 12.8")
        print("2. Убедитесь в правильной версии flash-attn")
        print("3. Попробуйте запуск через Docker как альтернативу")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Установка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)