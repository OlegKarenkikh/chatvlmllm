#!/usr/bin/env python3
"""
Быстрый запуск приоритетных моделей vLLM
"""

import subprocess
import time
import requests
import json
import os

def run_command(command):
    """Выполнение команды"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() if e.stderr else str(e)

def check_model_health(port):
    """Проверка готовности модели"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Основная функция"""
    print("🚀 БЫСТРЫЙ ЗАПУСК ПРИОРИТЕТНЫХ МОДЕЛЕЙ")
    print("=" * 40)
    
    # Загрузка конфигураций
    try:
        with open('vllm_models_config.json', 'r', encoding='utf-8') as f:
            configs = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигураций: {e}")
        return
    
    # Приоритетные модели для запуска
    priority_models = [
        "rednote-hilab/dots.ocr",  # Уже работает
        "stepfun-ai/GOT-OCR2_0",  # OCR модель
        "Qwen/Qwen3-VL-2B-Instruct"  # Легкая VLM модель
    ]
    
    cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
    
    print(f"📁 Путь к кешу: {cache_path}")
    print(f"🎯 Запуск {len(priority_models)} приоритетных моделей...")
    
    launched_models = []
    
    for model_name in priority_models:
        if model_name not in configs:
            print(f"⚠️ {model_name} - не найдена в конфигурации")
            continue
        
        config = configs[model_name]
        container_name = config['container_name']
        port = config['port']
        
        print(f"\n🔄 Запуск {model_name}...")
        print(f"   Контейнер: {container_name}")
        print(f"   Порт: {port}")
        print(f"   Размер: {config['size_gb']} ГБ")
        
        # Проверка, не запущена ли уже
        if check_model_health(port):
            print(f"   ✅ Уже запущена и готова!")
            launched_models.append(model_name)
            continue
        
        # Остановка существующего контейнера
        run_command(f"docker stop {container_name}")
        run_command(f"docker rm {container_name}")
        
        # Формирование команды запуска
        vllm_params = config['vllm_params']
        
        docker_command = f"""
        docker run -d \
            --gpus all \
            --name {container_name} \
            --restart unless-stopped \
            -p {port}:{port} \
            -v {cache_path}:/root/.cache/huggingface/hub:ro \
            --shm-size=8g \
            vllm/vllm-openai:latest \
            --model {model_name} \
            --trust-remote-code \
            --max-model-len {vllm_params['max_model_len']} \
            --gpu-memory-utilization {vllm_params['gpu_memory_utilization']} \
            --host 0.0.0.0 \
            --port {port} \
            --disable-log-requests
        """.strip().replace('\n', ' ').replace('\\', '')
        
        if vllm_params.get('enforce_eager'):
            docker_command += " --enforce-eager"
        
        # Запуск контейнера
        success, output = run_command(docker_command)
        
        if success:
            print(f"   ✅ Контейнер запущен")
            
            # Ожидание готовности (максимум 5 минут)
            print(f"   ⏳ Ожидание готовности...")
            max_attempts = 30
            
            for attempt in range(max_attempts):
                if check_model_health(port):
                    print(f"   🎉 Модель готова! ({attempt * 10} сек)")
                    launched_models.append(model_name)
                    break
                
                if attempt % 3 == 0:  # Каждые 30 секунд
                    print(f"   ⏳ Попытка {attempt + 1}/{max_attempts}...")
                
                time.sleep(10)
            else:
                print(f"   ❌ Модель не готова за 5 минут")
                print(f"   💡 Проверьте логи: docker logs {container_name}")
        else:
            print(f"   ❌ Ошибка запуска: {output}")
    
    # Итоговый отчет
    print(f"\n📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 20)
    print(f"🎯 Запланировано: {len(priority_models)} моделей")
    print(f"✅ Успешно запущено: {len(launched_models)} моделей")
    
    if launched_models:
        print(f"\n🟢 ГОТОВЫЕ МОДЕЛИ:")
        for model_name in launched_models:
            config = configs[model_name]
            print(f"   • {model_name}")
            print(f"     URL: http://localhost:{config['port']}")
            print(f"     Категория: {config['category']}")
        
        print(f"\n💡 СЛЕДУЮЩИЕ ШАГИ:")
        print("   1. Тестирование моделей:")
        print("      python test_all_vllm_models.py")
        print("   2. Создание клиента:")
        print("      python multi_model_launcher.py --create-client")
        print("   3. Проверка статуса:")
        print("      python multi_model_launcher.py --status")
    else:
        print(f"\n❌ Ни одна модель не запущена")
        print(f"💡 Проверьте:")
        print("   • Доступность GPU: nvidia-smi")
        print("   • Docker контейнеры: docker ps")
        print("   • Логи контейнеров: docker logs <container_name>")

if __name__ == "__main__":
    main()