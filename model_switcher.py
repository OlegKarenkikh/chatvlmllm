#!/usr/bin/env python3
"""
Простой переключатель моделей для системы OCR
"""

import subprocess
import time
import requests
import sys

def get_current_model():
    """Получение текущей активной модели"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line and ('dots-ocr' in line or 'qwen' in line):
                    parts = line.split('\t')
                    if len(parts) >= 2 and 'Up' in parts[1]:
                        container_name = parts[0]
                        if 'dots-ocr' in container_name:
                            return "dots-ocr", 8000
                        elif 'qwen3' in container_name:
                            return "qwen3-vl", 8004
        
        return None, None
    except:
        return None, None

def check_model_health(port):
    """Проверка здоровья модели"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def switch_to_dots_ocr():
    """Переключение на dots.ocr"""
    print("🔄 Переключение на dots.ocr...")
    
    # Останавливаем все модели
    subprocess.run(["docker", "stop", "dots-ocr-vllm-optimized"], capture_output=True)
    subprocess.run(["docker", "stop", "qwen3-vl-single"], capture_output=True)
    subprocess.run(["docker", "rm", "dots-ocr-vllm-optimized"], capture_output=True)
    subprocess.run(["docker", "rm", "qwen3-vl-single"], capture_output=True)
    
    time.sleep(3)
    
    # Запускаем dots.ocr
    try:
        userprofile = subprocess.check_output(['echo', '%USERPROFILE%'], shell=True, text=True).strip()
        cache_path = f"{userprofile}/.cache/huggingface/hub"
    except:
        cache_path = "~/.cache/huggingface/hub"
    
    command = [
        "docker", "run", "-d",
        "--name", "dots-ocr-vllm-optimized",
        "--restart", "unless-stopped",
        "-p", "8000:8000",
        "--gpus", "all",
        "--shm-size", "8g",
        "-v", f"{cache_path}:/root/.cache/huggingface/hub:rw",
        "-e", "CUDA_VISIBLE_DEVICES=0",
        "vllm/vllm-openai:latest",
        "--model", "rednote-hilab/dots.ocr",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--trust-remote-code",
        "--max-model-len", "8192",
        "--gpu-memory-utilization", "0.85",
        "--dtype", "bfloat16",
        "--enforce-eager",
        "--disable-log-requests"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        print("✅ dots.ocr запущен")
        return True
    else:
        print(f"❌ Ошибка запуска dots.ocr: {result.stderr}")
        return False

def switch_to_qwen3():
    """Переключение на Qwen3-VL"""
    print("🔄 Переключение на Qwen3-VL...")
    
    # Останавливаем все модели
    subprocess.run(["docker", "stop", "dots-ocr-vllm-optimized"], capture_output=True)
    subprocess.run(["docker", "stop", "qwen3-vl-single"], capture_output=True)
    subprocess.run(["docker", "rm", "dots-ocr-vllm-optimized"], capture_output=True)
    subprocess.run(["docker", "rm", "qwen3-vl-single"], capture_output=True)
    
    time.sleep(3)
    
    # Запускаем Qwen3-VL
    try:
        userprofile = subprocess.check_output(['echo', '%USERPROFILE%'], shell=True, text=True).strip()
        cache_path = f"{userprofile}/.cache/huggingface/hub"
    except:
        cache_path = "~/.cache/huggingface/hub"
    
    command = [
        "docker", "run", "-d",
        "--name", "qwen3-vl-single",
        "--restart", "unless-stopped",
        "-p", "8004:8000",
        "--gpus", "all",
        "--shm-size", "8g",
        "-v", f"{cache_path}:/root/.cache/huggingface/hub:rw",
        "-e", "CUDA_VISIBLE_DEVICES=0",
        "vllm/vllm-openai:latest",
        "--model", "Qwen/Qwen3-VL-2B-Instruct",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--trust-remote-code",
        "--max-model-len", "4096",
        "--gpu-memory-utilization", "0.8",
        "--dtype", "bfloat16",
        "--enforce-eager",
        "--disable-log-requests"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    
    if result.returncode == 0:
        print("✅ Qwen3-VL запущен")
        return True
    else:
        print(f"❌ Ошибка запуска Qwen3-VL: {result.stderr}")
        return False

def wait_for_model(port, timeout=300):
    """Ожидание готовности модели"""
    print(f"⏳ Ожидание готовности модели на порту {port}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_model_health(port):
            print("✅ Модель готова!")
            return True
        time.sleep(5)
    
    print("❌ Модель не готова после ожидания")
    return False

def show_status():
    """Показать текущий статус"""
    print("📊 Статус системы OCR")
    print("=" * 30)
    
    current_model, port = get_current_model()
    
    if current_model:
        healthy = check_model_health(port)
        status_icon = "✅" if healthy else "❌"
        print(f"{status_icon} Активная модель: {current_model}")
        print(f"   Порт: {port}")
        print(f"   Статус: {'Здорова' if healthy else 'Проблемы'}")
        
        if healthy:
            try:
                response = requests.get(f"http://localhost:{port}/v1/models", timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    for model in models_data.get("data", []):
                        print(f"   Модель: {model['id']}")
                        print(f"   Макс. токенов: {model.get('max_model_len', 'N/A')}")
            except:
                pass
    else:
        print("❌ Нет активной модели")
    
    print(f"\n💡 Доступные команды:")
    print(f"   python model_switcher.py dots-ocr    # Переключиться на dots.ocr")
    print(f"   python model_switcher.py qwen3-vl    # Переключиться на Qwen3-VL")
    print(f"   python model_switcher.py status      # Показать статус")

def main():
    if len(sys.argv) < 2:
        show_status()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_status()
    
    elif command == "dots-ocr":
        success = switch_to_dots_ocr()
        if success:
            if wait_for_model(8000):
                print("🎉 Переключение на dots.ocr завершено!")
                print("🚀 Запуск приложения: streamlit run app.py")
            else:
                print("⚠️ Модель запущена, но еще не готова")
        else:
            print("❌ Не удалось переключиться на dots.ocr")
    
    elif command == "qwen3-vl":
        success = switch_to_qwen3()
        if success:
            if wait_for_model(8004):
                print("🎉 Переключение на Qwen3-VL завершено!")
                print("🚀 Запуск приложения: streamlit run app.py")
                print("⚠️ Не забудьте обновить vllm_streamlit_adapter.py для порта 8004")
            else:
                print("⚠️ Модель запущена, но еще не готова")
        else:
            print("❌ Не удалось переключиться на Qwen3-VL")
    
    else:
        print("❌ Неизвестная команда")
        print("💡 Доступные команды: dots-ocr, qwen3-vl, status")

if __name__ == "__main__":
    main()