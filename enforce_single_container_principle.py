#!/usr/bin/env python3
"""
Принудительное соблюдение принципа одного контейнера
Останавливает лишние контейнеры и очищает остановленные
"""

import subprocess
import time
from single_container_manager import SingleContainerManager

def get_all_vllm_containers():
    """Получение всех vLLM контейнеров (запущенных и остановленных)"""
    try:
        result = subprocess.run([
            "docker", "ps", "-a", "--filter", "name=vllm", 
            "--format", "{{.Names}}\t{{.Status}}\t{{.ID}}"
        ], capture_output=True, text=True, timeout=10)
        
        containers = []
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        containers.append({
                            "name": parts[0],
                            "status": parts[1],
                            "id": parts[2],
                            "running": "Up" in parts[1]
                        })
        
        return containers
    except Exception as e:
        print(f"❌ Ошибка получения контейнеров: {e}")
        return []

def get_running_vllm_containers():
    """Получение только запущенных vLLM контейнеров"""
    try:
        result = subprocess.run([
            "docker", "ps", "--filter", "name=vllm", 
            "--format", "{{.Names}}\t{{.Status}}\t{{.ID}}"
        ], capture_output=True, text=True, timeout=10)
        
        containers = []
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        containers.append({
                            "name": parts[0],
                            "status": parts[1],
                            "id": parts[2]
                        })
        
        return containers
    except Exception as e:
        print(f"❌ Ошибка получения запущенных контейнеров: {e}")
        return []

def stop_container(container_name):
    """Остановка контейнера"""
    try:
        result = subprocess.run([
            "docker", "stop", container_name
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Остановлен: {container_name}")
            return True
        else:
            print(f"❌ Ошибка остановки {container_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ошибка остановки {container_name}: {e}")
        return False

def remove_stopped_containers():
    """Удаление всех остановленных vLLM контейнеров"""
    print("\n🗑️ ОЧИСТКА ОСТАНОВЛЕННЫХ КОНТЕЙНЕРОВ")
    print("=" * 40)
    
    try:
        # Получаем остановленные контейнеры
        result = subprocess.run([
            "docker", "ps", "-a", "--filter", "name=vllm", "--filter", "status=exited",
            "--format", "{{.Names}}\t{{.ID}}"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            removed_count = 0
            
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        container_name = parts[0]
                        container_id = parts[1]
                        
                        # Удаляем контейнер
                        remove_result = subprocess.run([
                            "docker", "rm", container_id
                        ], capture_output=True, text=True, timeout=10)
                        
                        if remove_result.returncode == 0:
                            print(f"🗑️ Удален: {container_name} ({container_id[:12]})")
                            removed_count += 1
                        else:
                            print(f"❌ Ошибка удаления {container_name}: {remove_result.stderr}")
            
            if removed_count > 0:
                print(f"✅ Удалено контейнеров: {removed_count}")
            else:
                print("ℹ️ Нет остановленных контейнеров для удаления")
        
    except Exception as e:
        print(f"❌ Ошибка очистки: {e}")

def enforce_single_container():
    """Принудительное соблюдение принципа одного контейнера"""
    print("🔧 ПРИНУДИТЕЛЬНОЕ СОБЛЮДЕНИЕ ПРИНЦИПА ОДНОГО КОНТЕЙНЕРА")
    print("=" * 60)
    
    # Шаг 1: Получаем все запущенные контейнеры
    running_containers = get_running_vllm_containers()
    
    print(f"📊 Запущенных vLLM контейнеров: {len(running_containers)}")
    
    if len(running_containers) == 0:
        print("ℹ️ Нет запущенных контейнеров")
        return True
    elif len(running_containers) == 1:
        container = running_containers[0]
        print(f"✅ Принцип соблюден: запущен только {container['name']}")
        return True
    else:
        print(f"❌ НАРУШЕНИЕ: Запущено {len(running_containers)} контейнеров!")
        
        # Показываем все запущенные контейнеры
        for i, container in enumerate(running_containers, 1):
            print(f"   {i}. {container['name']} - {container['status']}")
        
        # Шаг 2: Определяем, какой контейнер оставить
        print(f"\n🎯 ОПРЕДЕЛЕНИЕ АКТИВНОГО КОНТЕЙНЕРА")
        
        try:
            manager = SingleContainerManager()
            active_model = manager.get_active_model()
            
            if active_model:
                active_config = manager.models_config[active_model]
                target_container = active_config["container_name"]
                print(f"🎯 Активная модель: {active_config['display_name']}")
                print(f"📦 Целевой контейнер: {target_container}")
                
                # Останавливаем все контейнеры кроме активного
                stopped_count = 0
                for container in running_containers:
                    if container["name"] != target_container:
                        print(f"🛑 Останавливаю лишний контейнер: {container['name']}")
                        if stop_container(container["name"]):
                            stopped_count += 1
                
                print(f"✅ Остановлено лишних контейнеров: {stopped_count}")
                
                # Проверяем результат
                time.sleep(2)
                final_running = get_running_vllm_containers()
                
                if len(final_running) == 1:
                    print(f"🎊 ПРИНЦИП ВОССТАНОВЛЕН: Активен только {final_running[0]['name']}")
                    return True
                else:
                    print(f"⚠️ Все еще запущено {len(final_running)} контейнеров")
                    return False
                    
            else:
                print("⚠️ Container Manager не видит активной модели")
                print("🛑 Останавливаю все контейнеры для безопасности")
                
                stopped_count = 0
                for container in running_containers:
                    if stop_container(container["name"]):
                        stopped_count += 1
                
                print(f"✅ Остановлено контейнеров: {stopped_count}")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка определения активного контейнера: {e}")
            print("🛑 Останавливаю все контейнеры для безопасности")
            
            stopped_count = 0
            for container in running_containers:
                if stop_container(container["name"]):
                    stopped_count += 1
            
            print(f"✅ Остановлено контейнеров: {stopped_count}")
            return True

def main():
    """Основная функция"""
    print("🔧 ОБЕСПЕЧЕНИЕ ПРИНЦИПА ОДНОГО КОНТЕЙНЕРА")
    print("=" * 50)
    
    # Шаг 1: Принудительное соблюдение принципа
    success = enforce_single_container()
    
    # Шаг 2: Очистка остановленных контейнеров
    remove_stopped_containers()
    
    # Шаг 3: Финальная проверка
    print(f"\n🎯 ФИНАЛЬНАЯ ПРОВЕРКА")
    print("=" * 25)
    
    final_running = get_running_vllm_containers()
    all_containers = get_all_vllm_containers()
    
    print(f"📊 Всего vLLM контейнеров: {len(all_containers)}")
    print(f"🟢 Запущенных: {len(final_running)}")
    print(f"⚪ Остановленных: {len(all_containers) - len(final_running)}")
    
    if len(final_running) <= 1:
        print("✅ ПРИНЦИП ОДНОГО КОНТЕЙНЕРА СОБЛЮДЕН")
        
        if len(final_running) == 1:
            active_container = final_running[0]
            print(f"🎯 Активный контейнер: {active_container['name']}")
        else:
            print("ℹ️ Нет активных контейнеров")
    else:
        print(f"❌ НАРУШЕНИЕ: Все еще запущено {len(final_running)} контейнеров!")
        for container in final_running:
            print(f"   • {container['name']}")
    
    return len(final_running) <= 1

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)