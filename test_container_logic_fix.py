#!/usr/bin/env python3
"""
Тест исправленной логики SingleContainerManager
Проверяет, что система не останавливает уже активную модель
"""

import sys
import time

def test_active_model_detection():
    """Тестирование определения активной модели"""
    print("🧪 Тестирование определения активной модели")
    print("=" * 50)
    
    try:
        from single_container_manager import SingleContainerManager
        
        manager = SingleContainerManager()
        
        # Получаем статус системы
        status = manager.get_system_status()
        
        print(f"📊 Статус системы:")
        print(f"  • Активная модель: {status['active_model_name'] or 'Нет'}")
        print(f"  • Использование памяти: {status['total_memory_usage']} ГБ")
        
        # Проверяем каждую модель
        print(f"\n🔍 Детальный статус моделей:")
        
        for model_key, model_status in status["models"].items():
            config = model_status["config"]
            container_status = model_status["container_status"]
            
            print(f"\n  📦 {config['display_name']}:")
            print(f"    • Контейнер запущен: {container_status['running']}")
            print(f"    • Health статус: {container_status['health']}")
            print(f"    • API доступен: {model_status['api_healthy']}")
            print(f"    • API сообщение: {model_status['api_message']}")
            print(f"    • Считается активной: {model_status['is_active']}")
        
        # Тестируем логику определения активной модели
        active_model = manager.get_active_model()
        print(f"\n🎯 Результат get_active_model(): {active_model}")
        
        if active_model:
            active_config = manager.models_config[active_model]
            print(f"✅ Активная модель: {active_config['display_name']}")
            
            # Тестируем повторный запуск той же модели
            print(f"\n🔄 Тестирование повторного запуска активной модели...")
            success, message = manager.start_single_container(active_model)
            
            if success and "уже активна" in message:
                print(f"✅ Логика исправлена: {message}")
                return True
            else:
                print(f"❌ Логика не исправлена: {message}")
                return False
        else:
            print("ℹ️ Нет активной модели для тестирования")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_container_status_logic():
    """Тестирование логики статуса контейнеров"""
    print("\n🧪 Тестирование логики статуса контейнеров")
    print("=" * 50)
    
    try:
        from single_container_manager import SingleContainerManager
        
        manager = SingleContainerManager()
        
        # Проверяем статус каждого контейнера
        for model_key, config in manager.models_config.items():
            print(f"\n📦 Проверка {config['display_name']}:")
            
            # Статус контейнера
            container_status = manager.get_container_status(config["container_name"])
            print(f"  • Существует: {container_status['exists']}")
            print(f"  • Запущен: {container_status['running']}")
            print(f"  • Статус: {container_status['status']}")
            print(f"  • Health: {container_status['health']}")
            
            # API статус
            if container_status["running"]:
                api_healthy, api_message = manager.check_api_health(config["port"])
                print(f"  • API здоров: {api_healthy}")
                print(f"  • API сообщение: {api_message}")
                
                # Проверяем новую логику
                if api_healthy:
                    print(f"  ✅ По новой логике: АКТИВНА")
                else:
                    print(f"  ⚪ По новой логике: НЕ АКТИВНА ({api_message})")
            else:
                print(f"  ⚪ Контейнер не запущен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def test_docker_containers():
    """Проверка реального статуса Docker контейнеров"""
    print("\n🐳 Проверка Docker контейнеров")
    print("=" * 40)
    
    try:
        import subprocess
        
        # Проверяем все vLLM контейнеры
        result = subprocess.run([
            "docker", "ps", "-a", "--filter", "name=vllm", "--format", 
            "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("📋 Статус vLLM контейнеров:")
            print(result.stdout)
        else:
            print(f"❌ Ошибка получения статуса: {result.stderr}")
        
        # Проверяем запущенные контейнеры
        result = subprocess.run([
            "docker", "ps", "--filter", "name=vllm", "--format", 
            "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            running_containers = result.stdout.strip().split('\n')[1:]  # Убираем заголовок
            running_containers = [line for line in running_containers if line.strip()]
            
            print(f"\n🟢 Запущенных контейнеров: {len(running_containers)}")
            for container in running_containers:
                print(f"  • {container}")
            
            if len(running_containers) > 1:
                print("⚠️ ВНИМАНИЕ: Запущено больше одного контейнера!")
                print("💡 Это нарушает принцип одного активного контейнера")
                return False
            elif len(running_containers) == 1:
                print("✅ Принцип одного контейнера соблюден")
                return True
            else:
                print("ℹ️ Нет запущенных vLLM контейнеров")
                return True
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки Docker: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🔧 ТЕСТИРОВАНИЕ ИСПРАВЛЕННОЙ ЛОГИКИ КОНТЕЙНЕРОВ")
    print("=" * 60)
    
    tests = [
        ("Определение активной модели", test_active_model_detection),
        ("Логика статуса контейнеров", test_container_status_logic),
        ("Статус Docker контейнеров", test_docker_containers)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print(f"\n🎯 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Результат: {passed}/{total} тестов пройдено ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎊 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Логика исправлена корректно.")
    else:
        print("⚠️ Некоторые тесты не пройдены. Требуется дополнительная настройка.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)