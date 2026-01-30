#!/usr/bin/env python3
"""
Отладка одной модели с детальными логами
"""

import subprocess
import time
import requests
import os

def run_command(command):
    """Выполнение команды"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() if e.stderr else str(e)

def test_qwen2_vl_2b():
    """Тестирование Qwen2-VL-2B-Instruct с детальными логами"""
    
    cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
    model_name = "Qwen/Qwen2-VL-2B-Instruct"
    container_name = "debug-qwen2-vl-2b"
    port = 8015
    
    print(f"🧪 ОТЛАДКА: {model_name}")
    print("=" * 50)
    
    # Очистка предыдущих контейнеров
    run_command(f"docker stop {container_name}")
    run_command(f"docker rm {container_name}")
    
    # Формирование команды Docker
    docker_command = f"""
    docker run -d \
        --gpus all \
        --name {container_name} \
        -p {port}:{port} \
        -v {cache_path}:/root/.cache/huggingface/hub:ro \
        --shm-size=8g \
        vllm/vllm-openai:latest \
        --model {model_name} \
        --trust-remote-code \
        --max-model-len 2048 \
        --gpu-memory-utilization 0.7 \
        --host 0.0.0.0 \
        --port {port} \
        --disable-log-requests
    """.strip().replace('\n', ' ').replace('\\', '')
    
    print(f"🚀 Запуск контейнера...")
    print(f"Команда: {docker_command}")
    
    # Запуск контейнера
    success, output = run_command(docker_command)
    
    if not success:
        print(f"❌ Ошибка запуска: {output}")
        return
    
    print(f"📦 Контейнер запущен: {output}")
    
    # Мониторинг логов в реальном времени
    print(f"\n📋 МОНИТОРИНГ ЛОГОВ:")
    print("-" * 30)
    
    start_time = time.time()
    timeout = 300  # 5 минут
    
    while time.time() - start_time < timeout:
        # Получение последних логов
        success_log, logs = run_command(f"docker logs {container_name} --tail 5")
        
        if success_log and logs:
            current_time = int(time.time() - start_time)
            print(f"\n[{current_time}s] Последние логи:")
            for line in logs.split('\n'):
                if line.strip():
                    print(f"  {line}")
            
            # Проверка на ошибки
            if "ERROR" in logs or "Error" in logs:
                print(f"\n❌ ОБНАРУЖЕНА ОШИБКА!")
                break
            
            # Проверка готовности
            if "Application startup complete" in logs or "Uvicorn running" in logs:
                print(f"\n✅ Сервер готов!")
                break
        
        # Проверка health endpoint
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"\n✅ Health check успешен!")
                break
        except:
            pass
        
        time.sleep(10)
    
    # Финальные логи
    print(f"\n📋 ФИНАЛЬНЫЕ ЛОГИ:")
    print("-" * 20)
    success_log, logs = run_command(f"docker logs {container_name}")
    if success_log:
        print(logs)
    
    # Очистка
    print(f"\n🧹 Очистка...")
    run_command(f"docker stop {container_name}")
    run_command(f"docker rm {container_name}")

if __name__ == "__main__":
    test_qwen2_vl_2b()