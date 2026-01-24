#!/usr/bin/env python3
"""
Автоматическое тестирование всех моделей vLLM с очисткой несовместимых
"""

import json
import subprocess
import time
import requests
import base64
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any

class AutomatedModelTester:
    def __init__(self, config_file: str = "full_vllm_models_config.json"):
        self.config_file = config_file
        self.configs = self.load_configs()
        self.cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
        self.test_images = [
            "test_documents/01_simple_text.png",
            "test_documents/02_table.png", 
            "test_documents/04_numbers.png"
        ]
        self.results = {}
        self.incompatible_models = []
        
    def load_configs(self) -> Dict[str, Any]:
        """Загрузка конфигураций моделей"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
            return {}
    
    def run_command(self, command):
        """Выполнение команды"""
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip() if e.stderr else str(e)
    
    def check_gpu_memory(self):
        """Проверка памяти GPU"""
        success, output = self.run_command("nvidia-smi --query-gpu=memory.total,memory.used,memory.free --format=csv,noheader,nounits")
        
        if success:
            lines = output.strip().split('\n')
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) == 3:
                    total, used, free = map(int, parts)
                    return {
                        'total_mb': total,
                        'used_mb': used,
                        'free_mb': free,
                        'usage_percent': round((used / total) * 100, 1)
                    }
        return None
    
    def cleanup_containers(self):
        """Очистка всех контейнеров vLLM"""
        print("🧹 Очистка контейнеров...")
        success, output = self.run_command("docker ps -a --filter ancestor=vllm/vllm-openai:latest --format {{.Names}}")
        
        if success and output:
            container_names = output.strip().split('\n')
            for container_name in container_names:
                if container_name:
                    self.run_command(f"docker stop {container_name}")
                    self.run_command(f"docker rm {container_name}")
                    print(f"   🗑️ Удален {container_name}")
    
    def test_model_launch(self, model_name: str, config: Dict, timeout: int = 180) -> Dict[str, Any]:
        """Тестирование запуска модели"""
        print(f"\n🧪 ТЕСТ ЗАПУСКА: {model_name}")
        print("-" * 50)
        
        container_name = config['container_name']
        port = config['port']
        vllm_params = config['vllm_params']
        
        # Проверка памяти
        gpu_info = self.check_gpu_memory()
        if gpu_info:
            print(f"💾 GPU: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
        
        # Формирование команды Docker
        docker_command = f"""
        docker run -d \
            --gpus all \
            --name {container_name} \
            -p {port}:{port} \
            -v {self.cache_path}:/root/.cache/huggingface/hub:ro \
            --shm-size=8g \
            vllm/vllm-openai:latest \
            --model {model_name} \
            --trust-remote-code \
            --max-model-len {vllm_params['max_model_len']} \
            --gpu-memory-utilization {vllm_params['gpu_memory_utilization']} \
            --host 0.0.0.0 \
            --port {port} \
            --disable-log-requests
        """.strip().replace('\n', ' ').replace('\\', '')
        
        if vllm_params.get('enforce_eager'):
            docker_command += " --enforce-eager"
        
        print(f"🚀 Запуск контейнера {container_name}...")
        
        # Запуск контейнера
        success, output = self.run_command(docker_command)
        
        if not success:
            return {
                "launch_success": False,
                "error": f"Container start failed: {output}",
                "error_type": "container_start_error"
            }
        
        print(f"📦 Контейнер запущен, ожидание готовности...")
        
        # Ожидание готовности с мониторингом логов
        start_time = time.time()
        last_log_check = start_time
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    launch_time = time.time() - start_time
                    print(f"✅ Модель готова за {int(launch_time)} секунд!")
                    
                    # Проверка памяти после запуска
                    gpu_info = self.check_gpu_memory()
                    if gpu_info:
                        print(f"💾 GPU после запуска: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
                    
                    return {
                        "launch_success": True,
                        "launch_time": launch_time,
                        "gpu_memory_after": gpu_info
                    }
                    
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                print(f"⚠️ Ошибка проверки: {e}")
            
            # Проверка логов каждые 30 секунд
            current_time = time.time()
            if current_time - last_log_check > 30:
                elapsed = int(current_time - start_time)
                print(f"⏳ Ожидание {elapsed}/{timeout}с...")
                
                # Анализ логов на предмет ошибок
                success_log, logs = self.run_command(f"docker logs {container_name} --tail 10")
                if success_log and logs:
                    # Поиск критических ошибок
                    if "ImportError" in logs:
                        error_lines = [line for line in logs.split('\n') if 'ImportError' in line]
                        return {
                            "launch_success": False,
                            "error": f"Import error: {error_lines[-1] if error_lines else 'Unknown import error'}",
                            "error_type": "import_error",
                            "logs": logs
                        }
                    elif "ModuleNotFoundError" in logs:
                        error_lines = [line for line in logs.split('\n') if 'ModuleNotFoundError' in line]
                        return {
                            "launch_success": False,
                            "error": f"Module not found: {error_lines[-1] if error_lines else 'Unknown module error'}",
                            "error_type": "module_error",
                            "logs": logs
                        }
                    elif "CUDA out of memory" in logs:
                        return {
                            "launch_success": False,
                            "error": "CUDA out of memory",
                            "error_type": "memory_error",
                            "logs": logs
                        }
                
                last_log_check = current_time
            
            time.sleep(10)
        
        # Таймаут - получение финальных логов
        success_log, logs = self.run_command(f"docker logs {container_name} --tail 20")
        
        return {
            "launch_success": False,
            "error": f"Timeout after {timeout} seconds",
            "error_type": "timeout",
            "logs": logs if success_log else "No logs available"
        }
    
    def test_model_functionality(self, model_name: str, port: int) -> Dict[str, Any]:
        """Тестирование функциональности модели"""
        print(f"🔧 Тестирование функциональности...")
        
        # Простой текстовый тест
        try:
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hello, how are you?"}],
                "max_tokens": 50,
                "temperature": 0.1
            }
            
            start_time = time.time()
            response = requests.post(
                f"http://localhost:{port}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                text = result["choices"][0]["message"]["content"]
                
                return {
                    "text_test_success": True,
                    "text_response": text,
                    "text_processing_time": round(processing_time, 2),
                    "usage": result.get("usage", {})
                }
            else:
                return {
                    "text_test_success": False,
                    "text_error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except Exception as e:
            return {
                "text_test_success": False,
                "text_error": str(e)
            }
    
    def cleanup_model(self, container_name: str):
        """Очистка модели"""
        print(f"🧹 Очистка {container_name}...")
        self.run_command(f"docker stop {container_name}")
        self.run_command(f"docker rm {container_name}")
    
    def remove_incompatible_model_cache(self, model_name: str):
        """Удаление кеша несовместимой модели"""
        cache_dir_name = f"models--{model_name.replace('/', '--')}"
        cache_dir_path = Path(self.cache_path) / cache_dir_name
        
        if cache_dir_path.exists():
            try:
                shutil.rmtree(cache_dir_path)
                print(f"🗑️ Удален кеш модели: {model_name}")
                return True
            except Exception as e:
                print(f"❌ Ошибка удаления кеша {model_name}: {e}")
                return False
        else:
            print(f"⚠️ Кеш модели {model_name} не найден")
            return False
    
    def run_comprehensive_test(self):
        """Комплексное тестирование всех моделей"""
        print("🔬 АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ВСЕХ МОДЕЛЕЙ")
        print("=" * 50)
        
        # Очистка контейнеров
        self.cleanup_containers()
        
        # Сортировка моделей по приоритету
        sorted_models = sorted(
            self.configs.items(), 
            key=lambda x: (x[1]['priority'], x[1]['size_gb'])
        )
        
        print(f"📋 Планируется тестирование {len(sorted_models)} моделей")
        
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": {},
            "summary": {
                "total_tested": 0,
                "successful": 0,
                "failed": 0,
                "incompatible": 0,
                "removed_from_cache": 0
            }
        }
        
        # Тестирование каждой модели
        for i, (model_name, config) in enumerate(sorted_models, 1):
            print(f"\n{'='*70}")
            print(f"🔄 МОДЕЛЬ {i}/{len(sorted_models)}: {model_name}")
            print(f"📊 Приоритет: {config['priority']}, Размер: {config['size_gb']} ГБ")
            print(f"📋 Статус: {config['status']}")
            print(f"{'='*70}")
            
            # Пропуск заведомо несовместимых моделей
            if config['status'] == 'known_incompatible':
                print(f"⏭️ Пропуск заведомо несовместимой модели")
                
                # Предложение удалить из кеша
                print(f"🗑️ Удаление из кеша...")
                if self.remove_incompatible_model_cache(model_name):
                    all_results["summary"]["removed_from_cache"] += 1
                
                all_results["models"][model_name] = {
                    "status": "skipped_incompatible",
                    "reason": "Known incompatible model"
                }
                all_results["summary"]["incompatible"] += 1
                continue
            
            # Пропуск заведомо сломанных моделей
            if config['status'] == 'likely_broken':
                print(f"⏭️ Пропуск вероятно сломанной модели")
                
                # Предложение удалить из кеша
                print(f"🗑️ Удаление из кеша...")
                if self.remove_incompatible_model_cache(model_name):
                    all_results["summary"]["removed_from_cache"] += 1
                
                all_results["models"][model_name] = {
                    "status": "skipped_broken",
                    "reason": "Likely broken model (zero size)"
                }
                all_results["summary"]["incompatible"] += 1
                continue
            
            # Тестирование запуска
            launch_result = self.test_model_launch(model_name, config)
            all_results["summary"]["total_tested"] += 1
            
            model_result = {
                "config": config,
                "launch_result": launch_result,
                "functionality_result": None
            }
            
            if launch_result["launch_success"]:
                print(f"✅ Запуск успешен!")
                
                # Тестирование функциональности
                functionality_result = self.test_model_functionality(model_name, config['port'])
                model_result["functionality_result"] = functionality_result
                
                if functionality_result.get("text_test_success"):
                    print(f"✅ Функциональность работает!")
                    print(f"📝 Ответ: {functionality_result['text_response'][:100]}...")
                    all_results["summary"]["successful"] += 1
                    model_result["status"] = "working"
                else:
                    print(f"❌ Функциональность не работает: {functionality_result.get('text_error', 'Unknown error')}")
                    all_results["summary"]["failed"] += 1
                    model_result["status"] = "launch_ok_function_fail"
                
                # Очистка
                self.cleanup_model(config['container_name'])
                
            else:
                print(f"❌ Запуск неудачен: {launch_result['error']}")
                all_results["summary"]["failed"] += 1
                model_result["status"] = "launch_failed"
                
                # Анализ типа ошибки
                error_type = launch_result.get("error_type", "unknown")
                
                if error_type in ["import_error", "module_error"]:
                    print(f"🗑️ Модель несовместима, удаление из кеша...")
                    if self.remove_incompatible_model_cache(model_name):
                        all_results["summary"]["removed_from_cache"] += 1
                        model_result["cache_removed"] = True
                
                # Очистка контейнера
                self.cleanup_model(config['container_name'])
            
            all_results["models"][model_name] = model_result
            
            # Пауза между тестами
            if i < len(sorted_models):
                print(f"\n⏸️ Пауза 5 секунд...")
                time.sleep(5)
        
        # Финальная очистка
        self.cleanup_containers()
        
        # Сохранение результатов
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"automated_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # Создание обновленной конфигурации
        self.create_updated_config(all_results)
        
        # Показ итогов
        self.show_final_summary(all_results)
        
        print(f"\n💾 Результаты сохранены в: {results_file}")
        
        return all_results
    
    def create_updated_config(self, results: Dict[str, Any]):
        """Создание обновленной конфигурации на основе результатов"""
        working_models = {}
        
        for model_name, result in results["models"].items():
            if result.get("status") == "working":
                config = result["config"].copy()
                config["status"] = "tested_working"
                config["last_tested"] = results["timestamp"]
                working_models[model_name] = config
        
        if working_models:
            with open('working_vllm_models.json', 'w', encoding='utf-8') as f:
                json.dump(working_models, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Конфигурация работающих моделей сохранена: working_vllm_models.json")
            print(f"✅ Найдено {len(working_models)} работающих моделей")
    
    def show_final_summary(self, results: Dict[str, Any]):
        """Показ финального отчета"""
        summary = results["summary"]
        
        print(f"\n🏆 ФИНАЛЬНЫЙ ОТЧЕТ")
        print("=" * 30)
        print(f"📊 Всего протестировано: {summary['total_tested']}")
        print(f"✅ Успешно работают: {summary['successful']}")
        print(f"❌ Не работают: {summary['failed']}")
        print(f"⏭️ Несовместимые: {summary['incompatible']}")
        print(f"🗑️ Удалено из кеша: {summary['removed_from_cache']}")
        
        # Список работающих моделей
        working_models = [name for name, result in results["models"].items() 
                         if result.get("status") == "working"]
        
        if working_models:
            print(f"\n🎉 РАБОТАЮЩИЕ МОДЕЛИ:")
            for model_name in working_models:
                config = results["models"][model_name]["config"]
                print(f"   ✅ {model_name} (порт {config['port']}, {config['category']})")
        
        # Список проблемных моделей
        failed_models = [name for name, result in results["models"].items() 
                        if result.get("status") in ["launch_failed", "launch_ok_function_fail"]]
        
        if failed_models:
            print(f"\n❌ ПРОБЛЕМНЫЕ МОДЕЛИ:")
            for model_name in failed_models:
                result = results["models"][model_name]
                error = result["launch_result"].get("error", "Unknown error")
                print(f"   ❌ {model_name}: {error[:100]}...")

def main():
    """Основная функция"""
    tester = AutomatedModelTester()
    
    if not tester.configs:
        print("❌ Нет конфигураций для тестирования")
        return
    
    print("🚀 ЗАПУСК АВТОМАТИЧЕСКОГО ТЕСТИРОВАНИЯ")
    print("=" * 45)
    
    # Проверка GPU
    gpu_info = tester.check_gpu_memory()
    if gpu_info:
        print(f"🎮 GPU: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
    
    # Запуск тестирования
    results = tester.run_comprehensive_test()
    
    print(f"\n🎉 АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    main()