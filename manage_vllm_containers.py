#!/usr/bin/env python3
"""
Скрипт управления vLLM контейнерами с оптимизацией памяти
"""

import subprocess
import time
import requests
import argparse
import json

class VLLMContainerManager:
    def __init__(self):
        self.compose_file = "docker-compose-vllm-optimized.yml"
        
        self.services = {
            "dots-ocr": {
                "name": "dots.ocr",
                "port": 8000,
                "memory_gb": 4.5,
                "profile": "dots-ocr"
            },
            "qwen3-vl-2b": {
                "name": "Qwen3-VL 2B",
                "port": 8004,
                "memory_gb": 6.0,
                "profile": "qwen3-vl"
            },
            "qwen2-vl-2b": {
                "name": "Qwen2-VL 2B",
                "port": 8001,
                "memory_gb": 5.5,
                "profile": "qwen2-vl"
            }
        }
        
        self.max_memory_gb = 12
    
    def run_command(self, command, timeout=60):
        """Выполнение команды с таймаутом"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def check_service_health(self, port):
        """Проверка здоровья сервиса"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_running_services(self):
        """Получение списка запущенных сервисов"""
        running = []
        for service, config in self.services.items():
            if self.check_service_health(config["port"]):
                running.append(service)
        return running
    
    def calculate_memory_usage(self, services):
        """Расчет потребления памяти"""
        total = 0
        for service in services:
            if service in self.services:
                total += self.services[service]["memory_gb"]
        return total
    
    def can_run_together(self, services):
        """Проверка возможности совместного запуска"""
        return self.calculate_memory_usage(services) <= self.max_memory_gb
    
    def start_service(self, service):
        """Запуск сервиса"""
        if service not in self.services:
            return False, f"Unknown service: {service}"
        
        config = self.services[service]
        profile = config["profile"]
        
        print(f"🚀 Запуск {config['name']}...")
        
        command = f"docker-compose -f {self.compose_file} --profile {profile} up -d {service}"
        success, stdout, stderr = self.run_command(command, timeout=120)
        
        if not success:
            return False, f"Failed to start {service}: {stderr}"
        
        # Ожидание готовности
        print(f"⏳ Ожидание готовности {config['name']}...")
        max_wait = 180  # 3 минуты
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if self.check_service_health(config["port"]):
                print(f"✅ {config['name']} готов!")
                return True, f"{config['name']} started successfully"
            time.sleep(5)
        
        return False, f"Service {service} failed to become healthy"
    
    def stop_service(self, service):
        """Остановка сервиса"""
        if service not in self.services:
            return False, f"Unknown service: {service}"
        
        config = self.services[service]
        print(f"🛑 Остановка {config['name']}...")
        
        command = f"docker-compose -f {self.compose_file} stop {service}"
        success, stdout, stderr = self.run_command(command, timeout=30)
        
        if success:
            print(f"✅ {config['name']} остановлен")
            return True, f"{config['name']} stopped successfully"
        else:
            return False, f"Failed to stop {service}: {stderr}"
    
    def switch_to_single_model(self, target_service):
        """Переключение на одну модель (останавливает остальные)"""
        if target_service not in self.services:
            return False, f"Unknown service: {target_service}"
        
        running_services = self.get_running_services()
        target_config = self.services[target_service]
        
        print(f"🎯 Переключение на {target_config['name']} (режим одной модели)")
        
        # Останавливаем все остальные сервисы
        for service in running_services:
            if service != target_service:
                success, message = self.stop_service(service)
                if not success:
                    print(f"⚠️ Предупреждение: {message}")
                time.sleep(2)
        
        # Запускаем целевой сервис
        if target_service not in running_services:
            success, message = self.start_service(target_service)
            if not success:
                return False, message
        
        return True, f"Switched to {target_config['name']} (single model mode)"
    
    def start_optimal_combination(self):
        """Запуск оптимальной комбинации моделей"""
        print("🧠 Поиск оптимальной комбинации моделей...")
        
        # Приоритетные комбинации
        combinations = [
            ["dots-ocr"],  # Только dots.ocr (самая быстрая)
            ["qwen3-vl-2b"],  # Только Qwen3-VL
            ["dots-ocr", "qwen2-vl-2b"],  # dots.ocr + Qwen2-VL (если помещается)
        ]
        
        for combo in combinations:
            if self.can_run_together(combo):
                memory_usage = self.calculate_memory_usage(combo)
                print(f"✅ Найдена подходящая комбинация: {combo}")
                print(f"   Потребление памяти: {memory_usage:.1f}/{self.max_memory_gb} ГБ")
                
                # Останавливаем все текущие сервисы
                running = self.get_running_services()
                for service in running:
                    if service not in combo:
                        self.stop_service(service)
                        time.sleep(2)
                
                # Запускаем нужные сервисы
                for service in combo:
                    if service not in self.get_running_services():
                        success, message = self.start_service(service)
                        if not success:
                            print(f"❌ Ошибка запуска {service}: {message}")
                            continue
                        time.sleep(3)
                
                return True, f"Started optimal combination: {combo}"
        
        return False, "No suitable combination found"
    
    def get_status(self):
        """Получение статуса всех сервисов"""
        running_services = self.get_running_services()
        memory_usage = self.calculate_memory_usage(running_services)
        
        status = {
            "running_services": len(running_services),
            "services": {},
            "memory_usage_gb": memory_usage,
            "memory_limit_gb": self.max_memory_gb,
            "memory_usage_percent": (memory_usage / self.max_memory_gb) * 100,
            "memory_available_gb": self.max_memory_gb - memory_usage
        }
        
        for service, config in self.services.items():
            is_running = service in running_services
            status["services"][service] = {
                "name": config["name"],
                "running": is_running,
                "port": config["port"],
                "memory_gb": config["memory_gb"],
                "healthy": self.check_service_health(config["port"]) if is_running else False
            }
        
        return status
    
    def print_status(self):
        """Вывод статуса в консоль"""
        status = self.get_status()
        
        print("📊 СТАТУС vLLM КОНТЕЙНЕРОВ")
        print("=" * 50)
        
        print(f"Активных сервисов: {status['running_services']}")
        print(f"Использование GPU: {status['memory_usage_gb']:.1f}/{status['memory_limit_gb']} ГБ ({status['memory_usage_percent']:.1f}%)")
        print(f"Доступно памяти: {status['memory_available_gb']:.1f} ГБ")
        
        print("\n📋 Детали сервисов:")
        for service, info in status["services"].items():
            status_icon = "🟢" if info["running"] else "🔴"
            health_icon = "✅" if info["healthy"] else "❌"
            
            print(f"  {status_icon} {info['name']}")
            print(f"     Порт: {info['port']}, Память: {info['memory_gb']} ГБ")
            if info["running"]:
                print(f"     Здоровье: {health_icon}")
        
        # Рекомендации
        print(f"\n💡 Рекомендации:")
        if status['memory_usage_percent'] > 100:
            print("   ❌ Превышен лимит памяти! Остановите некоторые сервисы.")
        elif status['memory_usage_percent'] > 90:
            print("   ⚠️ Высокое использование памяти. Рекомендуется режим одной модели.")
        elif status['running_services'] == 0:
            print("   🚀 Нет активных сервисов. Запустите оптимальную комбинацию.")
        else:
            print("   ✅ Система работает в оптимальном режиме.")

def main():
    parser = argparse.ArgumentParser(description="Управление vLLM контейнерами")
    parser.add_argument("action", choices=[
        "status", "start", "stop", "switch", "optimize", "single"
    ], help="Действие для выполнения")
    parser.add_argument("--service", help="Имя сервиса (dots-ocr, qwen3-vl-2b, qwen2-vl-2b)")
    
    args = parser.parse_args()
    
    manager = VLLMContainerManager()
    
    if args.action == "status":
        manager.print_status()
    
    elif args.action == "start":
        if not args.service:
            print("❌ Укажите сервис для запуска: --service <service_name>")
            return
        
        success, message = manager.start_service(args.service)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    elif args.action == "stop":
        if not args.service:
            print("❌ Укажите сервис для остановки: --service <service_name>")
            return
        
        success, message = manager.stop_service(args.service)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    elif args.action == "switch" or args.action == "single":
        if not args.service:
            print("❌ Укажите сервис для переключения: --service <service_name>")
            return
        
        success, message = manager.switch_to_single_model(args.service)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    elif args.action == "optimize":
        success, message = manager.start_optimal_combination()
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    # Показываем финальный статус
    print("\n" + "="*50)
    manager.print_status()

if __name__ == "__main__":
    main()