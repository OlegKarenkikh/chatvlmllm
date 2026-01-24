#!/usr/bin/env python3
"""
Тест исправления конфигурации
"""

import yaml
import requests
import time

def test_config_loading():
    """Тест загрузки конфигурации"""
    print("🔧 Тестирование загрузки конфигурации...")
    
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # Проверка наличия необходимых секций
        required_sections = ["ocr", "document_templates", "models"]
        
        for section in required_sections:
            if section in config:
                print(f"✅ Секция '{section}' найдена")
            else:
                print(f"❌ Секция '{section}' отсутствует")
                return False
        
        # Проверка OCR настроек
        if "supported_formats" in config["ocr"]:
            formats = config["ocr"]["supported_formats"]
            print(f"✅ Поддерживаемые форматы: {formats}")
        else:
            print("❌ Отсутствуют поддерживаемые форматы")
            return False
        
        # Проверка шаблонов документов
        templates = list(config["document_templates"].keys())
        print(f"✅ Шаблоны документов: {templates}")
        
        # Проверка моделей
        models = list(config["models"].keys())
        print(f"✅ Модели: {models}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False

def test_streamlit_accessibility():
    """Тест доступности Streamlit"""
    print("\n🌐 Тестирование доступности Streamlit...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            print("✅ Streamlit доступен на http://localhost:8501")
            return True
        else:
            print(f"❌ Streamlit недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Streamlit: {e}")
        return False

def test_vllm_server():
    """Тест vLLM сервера"""
    print("\n🚀 Тестирование vLLM сервера...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ vLLM сервер работает")
            
            # Проверка моделей
            models_response = requests.get("http://localhost:8000/v1/models", timeout=5)
            if models_response.status_code == 200:
                models = models_response.json()
                print(f"✅ Доступно моделей: {len(models.get('data', []))}")
                return True
        else:
            print(f"❌ vLLM сервер недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ vLLM сервер недоступен: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ КОНФИГУРАЦИИ")
    print("=" * 45)
    
    tests = {
        "Загрузка конфигурации": test_config_loading(),
        "Доступность Streamlit": test_streamlit_accessibility(),
        "vLLM сервер": test_vllm_server()
    }
    
    print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    
    all_passed = True
    for test_name, passed in tests.items():
        status = "✅ Прошел" if passed else "❌ Не прошел"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 45)
    
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("\n💡 Система готова к использованию:")
        print("   • Конфигурация загружается корректно")
        print("   • Streamlit работает без ошибок")
        print("   • vLLM интеграция функциональна")
        print("\n🌐 Откройте http://localhost:8501 для использования")
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("\n💡 Проверьте:")
        if not tests["Загрузка конфигурации"]:
            print("   • Файл config.yaml и его структуру")
        if not tests["Доступность Streamlit"]:
            print("   • Запуск Streamlit: streamlit run app.py")
        if not tests["vLLM сервер"]:
            print("   • Запуск vLLM: docker-compose -f docker-compose-vllm.yml up -d")
        return 1

if __name__ == "__main__":
    exit(main())