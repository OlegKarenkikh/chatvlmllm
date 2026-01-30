#!/usr/bin/env python3
"""
Тест интеграции Streamlit с vLLM
"""

import requests
import time
import subprocess
import sys

def check_vllm_server():
    """Проверка vLLM сервера"""
    print("🔍 Проверка vLLM сервера...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ vLLM сервер работает")
            
            # Проверка моделей
            models_response = requests.get("http://localhost:8000/v1/models", timeout=5)
            if models_response.status_code == 200:
                models = models_response.json()
                print(f"✅ Доступно моделей: {len(models.get('data', []))}")
                for model in models.get('data', []):
                    print(f"   • {model.get('id', 'unknown')}")
                return True
        else:
            print(f"❌ vLLM сервер недоступен: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка подключения к vLLM: {e}")
    
    return False

def check_streamlit_interfaces():
    """Проверка Streamlit интерфейсов"""
    print("\n🌐 Проверка Streamlit интерфейсов...")
    
    interfaces = [
        ("Основной интерфейс", "http://localhost:8501"),
        ("vLLM тестовый интерфейс", "http://localhost:8502")
    ]
    
    working_interfaces = []
    
    for name, url in interfaces:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: {url}")
                working_interfaces.append((name, url))
            else:
                print(f"❌ {name} недоступен: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} недоступен: {e}")
    
    return working_interfaces

def test_vllm_adapter():
    """Тест vLLM адаптера"""
    print("\n🧪 Тест vLLM адаптера...")
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        
        adapter = VLLMStreamlitAdapter()
        status = adapter.get_server_status()
        
        if status["status"] == "healthy":
            print("✅ VLLMStreamlitAdapter работает корректно")
            print(f"   📊 Доступно моделей: {status['models']}")
            print(f"   🌐 URL: {status['url']}")
            return True
        else:
            print(f"❌ VLLMStreamlitAdapter: {status.get('error', 'Неизвестная ошибка')}")
    except Exception as e:
        print(f"❌ Ошибка VLLMStreamlitAdapter: {e}")
    
    return False

def check_docker_containers():
    """Проверка Docker контейнеров"""
    print("\n🐳 Проверка Docker контейнеров...")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=dots-ocr", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if "dots-ocr-fixed" in result.stdout:
            print("✅ Контейнер dots-ocr-fixed запущен")
            print(result.stdout)
            return True
        else:
            print("❌ Контейнер dots-ocr-fixed не найден")
            print("💡 Запустите: docker-compose -f docker-compose-vllm.yml up -d dots-ocr")
    except Exception as e:
        print(f"❌ Ошибка проверки Docker: {e}")
    
    return False

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ STREAMLIT + vLLM")
    print("=" * 50)
    
    # Проверки
    checks = {
        "Docker контейнеры": check_docker_containers(),
        "vLLM сервер": check_vllm_server(),
        "Streamlit интерфейсы": len(check_streamlit_interfaces()) > 0,
        "vLLM адаптер": test_vllm_adapter()
    }
    
    # Итоги
    print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ Прошел" if passed else "❌ Не прошел"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\n📡 Доступные интерфейсы:")
        print("   • Основной Streamlit: http://localhost:8501")
        print("   • vLLM тестовый: http://localhost:8502")
        print("   • vLLM API: http://localhost:8000")
        
        print("\n🎯 ГОТОВО К ТЕСТИРОВАНИЮ:")
        print("   1. Откройте http://localhost:8501")
        print("   2. Выберите 'vLLM (Рекомендуется)' в режиме выполнения")
        print("   3. Перейдите в 'Режим OCR'")
        print("   4. Загрузите изображение и протестируйте")
        
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("\n💡 Рекомендации:")
        
        if not checks["Docker контейнеры"]:
            print("   • Запустите vLLM: docker-compose -f docker-compose-vllm.yml up -d dots-ocr")
        
        if not checks["Streamlit интерфейсы"]:
            print("   • Запустите Streamlit: streamlit run app.py --server.port 8501")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())