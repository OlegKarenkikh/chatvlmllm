#!/usr/bin/env python3
"""
Аудит состояния контейнеров vLLM
Проверяет соблюдение принципа одного активного контейнера
"""

import subprocess
import requests
import json
from datetime import datetime
from single_container_manager import SingleContainerManager

def get_docker_containers_status():
    """Получение статуса всех vLLM контейнеров через Docker"""
    print("🐳 СТАТУС DOCKER КОНТЕЙНЕРОВ")
    print("=" * 40)
    
    try:
        # Все контейнеры (включая остановленные)
        result = subprocess.run([
            "docker", "ps", "-a", "--filter", "name=vllm", 
            "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.CreatedAt}}"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            containers = []
            
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        containers.append({
                            "name": parts[0],
                            "status": parts[1],
                            "ports": parts[2] if len(parts) > 2 else "None",
                            "created": parts[3] if len(parts) > 3 else "Unknown"
                        })
            
            print(f"📊 Найдено контейнеров: {len(containers)}")
            
            running_count = 0
            for container in containers:
                status_icon = "🟢" if "Up" in container["status"] else "⚪"
                if "Up" in container["status"]:
                    running_count += 1
                
                print(f"\n{status_icon} {container['name']}")
                print(f"   📊 Статус: {container['status']}")
                print(f"   🌐 Порты: {container['ports']}")
                print(f"   📅 Создан: {container['created']}")
            
            print(f"\n📈 ИТОГО:")
            print(f"   🟢 Запущенных: {running_count}")
            print(f"   ⚪ Остановленных: {len(containers) - running_count}")
            
            # Проверка принципа одного контейнера
            if running_count == 1:
                print("   ✅ ПРИНЦИП ОДНОГО КОНТЕЙНЕРА СОБЛЮДЕН")
            elif running_count == 0:
                print("   ℹ️ НЕТ АКТИВНЫХ КОНТЕЙНЕРОВ")
            else:
                print(f"   ❌ НАРУШЕНИЕ: ЗАПУЩЕНО {running_count} КОНТЕЙНЕРОВ!")
            
            return containers, running_count
        else:
            print(f"❌ Ошибка получения статуса: {result.stderr}")
            return [], 0
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return [], 0

def check_api_endpoints():
    """Проверка доступности API endpoints"""
    print("\n🌐 ПРОВЕРКА API ENDPOINTS")
    print("=" * 30)
    
    endpoints = [
        {"name": "dots.ocr", "port": 8000, "model": "rednote-hilab/dots.ocr"},
        {"name": "Qwen2-VL 2B", "port": 8001, "model": "Qwen/Qwen2-VL-2B-Instruct"},
        {"name": "Phi-3.5 Vision", "port": 8002, "model": "microsoft/Phi-3.5-vision-instruct"},
        {"name": "Qwen2-VL 7B", "port": 8003, "model": "Qwen/Qwen2-VL-7B-Instruct"},
        {"name": "Qwen3-VL 2B", "port": 8004, "model": "Qwen/Qwen3-VL-2B-Instruct"}
    ]
    
    active_endpoints = []
    
    for endpoint in endpoints:
        try:
            # Health check
            health_response = requests.get(f"http://localhost:{endpoint['port']}/health", timeout=3)
            
            if health_response.status_code == 200:
                # Models check
                models_response = requests.get(f"http://localhost:{endpoint['port']}/v1/models", timeout=3)
                
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    available_models = [model["id"] for model in models_data.get("data", [])]
                    
                    print(f"✅ {endpoint['name']} (порт {endpoint['port']})")
                    print(f"   🤖 Модели: {', '.join(available_models)}")
                    
                    active_endpoints.append({
                        "name": endpoint['name'],
                        "port": endpoint['port'],
                        "models": available_models
                    })
                else:
                    print(f"⚠️ {endpoint['name']} (порт {endpoint['port']}) - Health OK, но Models API недоступен")
            else:
                print(f"❌ {endpoint['name']} (порт {endpoint['port']}) - Health check failed")
                
        except requests.exceptions.ConnectionError:
            print(f"⚪ {endpoint['name']} (порт {endpoint['port']}) - Недоступен")
        except Exception as e:
            print(f"❌ {endpoint['name']} (порт {endpoint['port']}) - Ошибка: {str(e)[:50]}...")
    
    print(f"\n📊 АКТИВНЫХ API: {len(active_endpoints)}")
    
    if len(active_endpoints) == 1:
        print("✅ ПРИНЦИП ОДНОГО API СОБЛЮДЕН")
    elif len(active_endpoints) == 0:
        print("ℹ️ НЕТ АКТИВНЫХ API")
    else:
        print(f"❌ НАРУШЕНИЕ: АКТИВНО {len(active_endpoints)} API!")
    
    return active_endpoints

def check_container_manager_status():
    """Проверка статуса через SingleContainerManager"""
    print("\n🎯 СТАТУС ЧЕРЕЗ CONTAINER MANAGER")
    print("=" * 40)
    
    try:
        manager = SingleContainerManager()
        status = manager.get_system_status()
        
        print(f"🎯 Активная модель: {status['active_model_name'] or 'Нет'}")
        print(f"💾 Использование памяти: {status['total_memory_usage']} ГБ")
        print(f"📋 Принцип: {status['principle']}")
        
        print(f"\n📊 ДЕТАЛЬНЫЙ СТАТУС МОДЕЛЕЙ:")
        
        for model_key, model_status in status["models"].items():
            config = model_status["config"]
            
            status_icon = "🟢" if model_status["is_active"] else "⚪"
            print(f"\n{status_icon} {config['display_name']}")
            print(f"   📦 Контейнер: {model_status['container_status']['running']}")
            print(f"   🌐 API: {model_status['api_healthy']}")
            print(f"   💬 Сообщение: {model_status['api_message']}")
            print(f"   💾 Память: {config['memory_gb']} ГБ")
        
        return status
        
    except Exception as e:
        print(f"❌ Ошибка проверки через Container Manager: {e}")
        return None

def check_container_logs():
    """Проверка логов контейнеров"""
    print("\n📋 ПРОВЕРКА ЛОГОВ КОНТЕЙНЕРОВ")
    print("=" * 35)
    
    # Получаем список всех vLLM контейнеров
    try:
        result = subprocess.run([
            "docker", "ps", "-a", "--filter", "name=vllm", "--format", "{{.Names}}\t{{.Status}}"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        container_name = parts[0]
                        container_status = parts[1]
                        
                        print(f"\n📦 {container_name}")
                        print(f"   📊 Статус: {container_status}")
                        
                        # Получаем последние 5 строк логов
                        try:
                            log_result = subprocess.run([
                                "docker", "logs", container_name, "--tail", "5"
                            ], capture_output=True, text=True, timeout=10)
                            
                            if log_result.returncode == 0:
                                log_lines = log_result.stdout.strip().split('\n')
                                if log_lines and log_lines[0]:
                                    print("   📋 Последние логи:")
                                    for log_line in log_lines[-3:]:  # Показываем последние 3 строки
                                        if log_line.strip():
                                            # Сокращаем длинные строки
                                            short_line = log_line[:80] + "..." if len(log_line) > 80 else log_line
                                            print(f"      {short_line}")
                                else:
                                    print("   📋 Логи пусты")
                            else:
                                print(f"   ❌ Ошибка получения логов: {log_result.stderr[:50]}...")
                                
                        except Exception as e:
                            print(f"   ❌ Ошибка чтения логов: {str(e)[:50]}...")
        
    except Exception as e:
        print(f"❌ Ошибка проверки логов: {e}")

def generate_audit_report():
    """Генерация полного аудит-отчета"""
    print("🔍 ПОЛНЫЙ АУДИТ КОНТЕЙНЕРОВ vLLM")
    print("=" * 50)
    print(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Статус Docker контейнеров
    containers, running_count = get_docker_containers_status()
    
    # 2. Проверка API endpoints
    active_apis = check_api_endpoints()
    
    # 3. Статус через Container Manager
    manager_status = check_container_manager_status()
    
    # 4. Проверка логов
    check_container_logs()
    
    # 5. Итоговый анализ
    print("\n🎯 ИТОГОВЫЙ АНАЛИЗ")
    print("=" * 25)
    
    issues = []
    
    # Проверка принципа одного контейнера
    if running_count > 1:
        issues.append(f"❌ Запущено {running_count} контейнеров (должен быть 1)")
    elif running_count == 0:
        issues.append("⚠️ Нет активных контейнеров")
    else:
        print("✅ Принцип одного контейнера соблюден")
    
    # Проверка API
    if len(active_apis) > 1:
        issues.append(f"❌ Активно {len(active_apis)} API (должно быть 1)")
    elif len(active_apis) == 0:
        issues.append("⚠️ Нет активных API")
    else:
        print("✅ Принцип одного API соблюден")
    
    # Проверка согласованности
    if running_count != len(active_apis):
        issues.append(f"❌ Несоответствие: {running_count} контейнеров, {len(active_apis)} API")
    else:
        print("✅ Контейнеры и API согласованы")
    
    # Проверка Container Manager
    if manager_status and manager_status.get('active_model'):
        print(f"✅ Container Manager видит активную модель: {manager_status['active_model_name']}")
    else:
        issues.append("⚠️ Container Manager не видит активной модели")
    
    # Итоговый вердикт
    print(f"\n🏆 ИТОГОВЫЙ ВЕРДИКТ:")
    
    if not issues:
        print("🎊 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("✅ Система работает в соответствии с принципом одного контейнера")
        print("✅ Нет нарушений или проблем")
    else:
        print(f"⚠️ ОБНАРУЖЕНО ПРОБЛЕМ: {len(issues)}")
        for issue in issues:
            print(f"   {issue}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if running_count > 1:
        print("   🛑 Остановите лишние контейнеры:")
        for container in containers:
            if "Up" in container["status"]:
                print(f"      docker stop {container['name']}")
    
    if running_count == 0:
        print("   🚀 Запустите нужную модель:")
        print("      docker-compose -f docker-compose-vllm.yml up -d qwen3-vl-2b")
    
    if not issues:
        print("   🎯 Система настроена оптимально!")
        print("   💡 Продолжайте использовать текущую конфигурацию")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "containers_count": len(containers),
        "running_containers": running_count,
        "active_apis": len(active_apis),
        "issues": issues,
        "status": "OK" if not issues else "ISSUES_FOUND"
    }

if __name__ == "__main__":
    report = generate_audit_report()
    
    # Сохраняем отчет в JSON
    with open(f"container_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Отчет сохранен в JSON файл")