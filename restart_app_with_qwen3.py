#!/usr/bin/env python3
"""
Скрипт для перезапуска приложения с Qwen3-VL в vLLM режиме
"""

import requests
import time
import subprocess
import sys

def check_qwen3_vllm_health():
    """Проверка готовности Qwen3-VL в vLLM"""
    try:
        response = requests.get("http://localhost:8004/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_models_endpoint():
    """Проверка доступности моделей через API"""
    try:
        response = requests.get("http://localhost:8004/v1/models", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            for model in models_data.get("data", []):
                if "Qwen3-VL" in model["id"]:
                    return True
        return False
    except:
        return False

def main():
    print("🚀 Подготовка к перезапуску приложения с Qwen3-VL")
    print("=" * 60)
    
    # 1. Проверяем статус контейнеров
    print("\n1️⃣ Проверка статуса контейнеров...")
    
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if "qwen-qwen3-vl-2b-instruct-vllm" in result.stdout:
            print("✅ Qwen3-VL контейнер запущен")
        else:
            print("❌ Qwen3-VL контейнер не найден")
            print("💡 Запускаем контейнер...")
            subprocess.run([
                "docker-compose", "-f", "docker-compose-vllm.yml", 
                "up", "-d", "qwen3-vl-2b"
            ])
            time.sleep(10)
    except Exception as e:
        print(f"❌ Ошибка проверки контейнеров: {e}")
    
    # 2. Ожидание готовности Qwen3-VL
    print("\n2️⃣ Ожидание готовности Qwen3-VL...")
    
    max_wait_time = 300  # 5 минут
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        if check_qwen3_vllm_health():
            print("✅ Qwen3-VL health check прошел")
            
            # Дополнительная проверка API моделей
            if check_models_endpoint():
                print("✅ Qwen3-VL API готов к работе")
                break
            else:
                print("⏳ API моделей еще не готов...")
        else:
            print("⏳ Ожидание готовности Qwen3-VL...")
        
        time.sleep(10)
    else:
        print("❌ Qwen3-VL не готов после 5 минут ожидания")
        print("💡 Проверьте логи: docker logs qwen-qwen3-vl-2b-instruct-vllm")
        return False
    
    # 3. Проверка всех доступных моделей
    print("\n3️⃣ Проверка доступных моделей...")
    
    endpoints = {
        "dots.ocr": "http://localhost:8000",
        "Qwen3-VL-2B": "http://localhost:8004"
    }
    
    available_models = []
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f"{endpoint}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {endpoint}")
                available_models.append(name)
            else:
                print(f"❌ {name}: {endpoint}")
        except Exception as e:
            print(f"❌ {name}: {endpoint} - {e}")
    
    if not available_models:
        print("❌ Нет доступных моделей!")
        return False
    
    print(f"\n✅ Доступно моделей: {len(available_models)}")
    
    # 4. Создание отчета о готовности
    print("\n4️⃣ Создание отчета о готовности...")
    
    report = f"""# QWEN3-VL VLLM ИНТЕГРАЦИЯ - ГОТОВНОСТЬ СИСТЕМЫ

## Статус: ✅ ГОТОВО К РАБОТЕ

### Доступные модели:
{chr(10).join([f"- {model}" for model in available_models])}

### Endpoints:
- dots.ocr: http://localhost:8000
- Qwen3-VL-2B: http://localhost:8004

### Команды для запуска:
```bash
# Запуск Streamlit приложения
streamlit run app.py

# Или запуск с определенным портом
streamlit run app.py --server.port 8501
```

### Проверка работы:
1. Откройте приложение в браузере
2. Переключитесь в vLLM режим
3. Выберите модель Qwen3-VL-2B
4. Загрузите изображение для тестирования

### Дата готовности: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    with open("QWEN3_VLLM_READY_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ Отчет сохранен: QWEN3_VLLM_READY_REPORT.md")
    
    # 5. Запуск приложения
    print("\n5️⃣ Готов к запуску приложения!")
    print("=" * 60)
    print("🚀 Система готова! Qwen3-VL доступен в vLLM режиме")
    print("💡 Запустите приложение: streamlit run app.py")
    print("🌐 Или откройте: http://localhost:8501")
    
    # Опционально - автоматический запуск
    user_input = input("\n❓ Запустить приложение автоматически? (y/n): ")
    if user_input.lower() in ['y', 'yes', 'да']:
        print("🚀 Запускаем Streamlit приложение...")
        try:
            subprocess.run(["streamlit", "run", "app.py"], check=True)
        except KeyboardInterrupt:
            print("\n👋 Приложение остановлено пользователем")
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            print("💡 Запустите вручную: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)