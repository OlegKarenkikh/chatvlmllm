#!/usr/bin/env python3
"""
Тестирование системы переключения одиночных контейнеров
"""

import time
from single_container_manager import SingleContainerManager

def test_single_container_principle():
    """Тестирование принципа одного активного контейнера"""
    
    print("🎯 ТЕСТИРОВАНИЕ ПРИНЦИПА ОДНОГО АКТИВНОГО КОНТЕЙНЕРА")
    print("=" * 70)
    
    # Инициализация менеджера
    manager = SingleContainerManager()
    
    # Шаг 1: Проверка текущего состояния
    print("\n1️⃣ ТЕКУЩЕЕ СОСТОЯНИЕ СИСТЕМЫ")
    print("-" * 40)
    
    status = manager.get_system_status()
    print(f"Активная модель: {status['active_model_name'] or 'Нет'}")
    print(f"Использование памяти: {status['total_memory_usage']} ГБ")
    print(f"Принцип: {status['principle']}")
    
    print("\nСтатус всех моделей:")
    for model_key, model_status in status["models"].items():
        config = model_status["config"]
        container_status = model_status["container_status"]
        
        status_icon = "🟢" if model_status["is_active"] else ("🟡" if container_status["running"] else "⚪")
        api_status = "✅" if model_status["api_healthy"] else "❌"
        
        print(f"  {status_icon} {config['display_name']}")
        print(f"     Контейнер: {container_status['status']} | API: {api_status}")
        print(f"     Память: {config['memory_gb']} ГБ | Порт: {config['port']}")
    
    # Шаг 2: Тест переключения на dots.ocr
    print(f"\n2️⃣ ТЕСТ ПЕРЕКЛЮЧЕНИЯ НА DOTS.OCR")
    print("-" * 40)
    
    print("Переключение на dots.ocr...")
    success, message = manager.start_single_container("dots.ocr")
    
    if success:
        print(f"✅ Успешно: {message}")
        
        # Проверяем состояние после переключения
        time.sleep(2)
        new_status = manager.get_system_status()
        print(f"Новая активная модель: {new_status['active_model_name']}")
        print(f"Использование памяти: {new_status['total_memory_usage']} ГБ")
        
        # Подсчитываем запущенные контейнеры
        running_count = sum(1 for model_status in new_status["models"].values() 
                          if model_status["container_status"]["running"])
        print(f"Запущенных контейнеров: {running_count}")
        
        if running_count == 1:
            print("✅ ПРИНЦИП СОБЛЮДЕН: Только один контейнер активен")
        else:
            print(f"❌ ПРИНЦИП НАРУШЕН: {running_count} контейнеров активны")
    else:
        print(f"❌ Ошибка: {message}")
    
    # Шаг 3: Тест переключения на Qwen3
    print(f"\n3️⃣ ТЕСТ ПЕРЕКЛЮЧЕНИЯ НА QWEN3-VL")
    print("-" * 40)
    
    print("Переключение на Qwen3-VL...")
    success, message = manager.start_single_container("qwen3-vl-2b")
    
    if success:
        print(f"✅ Успешно: {message}")
        
        # Проверяем состояние после переключения
        time.sleep(2)
        final_status = manager.get_system_status()
        print(f"Финальная активная модель: {final_status['active_model_name']}")
        print(f"Использование памяти: {final_status['total_memory_usage']} ГБ")
        
        # Подсчитываем запущенные контейнеры
        running_count = sum(1 for model_status in final_status["models"].values() 
                          if model_status["container_status"]["running"])
        print(f"Запущенных контейнеров: {running_count}")
        
        if running_count == 1:
            print("✅ ПРИНЦИП СОБЛЮДЕН: Только один контейнер активен")
        else:
            print(f"❌ ПРИНЦИП НАРУШЕН: {running_count} контейнеров активны")
    else:
        print(f"❌ Ошибка: {message}")
    
    # Шаг 4: Итоговый отчет
    print(f"\n4️⃣ ИТОГОВЫЙ ОТЧЕТ")
    print("-" * 40)
    
    final_status = manager.get_system_status()
    
    print("Финальное состояние системы:")
    active_models = []
    stopped_models = []
    
    for model_key, model_status in final_status["models"].items():
        config = model_status["config"]
        if model_status["is_active"]:
            active_models.append(config["display_name"])
        elif not model_status["container_status"]["running"]:
            stopped_models.append(config["display_name"])
    
    print(f"✅ Активные модели: {', '.join(active_models) if active_models else 'Нет'}")
    print(f"⚪ Остановленные модели: {', '.join(stopped_models) if stopped_models else 'Нет'}")
    print(f"💾 Общее использование памяти: {final_status['total_memory_usage']} ГБ")
    
    # Проверка принципа
    active_count = len(active_models)
    if active_count <= 1:
        print(f"\n🎊 ПРИНЦИП СОБЛЮДЕН!")
        print(f"   Активных моделей: {active_count}")
        print(f"   Экономия памяти: Максимальная")
        print(f"   Стабильность: Высокая")
    else:
        print(f"\n⚠️ ПРИНЦИП НАРУШЕН!")
        print(f"   Активных моделей: {active_count}")
        print(f"   Риск нехватки памяти: Высокий")
    
    return active_count <= 1

def test_memory_efficiency():
    """Тестирование эффективности использования памяти"""
    
    print(f"\n🧠 ТЕСТ ЭФФЕКТИВНОСТИ ПАМЯТИ")
    print("=" * 50)
    
    manager = SingleContainerManager()
    
    # Расчет теоретического потребления при запуске всех моделей
    total_memory_all = sum(config["memory_gb"] for config in manager.models_config.values())
    print(f"Память при запуске ВСЕХ моделей: {total_memory_all} ГБ")
    
    # Текущее потребление
    status = manager.get_system_status()
    current_memory = status["total_memory_usage"]
    print(f"Текущее потребление памяти: {current_memory} ГБ")
    
    # Экономия
    if total_memory_all > 0:
        savings_gb = total_memory_all - current_memory
        savings_percent = (savings_gb / total_memory_all) * 100
        
        print(f"Экономия памяти: {savings_gb} ГБ ({savings_percent:.1f}%)")
        
        if savings_percent > 70:
            print("✅ ОТЛИЧНАЯ экономия памяти!")
        elif savings_percent > 50:
            print("✅ ХОРОШАЯ экономия памяти!")
        elif savings_percent > 0:
            print("✅ Есть экономия памяти")
        else:
            print("⚠️ Нет экономии памяти")
    
    return current_memory < total_memory_all

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ СИСТЕМЫ УПРАВЛЕНИЯ ОДИНОЧНЫМИ КОНТЕЙНЕРАМИ")
    print("=" * 80)
    
    # Основной тест принципа
    principle_ok = test_single_container_principle()
    
    # Тест эффективности памяти
    memory_ok = test_memory_efficiency()
    
    # Финальный результат
    print(f"\n📊 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ")
    print("=" * 30)
    print(f"Принцип одного контейнера: {'✅ СОБЛЮДЕН' if principle_ok else '❌ НАРУШЕН'}")
    print(f"Эффективность памяти: {'✅ ХОРОШАЯ' if memory_ok else '❌ ПЛОХАЯ'}")
    
    if principle_ok and memory_ok:
        print(f"\n🎊 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("Система готова к продуктивному использованию")
    else:
        print(f"\n⚠️ ЕСТЬ ПРОБЛЕМЫ")
        print("Требуется дополнительная настройка")