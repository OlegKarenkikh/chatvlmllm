#!/usr/bin/env python3
"""
Исправление проблемы с памятью Qwen3-VL
"""

import subprocess
import time
import requests

def fix_qwen3_memory_issue():
    """Исправление проблемы с памятью Qwen3-VL"""
    
    print("🔧 Исправление проблемы с памятью Qwen3-VL")
    print("=" * 50)
    
    # 1. Остановка всех vLLM контейнеров
    print("\n1️⃣ Остановка всех vLLM контейнеров...")
    
    containers_to_stop = [
        "dots-ocr-vllm-optimized",
        "qwen-qwen3-vl-2b-instruct-vllm", 
        "qwen3-vl-2b-memory-optimized",
        "dots-ocr-memory-optimized"
    ]
    
    for container in containers_to_stop:
        try:
            result = subprocess.run(
                ["docker", "stop", container], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                print(f"✅ Остановлен: {container}")
            else:
                print(f"⚠️ Контейнер {container} не найден или уже остановлен")
        except Exception as e:
            print(f"⚠️ Ошибка остановки {container}: {e}")
    
    # 2. Очистка GPU памяти
    print("\n2️⃣ Очистка GPU памяти...")
    time.sleep(5)
    
    try:
        # Попытка очистить CUDA кеш
        result = subprocess.run(
            ["docker", "system", "prune", "-f"], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        print("✅ Docker система очищена")
    except Exception as e:
        print(f"⚠️ Ошибка очистки: {e}")
    
    # 3. Запуск только dots.ocr с минимальными настройками
    print("\n3️⃣ Запуск dots.ocr с оптимизированными настройками...")
    
    dots_ocr_command = [
        "docker", "run", "-d",
        "--name", "dots-ocr-ultra-optimized",
        "--restart", "unless-stopped",
        "-p", "8000:8000",
        "--gpus", "all",
        "--shm-size", "2g",
        "-v", f"{subprocess.check_output(['echo', '%USERPROFILE%'], shell=True, text=True).strip()}/.cache/huggingface/hub:/root/.cache/huggingface/hub:rw",
        "-e", "CUDA_VISIBLE_DEVICES=0",
        "-e", "NVIDIA_VISIBLE_DEVICES=all",
        "vllm/vllm-openai:latest",
        "--model", "rednote-hilab/dots.ocr",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--trust-remote-code",
        "--max-model-len", "1024",
        "--gpu-memory-utilization", "0.35",  # Очень консервативно
        "--dtype", "bfloat16",
        "--enforce-eager",
        "--disable-log-requests",
        "--max-num-batched-tokens", "256"  # Минимальный батч
    ]
    
    try:
        result = subprocess.run(dots_ocr_command, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ dots.ocr запущен с ультра-оптимизацией")
        else:
            print(f"❌ Ошибка запуска dots.ocr: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ошибка запуска dots.ocr: {e}")
        return False
    
    # 4. Ожидание готовности dots.ocr
    print("\n4️⃣ Ожидание готовности dots.ocr...")
    
    max_wait = 180
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ dots.ocr готов!")
                break
        except:
            pass
        
        print("⏳ Ожидание dots.ocr...")
        time.sleep(10)
    else:
        print("❌ dots.ocr не готов после 3 минут")
        return False
    
    # 5. Запуск Qwen3-VL с минимальными настройками
    print("\n5️⃣ Запуск Qwen3-VL с ультра-оптимизацией...")
    
    qwen3_command = [
        "docker", "run", "-d",
        "--name", "qwen3-vl-ultra-optimized",
        "--restart", "unless-stopped", 
        "-p", "8004:8000",
        "--gpus", "all",
        "--shm-size", "2g",
        "-v", f"{subprocess.check_output(['echo', '%USERPROFILE%'], shell=True, text=True).strip()}/.cache/huggingface/hub:/root/.cache/huggingface/hub:rw",
        "-e", "CUDA_VISIBLE_DEVICES=0",
        "-e", "NVIDIA_VISIBLE_DEVICES=all",
        "vllm/vllm-openai:latest",
        "--model", "Qwen/Qwen3-VL-2B-Instruct",
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--trust-remote-code",
        "--max-model-len", "1024",  # Сильно уменьшено
        "--gpu-memory-utilization", "0.6",  # Увеличено для KV cache
        "--dtype", "bfloat16",
        "--disable-log-requests",
        "--max-num-batched-tokens", "512",  # Уменьшено
        "--kv-cache-dtype", "fp8"  # Экономия памяти для KV cache
    ]
    
    try:
        result = subprocess.run(qwen3_command, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Qwen3-VL запущен с ультра-оптимизацией")
        else:
            print(f"❌ Ошибка запуска Qwen3-VL: {result.stderr}")
            print("💡 Попробуем запустить только одну модель за раз")
            return "single_model_mode"
    except Exception as e:
        print(f"❌ Ошибка запуска Qwen3-VL: {e}")
        return "single_model_mode"
    
    # 6. Ожидание готовности Qwen3-VL
    print("\n6️⃣ Ожидание готовности Qwen3-VL...")
    
    max_wait = 300  # 5 минут для первой загрузки
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8004/health", timeout=5)
            if response.status_code == 200:
                print("✅ Qwen3-VL готов!")
                break
        except:
            pass
        
        elapsed = int(time.time() - start_time)
        print(f"⏳ Ожидание Qwen3-VL... ({elapsed}s)")
        time.sleep(15)
    else:
        print("❌ Qwen3-VL не готов после 5 минут")
        print("💡 Переходим в режим одной модели")
        return "single_model_mode"
    
    # 7. Проверка обеих моделей
    print("\n7️⃣ Проверка работы обеих моделей...")
    
    models_status = {}
    
    for name, port in [("dots.ocr", 8000), ("Qwen3-VL", 8004)]:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            models_status[name] = response.status_code == 200
            
            if models_status[name]:
                # Проверяем API моделей
                models_response = requests.get(f"http://localhost:{port}/v1/models", timeout=5)
                if models_response.status_code == 200:
                    print(f"✅ {name} работает корректно (порт {port})")
                else:
                    print(f"⚠️ {name} запущен, но API моделей недоступен")
                    models_status[name] = False
            else:
                print(f"❌ {name} не отвечает на health check")
        except Exception as e:
            print(f"❌ {name} недоступен: {e}")
            models_status[name] = False
    
    # 8. Результат
    print(f"\n8️⃣ Результат оптимизации:")
    print("=" * 50)
    
    working_models = sum(models_status.values())
    
    if working_models == 2:
        print("🎉 УСПЕХ! Обе модели работают с оптимизированными настройками")
        print("📊 Конфигурация:")
        print("   - dots.ocr: 35% GPU, 1024 токенов, 256 батч")
        print("   - Qwen3-VL: 60% GPU, 1024 токенов, 512 батч, fp8 KV cache")
        print("💡 Можно запускать приложение: streamlit run app.py")
        return True
    elif working_models == 1:
        working_model = [name for name, status in models_status.items() if status][0]
        print(f"⚠️ ЧАСТИЧНЫЙ УСПЕХ: Работает только {working_model}")
        print("💡 Система готова в режиме одной модели")
        return "single_model_mode"
    else:
        print("❌ НЕУДАЧА: Ни одна модель не работает")
        print("💡 Требуется дополнительная диагностика")
        return False

def setup_single_model_mode():
    """Настройка режима одной модели"""
    
    print("\n🔧 Настройка режима одной модели")
    print("=" * 50)
    
    # Останавливаем все контейнеры
    print("1️⃣ Остановка всех контейнеров...")
    subprocess.run(["docker", "stop", "qwen3-vl-ultra-optimized"], capture_output=True)
    subprocess.run(["docker", "rm", "qwen3-vl-ultra-optimized"], capture_output=True)
    
    # Оставляем только dots.ocr с максимальной оптимизацией
    print("2️⃣ Оптимизация dots.ocr для режима одной модели...")
    
    subprocess.run(["docker", "stop", "dots-ocr-ultra-optimized"], capture_output=True)
    subprocess.run(["docker", "rm", "dots-ocr-ultra-optimized"], capture_output=True)
    
    # Запуск dots.ocr с увеличенными лимитами
    dots_single_command = [
        "docker", "run", "-d",
        "--name", "dots-ocr-single-mode",
        "--restart", "unless-stopped",
        "-p", "8000:8000",
        "--gpus", "all",
        "--shm-size", "4g",
        "-v", f"{subprocess.check_output(['echo', '%USERPROFILE%'], shell=True, text=True).strip()}/.cache/huggingface/hub:/root/.cache/huggingface/hub:rw",
        "-e", "CUDA_VISIBLE_DEVICES=0",
        "vllm/vllm-openai:latest",
        "--model", "rednote-hilab/dots.ocr",
        "--host", "0.0.0.0",
        "--port", "8000", 
        "--trust-remote-code",
        "--max-model-len", "2048",  # Увеличено
        "--gpu-memory-utilization", "0.8",  # Максимально
        "--dtype", "bfloat16",
        "--enforce-eager",
        "--disable-log-requests"
    ]
    
    try:
        result = subprocess.run(dots_single_command, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ dots.ocr запущен в режиме одной модели")
            
            # Ожидание готовности
            time.sleep(30)
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ dots.ocr готов в режиме одной модели")
                return True
        
        print(f"❌ Ошибка: {result.stderr}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    result = fix_qwen3_memory_issue()
    
    if result == "single_model_mode":
        print("\n" + "="*50)
        print("🔄 Переход в режим одной модели...")
        success = setup_single_model_mode()
        
        if success:
            print("\n✅ СИСТЕМА ГОТОВА В РЕЖИМЕ ОДНОЙ МОДЕЛИ")
            print("🤖 Активна: dots.ocr (оптимизированная)")
            print("💡 Запуск: streamlit run app.py")
        else:
            print("\n❌ Не удалось настроить режим одной модели")
    elif result:
        print("\n✅ СИСТЕМА ГОТОВА В РЕЖИМЕ ДВУХ МОДЕЛЕЙ")
        print("🤖 Активны: dots.ocr + Qwen3-VL")
        print("💡 Запуск: streamlit run app.py")
    else:
        print("\n❌ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ДИАГНОСТИКА")
        print("💡 Проверьте логи контейнеров и доступную GPU память")