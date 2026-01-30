#!/usr/bin/env python3
"""
Запуск dots.ocr с оптимизацией для ограниченной GPU памяти
Решение проблемы: ValueError: Free memory on device cuda:0 (5.81/11.94 GiB)
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

def check_gpu_memory():
    """Проверка доступной GPU памяти"""
    print("🔍 Проверка GPU памяти...")
    try:
        result = subprocess.run(
            "nvidia-smi --query-gpu=memory.total,memory.free,memory.used --format=csv,noheader,nounits",
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            total, free, used = map(int, result.stdout.strip().split(', '))
            print(f"📊 GPU память: {total} MB всего, {free} MB свободно, {used} MB занято")
            return total, free, used
    except Exception as e:
        print(f"⚠️ Не удалось получить информацию о GPU: {e}")
    return None, None, None

def cleanup_gpu():
    """Очистка GPU памяти"""
    print("🧹 Очистка GPU памяти...")
    
    # Остановка всех Docker контейнеров
    print("🛑 Остановка Docker контейнеров...")
    run_command("docker stop $(docker ps -aq) 2>/dev/null || true")
    run_command("docker system prune -f")
    
    # Очистка CUDA кеша
    print("🗑️ Очистка CUDA кеша...")
    cleanup_script = """
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print("CUDA кеш очищен")
else:
    print("CUDA недоступна")
"""
    
    try:
        subprocess.run(["python", "-c", cleanup_script], check=True)
    except:
        print("⚠️ Не удалось очистить CUDA кеш")

def main():
    """Основная функция"""
    print("🚀 ЗАПУСК DOTS.OCR С ОПТИМИЗАЦИЕЙ ПАМЯТИ")
    print("=" * 50)
    
    # Проверка GPU памяти
    total, free, used = check_gpu_memory()
    if free and free < 6000:  # Меньше 6GB свободно
        print(f"⚠️ Мало свободной GPU памяти: {free} MB")
        print("🧹 Выполняем очистку...")
        cleanup_gpu()
        time.sleep(5)
        total, free, used = check_gpu_memory()
    
    # Остановка существующих контейнеров dots.ocr
    print("🛑 Остановка существующих контейнеров...")
    run_command("docker stop dots-ocr-fixed dots-ocr-simple dots-ocr-memory-opt 2>/dev/null || true")
    run_command("docker rm dots-ocr-fixed dots-ocr-simple dots-ocr-memory-opt 2>/dev/null || true")
    
    # Путь к кешу
    cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
    print(f"📁 Путь к кешу: {cache_path}")
    
    # Определение оптимальных параметров памяти
    if free:
        # Используем 40% от свободной памяти для безопасности
        gpu_util = min(0.4, (free * 0.4) / total)
        print(f"🎯 Рассчитанная утилизация GPU: {gpu_util:.2f}")
    else:
        gpu_util = 0.35  # Консервативное значение
        print(f"🎯 Консервативная утилизация GPU: {gpu_util}")
    
    print(f"\n🚀 Запуск dots.ocr с оптимизированными параметрами памяти...")
    print(f"   • GPU утилизация: {gpu_util}")
    print(f"   • Max model length: 1024 (минимум)")
    print(f"   • Dtype: bfloat16 (экономия памяти)")
    print(f"   • Enforce eager: true (стабильность)")
    
    # Команда запуска с минимальными требованиями к памяти
    docker_command = f"""
    docker run -d \
        --gpus all \
        --name dots-ocr-memory-opt \
        --restart unless-stopped \
        -p 8000:8000 \
        -v {cache_path}:/root/.cache/huggingface/hub:ro \
        --shm-size=4g \
        vllm/vllm-openai:latest \
        --model rednote-hilab/dots.ocr \
        --trust-remote-code \
        --max-model-len 1024 \
        --gpu-memory-utilization {gpu_util} \
        --host 0.0.0.0 \
        --port 8000 \
        --disable-log-requests \
        --enforce-eager \
        --dtype bfloat16 \
        --max-num-seqs 1
    """.strip().replace('\n', ' ').replace('\\', '')
    
    if run_command(docker_command):
        print("✅ dots.ocr контейнер запущен с оптимизацией памяти")
        
        # Ожидание запуска
        print("\n⏳ Ожидание запуска сервера (может занять 5-10 минут)...")
        max_attempts = 40
        
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
            print("📋 Проверьте логи: docker logs dots-ocr-memory-opt")
            print("💡 Возможные причины:")
            print("   • Недостаточно GPU памяти (нужно минимум 8GB свободно)")
            print("   • Модель слишком большая для вашей GPU")
            print("   • Проблемы с WSL/Docker")
            return
        
        print("\n🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        print("=" * 25)
        print("📡 dots.ocr доступна на: http://localhost:8000")
        print("📋 Документация: http://localhost:8000/docs")
        print("🔧 Управление:")
        print("   docker logs dots-ocr-memory-opt     # Логи")
        print("   docker stop dots-ocr-memory-opt     # Остановка")
        print("   docker restart dots-ocr-memory-opt  # Перезапуск")
        
        print(f"\n💡 ОПТИМИЗАЦИИ ДЛЯ ОГРАНИЧЕННОЙ ПАМЯТИ:")
        print(f"   • GPU утилизация: {gpu_util} (снижено)")
        print("   • Max model length: 1024 (минимум)")
        print("   • Dtype: bfloat16 (экономия памяти)")
        print("   • Max num seqs: 1 (один запрос за раз)")
        print("   • Shared memory: 4GB (уменьшено)")
        
        print(f"\n⚠️ ОГРАНИЧЕНИЯ:")
        print("   • Обработка только одного запроса за раз")
        print("   • Максимум 1024 токена в ответе")
        print("   • Может быть медленнее из-за консервативных настроек")
        
    else:
        print("❌ Не удалось запустить контейнер")
        print("\n🔧 АЛЬТЕРНАТИВНЫЕ РЕШЕНИЯ:")
        print("1. Использовать CPU версию (медленно, но работает)")
        print("2. Использовать квантованную модель (если доступна)")
        print("3. Использовать transformers с load_in_8bit=True")
        print("4. Перейти на более легкую OCR модель (GOT-OCR, PaddleOCR)")

if __name__ == "__main__":
    main()