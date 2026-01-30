#!/usr/bin/env python3
"""
Финальное комплексное тестирование всех готовых моделей с увеличенными таймаутами
"""

import json
import subprocess
import time
import requests
import base64
import os
from pathlib import Path
from typing import Dict, List, Any

class FinalComprehensiveTester:
    def __init__(self):
        self.cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
        self.test_image = "test_documents/01_simple_text.png"
        
        # Все готовые модели с увеличенными таймаутами
        self.models_to_test = {
            "rednote-hilab/dots.ocr": {
                "container_name": "dots-ocr-final-test",
                "port": 8000,
                "timeout": 120,  # Быстрая модель
                "vllm_params": {
                    "max_model_len": 1024,
                    "gpu_memory_utilization": 0.85,
                    "trust_remote_code": True,
                    "enforce_eager": True
                },
                "status": "tested_working"
            },
            "Qwen/Qwen3-VL-2B-Instruct": {
                "container_name": "qwen3-vl-2b-final-test",
                "port": 8010,
                "timeout": 300,  # 5 минут
                "vllm_params": {
                    "max_model_len": 2048,
                    "gpu_memory_utilization": 0.7,
                    "trust_remote_code": True,
                    "enforce_eager": False
                },
                "status": "tested_working"
            },
            "Qwen/Qwen2-VL-2B-Instruct": {
                "container_name": "qwen2-vl-2b-final-test",
                "port": 8011,
                "timeout": 300,  # 5 минут
                "vllm_params": {
                    "max_model_len": 4096,
                    "gpu_memory_utilization": 0.7,
                    "trust_remote_code": True,
                    "enforce_eager": False
                },
                "status": "needs_testing"
            },
            "Qwen/Qwen2-VL-7B-Instruct": {
                "container_name": "qwen2-vl-7b-final-test",
                "port": 8013,
                "timeout": 360,  # 6 минут (большая модель)
                "vllm_params": {
                    "max_model_len": 4096,
                    "gpu_memory_utilization": 0.6,
                    "trust_remote_code": True,
                    "enforce_eager": False
                },
                "status": "needs_testing"
            },
            "microsoft/Phi-3.5-vision-instruct": {
                "container_name": "phi-3-5-vision-final-test",
                "port": 8014,
                "timeout": 360,  # 6 минут (большая модель)
                "vllm_params": {
                    "max_model_len": 4096,
                    "gpu_memory_utilization": 0.6,
                    "trust_remote_code": True,
                    "enforce_eager": False
                },
                "status": "needs_testing"
            },
            "stepfun-ai/GOT-OCR-2.0-hf": {
                "container_name": "got-ocr-2-0-hf-final-test",
                "port": 8002,
                "timeout": 240,  # 4 минуты
                "vllm_params": {
                    "max_model_len": 2048,
                    "gpu_memory_utilization": 0.7,
                    "trust_remote_code": True,
                    "enforce_eager": True
                },
                "status": "needs_testing"
            },
            "vikhyatk/moondream2": {
                "container_name": "moondream2-final-test",
                "port": 8023,
                "timeout": 240,  # 4 минуты
                "vllm_params": {
                    "max_model_len": 2048,
                    "gpu_memory_utilization": 0.6,
                    "trust_remote_code": True,
                    "enforce_eager": True
                },
                "status": "needs_testing"
            }
        }
        
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
    
    def encode_image(self, image_path: str) -> str:
        """Кодирование изображения в base64"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Ошибка кодирования изображения: {e}")
            return None
    
    def test_model_launch(self, model_name: str, config: Dict) -> Dict[str, Any]:
        """Тестирование запуска модели с увеличенным таймаутом"""
        print(f"\n🧪 ТЕСТ ЗАПУСКА: {model_name}")
        print("-" * 50)
        
        container_name = config['container_name']
        port = config['port']
        timeout = config['timeout']
        vllm_params = config['vllm_params']
        
        # Проверка памяти
        gpu_info = self.check_gpu_memory()
        if gpu_info:
            print(f"💾 GPU до запуска: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
        
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
        print(f"⏱️ Таймаут: {timeout} секунд")
        
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
        
        results = {}
        
        # 1. Простой текстовый тест
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
                
                results["text_test"] = {
                    "success": True,
                    "response": text,
                    "processing_time": round(processing_time, 2),
                    "usage": result.get("usage", {})
                }
                print(f"   ✅ Текстовый тест: {text[:50]}...")
            else:
                results["text_test"] = {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                print(f"   ❌ Текстовый тест неудачен")
                
        except Exception as e:
            results["text_test"] = {
                "success": False,
                "error": str(e)
            }
            print(f"   ❌ Текстовый тест ошибка: {e}")
        
        # 2. Тест с изображением (если есть)
        if os.path.exists(self.test_image):
            try:
                image_base64 = self.encode_image(self.test_image)
                if image_base64:
                    payload = {
                        "model": model_name,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "What do you see in this image? Describe it briefly."},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 100,
                        "temperature": 0.1
                    }
                    
                    start_time = time.time()
                    response = requests.post(
                        f"http://localhost:{port}/v1/chat/completions",
                        json=payload,
                        timeout=60
                    )
                    processing_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        text = result["choices"][0]["message"]["content"]
                        
                        results["vision_test"] = {
                            "success": True,
                            "response": text,
                            "processing_time": round(processing_time, 2),
                            "usage": result.get("usage", {})
                        }
                        print(f"   ✅ Vision тест: {text[:50]}...")
                    else:
                        results["vision_test"] = {
                            "success": False,
                            "error": f"HTTP {response.status_code}: {response.text[:200]}"
                        }
                        print(f"   ❌ Vision тест неудачен")
                        
            except Exception as e:
                results["vision_test"] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"   ❌ Vision тест ошибка: {e}")
        
        return results
    
    def cleanup_model(self, container_name: str):
        """Очистка модели"""
        print(f"🧹 Очистка {container_name}...")
        self.run_command(f"docker stop {container_name}")
        self.run_command(f"docker rm {container_name}")
    
    def run_comprehensive_test(self):
        """Запуск комплексного тестирования всех моделей"""
        print("🔬 ФИНАЛЬНОЕ КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ")
        print("=" * 50)
        
        # Очистка контейнеров
        self.cleanup_containers()
        
        # Проверка GPU
        gpu_info = self.check_gpu_memory()
        if gpu_info:
            print(f"🎮 GPU: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
        
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": {},
            "summary": {
                "total_tested": 0,
                "successful": 0,
                "failed": 0,
                "working_models": [],
                "failed_models": []
            }
        }
        
        # Тестирование каждой модели
        for i, (model_name, config) in enumerate(self.models_to_test.items(), 1):
            print(f"\n{'='*70}")
            print(f"🔄 МОДЕЛЬ {i}/{len(self.models_to_test)}: {model_name}")
            print(f"📊 Статус: {config['status']}, Таймаут: {config['timeout']}с")
            print(f"{'='*70}")
            
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
                
                # Проверка успешности
                text_success = functionality_result.get("text_test", {}).get("success", False)
                vision_success = functionality_result.get("vision_test", {}).get("success", False)
                
                if text_success or vision_success:
                    print(f"✅ Функциональность работает!")
                    all_results["summary"]["successful"] += 1
                    all_results["summary"]["working_models"].append(model_name)
                    model_result["status"] = "working"
                else:
                    print(f"❌ Функциональность не работает")
                    all_results["summary"]["failed"] += 1
                    all_results["summary"]["failed_models"].append(model_name)
                    model_result["status"] = "launch_ok_function_fail"
                
                # Очистка
                self.cleanup_model(config['container_name'])
                
            else:
                print(f"❌ Запуск неудачен: {launch_result['error']}")
                all_results["summary"]["failed"] += 1
                all_results["summary"]["failed_models"].append(model_name)
                model_result["status"] = "launch_failed"
                
                # Очистка контейнера
                self.cleanup_model(config['container_name'])
            
            all_results["models"][model_name] = model_result
            
            # Пауза между тестами
            if i < len(self.models_to_test):
                print(f"\n⏸️ Пауза 10 секунд...")
                time.sleep(10)
        
        # Финальная очистка
        self.cleanup_containers()
        
        # Сохранение результатов
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"final_comprehensive_test_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # Создание финальной конфигурации работающих моделей
        self.create_final_working_config(all_results)
        
        # Показ итогов
        self.show_final_summary(all_results)
        
        print(f"\n💾 Результаты сохранены в: {results_file}")
        
        return all_results
    
    def create_final_working_config(self, results: Dict[str, Any]):
        """Создание финальной конфигурации работающих моделей"""
        working_models = {}
        
        for model_name, result in results["models"].items():
            if result.get("status") == "working":
                config = result["config"].copy()
                config["status"] = "tested_working"
                config["last_tested"] = results["timestamp"]
                
                # Добавление результатов тестирования
                if result.get("functionality_result"):
                    func_result = result["functionality_result"]
                    config["test_results"] = {
                        "text_test_success": func_result.get("text_test", {}).get("success", False),
                        "vision_test_success": func_result.get("vision_test", {}).get("success", False),
                        "launch_time": result["launch_result"].get("launch_time", 0)
                    }
                
                working_models[model_name] = config
        
        if working_models:
            with open('final_working_models.json', 'w', encoding='utf-8') as f:
                json.dump(working_models, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Финальная конфигурация работающих моделей: final_working_models.json")
            print(f"✅ Найдено {len(working_models)} работающих моделей")
    
    def show_final_summary(self, results: Dict[str, Any]):
        """Показ финального отчета"""
        summary = results["summary"]
        
        print(f"\n🏆 ФИНАЛЬНЫЙ ОТЧЕТ")
        print("=" * 30)
        print(f"📊 Всего протестировано: {summary['total_tested']}")
        print(f"✅ Успешно работают: {summary['successful']}")
        print(f"❌ Не работают: {summary['failed']}")
        
        # Список работающих моделей
        if summary["working_models"]:
            print(f"\n🎉 РАБОТАЮЩИЕ МОДЕЛИ:")
            for model_name in summary["working_models"]:
                result = results["models"][model_name]
                config = result["config"]
                launch_time = result["launch_result"].get("launch_time", 0)
                print(f"   ✅ {model_name}")
                print(f"      Порт: {config['port']}, Время запуска: {int(launch_time)}с")
                
                func_result = result.get("functionality_result", {})
                text_ok = func_result.get("text_test", {}).get("success", False)
                vision_ok = func_result.get("vision_test", {}).get("success", False)
                print(f"      Текст: {'✅' if text_ok else '❌'}, Vision: {'✅' if vision_ok else '❌'}")
        
        # Список проблемных моделей
        if summary["failed_models"]:
            print(f"\n❌ ПРОБЛЕМНЫЕ МОДЕЛИ:")
            for model_name in summary["failed_models"]:
                result = results["models"][model_name]
                error = result["launch_result"].get("error", "Unknown error")
                print(f"   ❌ {model_name}: {error[:100]}...")

def main():
    """Основная функция"""
    tester = FinalComprehensiveTester()
    
    print("🚀 ЗАПУСК ФИНАЛЬНОГО КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    # Запуск тестирования
    results = tester.run_comprehensive_test()
    
    print(f"\n🎉 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    main()