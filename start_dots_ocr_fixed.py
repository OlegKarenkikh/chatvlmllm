#!/usr/bin/env python3
"""
Исправленный запуск dots.ocr с оптимизированными параметрами памяти
"""

import subprocess
import time
import requests
import os

def run_command(command):
    """Выполнение команды"""
    print(f"🔄 {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        if e.stderr:
            print(f"❌ {e.stderr}")
        return False

def main():
    """Основная функция"""
    print("🚀 ИСПРАВЛЕННЫЙ ЗАПУСК DOTS.OCR")
    print("=" * 35)
    
    # Остановка существующих контейнеров
    print("🛑 Остановка существующих контейнеров...")
    run_command("docker stop dots-ocr-simple")
    run_command("docker rm dots-ocr-simple")
    
    # Путь к кешу
    cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
    print(f"📁 Путь к кешу: {cache_path}")
    
    # Запуск dots.ocr с исправленными параметрами памяти
    print("\n🚀 Запуск dots.ocr с оптимизированными параметрами...")
    
    docker_command = f"""
    docker run -d \
        --gpus all \
        --name dots-ocr-fixed \
        --restart unless-stopped \
        -p 8000:8000 \
        -v {cache_path}:/root/.cache/huggingface/hub:ro \
        --shm-size=8g \
        vllm/vllm-openai:latest \
        --model rednote-hilab/dots.ocr \
        --trust-remote-code \
        --max-model-len 1024 \
        --gpu-memory-utilization 0.85 \
        --host 0.0.0.0 \
        --port 8000 \
        --disable-log-requests \
        --enforce-eager
    """.strip().replace('\n', ' ').replace('\\', '')
    
    if run_command(docker_command):
        print("✅ dots.ocr контейнер запущен с исправленными параметрами")
        
        # Ожидание запуска
        print("\n⏳ Ожидание запуска сервера (может занять 3-5 минут)...")
        max_attempts = 25
        
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ dots.ocr готова к работе!")
                    
                    # Проверка models endpoint
                    try:
                        models_response = requests.get("http://localhost:8000/v1/models", timeout=5)
                        if models_response.status_code == 200:
                            models_data = models_response.json()
                            print(f"📊 Доступные модели: {len(models_data.get('data', []))}")
                            for model in models_data.get('data', []):
                                print(f"   • {model.get('id', 'unknown')}")
                    except Exception as e:
                        print(f"⚠️ Не удалось получить список моделей: {e}")
                    
                    break
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                print(f"⚠️ Ошибка проверки: {e}")
            
            print(f"⏳ Попытка {attempt + 1}/{max_attempts} (ждем еще 15 сек...)")
            time.sleep(15)
        else:
            print("❌ Сервер не запустился")
            print("📋 Проверьте логи: docker logs dots-ocr-fixed")
            return
        
        print("\n🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        print("=" * 25)
        print("📡 dots.ocr доступна на: http://localhost:8000")
        print("📋 Документация: http://localhost:8000/docs")
        print("🔧 Управление:")
        print("   docker logs dots-ocr-fixed     # Логи")
        print("   docker stop dots-ocr-fixed     # Остановка")
        print("   docker restart dots-ocr-fixed  # Перезапуск")
        
        print("\n💡 ИЗМЕНЕНИЯ В ПАРАМЕТРАХ:")
        print("   • max-model-len: 2048 → 1024 (меньше памяти)")
        print("   • gpu-memory-utilization: 0.6 → 0.85 (больше для модели)")
        print("   • enforce-eager: включен (стабильность)")
        print("   • disable-log-requests: отключены лишние логи")
        
    else:
        print("❌ Не удалось запустить контейнер")

if __name__ == "__main__":
    main()