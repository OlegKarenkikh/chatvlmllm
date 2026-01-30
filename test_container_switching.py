#!/usr/bin/env python3
"""
Тест переключения контейнеров
Проверяет, что при запуске новой модели старая останавливается
"""

import time
import subprocess
from single_container_manager import SingleContainerManager

def get_running_containers():
    """Получение списка запущенных vLLM контейнеров"""
    try:
        result = subprocess.run([
            "docker", "ps", "--filter", "ancestor=vllm/vllm-openai:latest", 
            "--format", "{{.Names}}"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            containers = [name.strip() for name in result.stdout.strip().split('\n') if name.strip()]
            return containers
        return []
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def main():
    print("🧪 ТЕСТ ПЕРЕКЛЮЧЕНИЯ КОНТЕЙНЕРОВ")
    print("=" * 40)
    
    manager = SingleContainerManager()
    
    # Шаг 1: Проверяем текущее состояние
    print("\n📊 ТЕКУЩЕЕ СОСТОЯНИЕ:")
    running = get_running_containers()
    print(f"Запущенных контейнеров: {len(running)}")
    for container in running:
        print(f"  • {container}")
    
    # Шаг 2: Получаем статус через менеджер
    print(f"\n🎯 СТАТУС ЧЕРЕЗ МЕНЕДЖЕР:")
    status = manager.get_system_status()
    print(f"Активная модель: {status['active_model_name'] or 'Нет'}")
    
    # Шаг 3: Тестируем переключение на Qwen3-VL
    print(f"\n🔄 ТЕСТ ПЕРЕКЛЮЧЕНИЯ НА QWEN3-VL:")
    print("Запускаем qwen3-vl-2b...")
    
    success, message = manager.start_single_container("qwen3-vl-2b")
    
    print(f"Результат: {'✅ Успех' if success else '❌ Ошибка'}")
    print(f"Сообщение: {message}")
    
    # Шаг 4: Проверяем результат
    print(f"\n📊 РЕЗУЛЬТАТ:")
    time.sleep(2)  # Даем время на остановку
    
    final_running = get_running_containers()
    print(f"Запущенных контейнеров: {len(final_running)}")
    for container in final_running:
        print(f"  • {container}")
    
    # Шаг 5: Проверяем принцип
    if len(final_running) <= 1:
        print("✅ ПРИНЦИП СОБЛЮДЕН: Не более одного контейнера")
    else:
        print(f"❌ НАРУШЕНИЕ: Запущено {len(final_running)} контейнеров!")
    
    return len(final_running) <= 1

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)