#!/usr/bin/env python3
"""
Полный интеграционный тест: запуск всех сервисов и тестирование
"""

import subprocess
import time
import requests
import threading
import os
import signal
import sys
from pathlib import Path

class FullIntegrationRunner:
    def __init__(self):
        self.processes = {}
        self.services = {
            "api": {
                "command": ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"],
                "url": "http://localhost:8001",
                "health_endpoint": "/health",
                "name": "FastAPI Server"
            },
            "streamlit": {
                "command": ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
                "url": "http://localhost:8501",
                "health_endpoint": "/",
                "name": "Streamlit Interface"
            }
        }
        self.vllm_models = []
        
    def start_service(self, service_name: str, config: dict) -> bool:
        """Запуск сервиса"""
        print(f"🚀 Запуск {config['name']}...")
        
        try:
            # Запуск процесса
            process = subprocess.Popen(
                config["command"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[service_name] = process
            
            # Ожидание готовности сервиса
            max_wait = 60  # 1 минута
            wait_interval = 2
            
            for attempt in range(max_wait // wait_interval):
                if process.poll() is not None:
                    # Процесс завершился
                    stdout, stderr = process.communicate()
                    print(f"❌ {config['name']} завершился с кодом {process.returncode}")
                    print(f"STDOUT: {stdout[-500:]}")  # Последние 500 символов
                    print(f"STDERR: {stderr[-500:]}")
                    return False
                
                try:
                    response = requests.get(
                        config["url"] + config["health_endpoint"],
                        timeout=5
                    )
                    if response.status_code == 200:
                        print(f"✅ {config['name']} готов на {config['url']}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                print(f"   ⏳ Ожидание готовности... ({attempt + 1}/{max_wait // wait_interval})")
                time.sleep(wait_interval)
            
            print(f"❌ {config['name']} не готов после {max_wait}с")
            return False
            
        except Exception as e:
            print(f"❌ Ошибка запуска {config['name']}: {e}")
            return False
    
    def check_vllm_models(self) -> list:
        """Проверка доступных vLLM моделей"""
        print(f"\n🔍 Проверка vLLM моделей...")
        
        vllm_endpoints = [
            ("dots.ocr", "http://localhost:8000"),
            ("Qwen3-VL-2B", "http://localhost:8010"),
            ("Qwen2-VL-2B", "http://localhost:8011")
        ]
        
        available_models = []
        
        for model_name, url in vllm_endpoints:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    available_models.append((model_name, url))
                    print(f"   ✅ {model_name}: Доступна")
                else:
                    print(f"   ❌ {model_name}: HTTP {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"   ❌ {model_name}: Недоступна")
        
        if not available_models:
            print(f"   ⚠️ vLLM модели не найдены. Запустите их с помощью:")
            print(f"   python launch_working_models.py")
        
        return available_models
    
    def start_vllm_model(self, model_choice: str = "1") -> bool:
        """Запуск одной vLLM модели для тестирования"""
        print(f"\n🤖 Запуск vLLM модели для тестирования...")
        
        try:
            # Запуск лаунчера в отдельном процессе
            from launch_working_models import WorkingModelsLauncher
            
            launcher = WorkingModelsLauncher()
            
            # Очистка старых контейнеров
            launcher.cleanup_containers()
            
            # Запуск выбранной модели (по умолчанию dots.ocr)
            success = launcher.launch_single_model(model_choice)
            
            if success:
                print(f"✅ vLLM модель запущена успешно")
                return True
            else:
                print(f"❌ Не удалось запустить vLLM модель")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка запуска vLLM модели: {e}")
            return False
    
    def stop_all_services(self):
        """Остановка всех сервисов"""
        print(f"\n🛑 Остановка сервисов...")
        
        for service_name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"   Остановка {service_name}...")
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                except Exception as e:
                    print(f"   Ошибка остановки {service_name}: {e}")
        
        # Очистка vLLM контейнеров
        try:
            from launch_working_models import WorkingModelsLauncher
            launcher = WorkingModelsLauncher()
            launcher.cleanup_containers()
            print(f"   ✅ vLLM контейнеры очищены")
        except Exception as e:
            print(f"   ⚠️ Ошибка очистки vLLM: {e}")
    
    def run_integration_tests(self) -> bool:
        """Запуск интеграционных тестов"""
        print(f"\n🧪 Запуск интеграционных тестов...")
        
        try:
            # Импорт и запуск тестера
            from test_end_to_end_integration import EndToEndTester
            
            tester = EndToEndTester()
            tester.run_all_tests()
            
            # Проверка результатов
            summary = tester.results["summary"]
            success_rate = summary["passed"] / summary["total"] if summary["total"] > 0 else 0
            
            print(f"\n📊 Результаты тестирования:")
            print(f"   Всего тестов: {summary['total']}")
            print(f"   Прошло: {summary['passed']}")
            print(f"   Не прошло: {summary['failed']}")
            print(f"   Успешность: {success_rate:.1%}")
            
            return success_rate >= 0.7  # 70% успешности
            
        except Exception as e:
            print(f"❌ Ошибка запуска тестов: {e}")
            return False
    
    def run_full_test(self):
        """Полный цикл тестирования"""
        print("🎯 ПОЛНЫЙ ИНТЕГРАЦИОННЫЙ ТЕСТ")
        print("=" * 50)
        
        success = True
        
        try:
            # 1. Запуск основных сервисов
            print(f"\n📋 ЭТАП 1: Запуск основных сервисов")
            print("-" * 30)
            
            for service_name, config in self.services.items():
                if not self.start_service(service_name, config):
                    print(f"❌ Не удалось запустить {config['name']}")
                    success = False
                    break
            
            if not success:
                return False
            
            # 2. Проверка vLLM моделей
            print(f"\n📋 ЭТАП 2: Проверка vLLM моделей")
            print("-" * 30)
            
            available_models = self.check_vllm_models()
            
            if not available_models:
                print(f"⚠️ vLLM модели недоступны, попытка запуска...")
                if not self.start_vllm_model():
                    print(f"❌ Не удалось запустить vLLM модель")
                    print(f"ℹ️ Тесты будут выполнены без vLLM интеграции")
            
            # 3. Пауза для стабилизации
            print(f"\n📋 ЭТАП 3: Стабилизация системы")
            print("-" * 30)
            print(f"⏳ Ожидание 10 секунд для стабилизации...")
            time.sleep(10)
            
            # 4. Запуск тестов
            print(f"\n📋 ЭТАП 4: Интеграционное тестирование")
            print("-" * 30)
            
            test_success = self.run_integration_tests()
            
            if test_success:
                print(f"\n🎉 ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            else:
                print(f"\n⚠️ Некоторые тесты не прошли, но система частично работает")
            
            return test_success
            
        except KeyboardInterrupt:
            print(f"\n⚠️ Тестирование прервано пользователем")
            return False
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            return False
        finally:
            # Всегда останавливаем сервисы
            self.stop_all_services()
    
    def run_quick_test(self):
        """Быстрый тест без запуска сервисов"""
        print("⚡ БЫСТРЫЙ ИНТЕГРАЦИОННЫЙ ТЕСТ")
        print("=" * 40)
        
        print(f"ℹ️ Проверка уже запущенных сервисов...")
        
        # Проверка API
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ API сервер доступен")
            else:
                print(f"❌ API сервер недоступен")
        except:
            print(f"❌ API сервер недоступен")
        
        # Проверка Streamlit
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print(f"✅ Streamlit интерфейс доступен")
            else:
                print(f"❌ Streamlit интерфейс недоступен")
        except:
            print(f"❌ Streamlit интерфейс недоступен")
        
        # Проверка vLLM
        self.check_vllm_models()
        
        # Запуск тестов
        return self.run_integration_tests()

def signal_handler(sig, frame):
    """Обработчик сигнала для корректного завершения"""
    print(f"\n⚠️ Получен сигнал завершения, остановка сервисов...")
    sys.exit(0)

def main():
    """Основная функция"""
    # Установка обработчика сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    runner = FullIntegrationRunner()
    
    # Выбор режима тестирования
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = runner.run_quick_test()
    else:
        success = runner.run_full_test()
    
    if success:
        print(f"\n🎯 ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        sys.exit(0)
    else:
        print(f"\n⚠️ ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ПРОБЛЕМАМИ")
        sys.exit(1)

if __name__ == "__main__":
    main()