#!/usr/bin/env python3
"""
Быстрый запуск системы ChatVLMLLM
Единообразный запуск на стандартных портах
"""

import subprocess
import time
import requests
import sys
import os

def run_command(cmd, shell=True):
    """Выполнение команды с выводом"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_port(port, timeout=5):
    """Проверка доступности порта"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Запуск системы ChatVLMLLM")
    print("=" * 50)
    
    # 1. Проверяем и останавливаем существующие процессы
    print("1️⃣ Очистка существующих процессов...")
    
    # Останавливаем Streamlit
    success, stdout, stderr = run_command("taskkill /F /IM streamlit.exe 2>nul")
    if success:
        print("   ✅ Streamlit процессы остановлены")
    
    # Останавливаем и удаляем ВСЕ старые контейнеры vLLM
    old_containers = [
        "dots-ocr-stable", "dots-ocr-optimized", "dots-ocr-performance", 
        "dots-ocr-fixed", "qwen-qwen3-vl-2b-instruct-vllm", 
        "qwen-qwen2-vl-2b-instruct-vllm", "microsoft-phi-3-5-vision-instruct-vllm"
    ]
    
    for container in old_containers:
        run_command(f"docker stop {container} 2>nul")
        run_command(f"docker rm {container} 2>nul")
    
    print("   ✅ Старые контейнеры очищены")
    
    # 2. Запускаем dots.ocr контейнер
    print("\n2️⃣ Запуск dots.ocr модели...")
    
    # Проверяем, не запущен ли уже правильный контейнер
    success, stdout, stderr = run_command("docker ps --filter name=dots-ocr-fixed --format '{{.Names}}'")
    if "dots-ocr-fixed" in stdout:
        print("   ✅ Контейнер dots-ocr-fixed уже запущен")
    else:
        # Останавливаем и удаляем если есть
        run_command("docker stop dots-ocr-fixed 2>nul")
        run_command("docker rm dots-ocr-fixed 2>nul")
        
        # Запускаем новый контейнер
        docker_cmd = [
            "docker", "run", "-d",
            "--name", "dots-ocr-fixed",
            "--gpus", "all",
            "-p", "8000:8000",
            "--shm-size=8g",
            "-v", "C:/Users/Colorful/.cache/huggingface:/root/.cache/huggingface:rw",
            "-e", "CUDA_VISIBLE_DEVICES=0",
            "-e", "HF_HOME=/root/.cache/huggingface",
            "-e", "TRANSFORMERS_CACHE=/root/.cache/huggingface/hub",
            "vllm/vllm-openai:latest",
            "--model", "rednote-hilab/dots.ocr",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--trust-remote-code",
            "--max-model-len", "4096",
            "--gpu-memory-utilization", "0.85",
            "--dtype", "bfloat16",
            "--enforce-eager",
            "--disable-log-requests"
        ]
        
        success, stdout, stderr = run_command(docker_cmd, shell=False)
        if success:
            print("   ✅ Контейнер dots-ocr-fixed запущен")
        else:
            print(f"   ❌ Ошибка запуска контейнера: {stderr}")
            return False
    
    # 3. Ожидание готовности API
    print("\n3️⃣ Ожидание готовности модели...")
    
    max_wait = 180  # 3 минуты (увеличено с 2 минут)
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if check_port(8000):
            print("   ✅ API dots.ocr готов!")
            break
        
        elapsed = int(time.time() - start_time)
        print(f"   ⏳ Загрузка модели... ({elapsed}с/{max_wait}с)")
        time.sleep(5)
    else:
        print("   ❌ Таймаут загрузки модели")
        return False
    
    # 4. Запуск Streamlit приложения
    print("\n4️⃣ Запуск Streamlit приложения...")
    
    # Очищаем кеши
    cache_dirs = [
        os.path.expanduser("~/.streamlit"),
        "__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                if os.path.isdir(cache_dir):
                    import shutil
                    shutil.rmtree(cache_dir)
                else:
                    os.remove(cache_dir)
                print(f"   ✅ Очищен кеш: {cache_dir}")
            except:
                pass
    
    # Запускаем Streamlit
    print("   🚀 Запуск Streamlit на http://localhost:8501...")
    
    try:
        # Запускаем в фоновом режиме
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Ждем запуска
        time.sleep(10)
        
        # Проверяем доступность
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print("   ✅ Streamlit запущен успешно!")
            else:
                print(f"   ⚠️ Streamlit отвечает с кодом: {response.status_code}")
        except:
            print("   ⚠️ Streamlit запускается... (может потребоваться время)")
        
    except Exception as e:
        print(f"   ❌ Ошибка запуска Streamlit: {e}")
        return False
    
    # 5. Финальная проверка
    print("\n5️⃣ Финальная проверка системы...")
    
    # Проверяем GPU
    success, stdout, stderr = run_command("nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits")
    if success and stdout.strip():
        memory_used = int(stdout.strip())
        if memory_used > 5000:  # Больше 5GB
            print(f"   ✅ GPU активен: {memory_used}MB используется")
        else:
            print(f"   ⚠️ GPU память: {memory_used}MB (модель может еще загружаться)")
    
    # Проверяем контейнер
    success, stdout, stderr = run_command("docker ps --filter name=dots-ocr-fixed --format '{{.Status}}'")
    if "Up" in stdout:
        print("   ✅ Контейнер dots-ocr-fixed работает")
    else:
        print("   ❌ Проблема с контейнером")
    
    print("\n" + "=" * 50)
    print("🎉 СИСТЕМА ЗАПУЩЕНА!")
    print()
    print("📱 Интерфейсы:")
    print("   • Streamlit: http://localhost:8501")
    print("   • dots.ocr API: http://localhost:8000")
    print()
    print("💡 Инструкции:")
    print("   1. Откройте http://localhost:8501")
    print("   2. Если модель не обнаруживается - нажмите '🔄 Обновить статус моделей'")
    print("   3. Выберите режим OCR или Чат")
    print("   4. Загрузите изображение и начинайте работу!")
    print()
    print("🔧 Управление:")
    print("   • Остановка: Ctrl+C в терминале Streamlit")
    print("   • Логи контейнера: docker logs dots-ocr-fixed")
    print("   • Перезапуск: python start_system.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Ошибка запуска системы")
        sys.exit(1)
    else:
        print("\n✅ Система готова к работе!")
        sys.exit(0)