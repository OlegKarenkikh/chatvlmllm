#!/usr/bin/env python3
"""
Тест поведения переключения моделей
Проверяет, что система не останавливает уже активную модель
"""

import time
from single_container_manager import SingleContainerManager

def test_model_switching_logic():
    """Тестирование логики переключения моделей"""
    print("🔄 ТЕСТИРОВАНИЕ ПОВЕДЕНИЯ ПЕРЕКЛЮЧЕНИЯ МОДЕЛЕЙ")
    print("=" * 60)
    
    manager = SingleContainerManager()
    
    # Получаем текущую активную модель
    current_active = manager.get_active_model()
    
    if not current_active:
        print("❌ Нет активной модели для тестирования")
        return False
    
    active_config = manager.models_config[current_active]
    print(f"🎯 Текущая активная модель: {active_config['display_name']}")
    
    # Тест 1: Попытка переключиться на ту же модель
    print(f"\n🧪 ТЕСТ 1: Переключение на ту же модель ({current_active})")
    print("-" * 50)
    
    start_time = time.time()
    success, message = manager.start_single_container(current_active)
    elapsed_time = time.time() - start_time
    
    print(f"⏱️ Время выполнения: {elapsed_time:.2f} секунд")
    print(f"✅ Успех: {success}")
    print(f"💬 Сообщение: {message}")
    
    # Проверяем, что это было быстро (не было перезапуска)
    if success and elapsed_time < 5 and "уже активна" in message:
        print("✅ ТЕСТ 1 ПРОЙДЕН: Система корректно определила, что модель уже активна")
        test1_passed = True
    else:
        print("❌ ТЕСТ 1 НЕ ПРОЙДЕН: Система попыталась перезапустить активную модель")
        test1_passed = False
    
    # Тест 2: Проверка, что модель все еще активна
    print(f"\n🧪 ТЕСТ 2: Проверка состояния после 'переключения'")
    print("-" * 50)
    
    still_active = manager.get_active_model()
    api_healthy, api_message = manager.check_api_health(active_config["port"])
    
    print(f"🎯 Активная модель: {still_active}")
    print(f"🌐 API доступен: {api_healthy}")
    print(f"💬 API статус: {api_message}")
    
    if still_active == current_active and api_healthy:
        print("✅ ТЕСТ 2 ПРОЙДЕН: Модель осталась активной и доступной")
        test2_passed = True
    else:
        print("❌ ТЕСТ 2 НЕ ПРОЙДЕН: Состояние модели изменилось")
        test2_passed = False
    
    # Тест 3: Проверка количества запущенных контейнеров
    print(f"\n🧪 ТЕСТ 3: Проверка принципа одного контейнера")
    print("-" * 50)
    
    import subprocess
    result = subprocess.run([
        "docker", "ps", "--filter", "name=vllm", "--format", "{{.Names}}"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        running_containers = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        print(f"🐳 Запущенных vLLM контейнеров: {len(running_containers)}")
        
        for container in running_containers:
            print(f"  • {container}")
        
        if len(running_containers) == 1:
            print("✅ ТЕСТ 3 ПРОЙДЕН: Принцип одного контейнера соблюден")
            test3_passed = True
        else:
            print("❌ ТЕСТ 3 НЕ ПРОЙДЕН: Запущено больше одного контейнера")
            test3_passed = False
    else:
        print("❌ ТЕСТ 3 НЕ ПРОЙДЕН: Ошибка проверки Docker")
        test3_passed = False
    
    # Итоговый результат
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print("=" * 30)
    
    tests_passed = sum([test1_passed, test2_passed, test3_passed])
    total_tests = 3
    
    results = [
        ("Логика переключения на активную модель", test1_passed),
        ("Сохранение состояния модели", test2_passed),
        ("Принцип одного контейнера", test3_passed)
    ]
    
    for test_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Результат: {tests_passed}/{total_tests} тестов пройдено ({tests_passed/total_tests*100:.1f}%)")
    
    if tests_passed == total_tests:
        print("🎊 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Поведение переключения моделей исправлено.")
        print("💡 Пользователь больше не увидит нелогичное поведение.")
    else:
        print("⚠️ Некоторые тесты не пройдены. Требуется дополнительная настройка.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = test_model_switching_logic()
    exit(0 if success else 1)