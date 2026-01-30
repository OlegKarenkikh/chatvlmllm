#!/usr/bin/env python3
"""
Тест обнаружения активного контейнера dots.ocr
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from single_container_manager import SingleContainerManager
import requests

def test_container_detection():
    """Тестирование обнаружения активного контейнера"""
    
    print("🔍 Тестирование обнаружения контейнера dots.ocr")
    print("=" * 60)
    
    # Инициализируем менеджер
    manager = SingleContainerManager()
    
    # Проверяем статус контейнера dots.ocr
    print("1️⃣ Проверка статуса контейнера...")
    container_status = manager.get_container_status("dots-ocr-fixed")
    print(f"   Существует: {container_status['exists']}")
    print(f"   Запущен: {container_status['running']}")
    print(f"   Статус: {container_status['status']}")
    print(f"   Health: {container_status['health']}")
    
    # Проверяем API здоровье
    print("\n2️⃣ Проверка API здоровья...")
    api_healthy, api_message = manager.check_api_health(8000)
    print(f"   API здоров: {api_healthy}")
    print(f"   Сообщение: {api_message}")
    
    # Проверяем активную модель
    print("\n3️⃣ Определение активной модели...")
    active_model = manager.get_active_model()
    print(f"   Активная модель: {active_model}")
    
    # Получаем полный статус системы
    print("\n4️⃣ Полный статус системы...")
    system_status = manager.get_system_status()
    print(f"   Активная модель: {system_status['active_model']}")
    print(f"   Имя модели: {system_status['active_model_name']}")
    print(f"   Использование памяти: {system_status['total_memory_usage']} ГБ")
    print(f"   Принцип: {system_status['principle']}")
    
    # Детальная информация о dots.ocr
    if 'dots.ocr' in system_status['models']:
        dots_status = system_status['models']['dots.ocr']
        print(f"\n📊 Статус dots.ocr:")
        print(f"   Контейнер запущен: {dots_status['container_status']['running']}")
        print(f"   API здоров: {dots_status['api_healthy']}")
        print(f"   API сообщение: {dots_status['api_message']}")
        print(f"   Активна: {dots_status['is_active']}")
    
    # Прямая проверка API
    print("\n5️⃣ Прямая проверка API...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"   Health endpoint: {response.status_code}")
        
        models_response = requests.get("http://localhost:8000/v1/models", timeout=5)
        print(f"   Models endpoint: {models_response.status_code}")
        
        if models_response.status_code == 200:
            models_data = models_response.json()
            print(f"   Доступные модели: {len(models_data.get('data', []))}")
            for model in models_data.get('data', []):
                print(f"     - {model['id']} (max_tokens: {model.get('max_model_len', 'N/A')})")
    
    except Exception as e:
        print(f"   ❌ Ошибка API: {e}")
    
    print("\n" + "=" * 60)
    
    # Итоговая диагностика
    if active_model == "dots.ocr":
        print("✅ УСПЕХ: dots.ocr правильно обнаружена как активная модель")
        return True
    else:
        print("❌ ПРОБЛЕМА: dots.ocr не обнаружена как активная модель")
        print("💡 Возможные причины:")
        print("   - Контейнер еще загружается")
        print("   - API не готов")
        print("   - Проблема с сетевым подключением")
        return False

if __name__ == "__main__":
    success = test_container_detection()
    sys.exit(0 if success else 1)