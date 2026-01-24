#!/usr/bin/env python3
"""
Комплексное тестирование всех моделей vLLM по очереди
"""

import json
import subprocess
import time
import requests
import base64
import os
from pathlib import Path
from typing import Dict, List, Any

class ComprehensiveModelTester:
    def __init__(self):
        self.cache_path = str(os.path.expanduser("~/.cache/huggingface/hub")).replace('\\', '/')
        self.test_images = [
            "test_documents/01_simple_text.png",
            "test_documents/02_table.png", 
            "test_documents/04_numbers.png"
        ]
        self.text_prompts = [
            "Привет! Как дела?",
            "Что такое искусственный интеллект?",
            "Опиши процесс машинного обучения кратко"
        ]
        self.results = {}
        
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
    
    def launch_model(self, model_name, config, timeout=300):
        """Запуск модели"""
        print(f"\n🚀 ЗАПУСК МОДЕЛИ: {model_name}")
        print("=" * 50)
        
        container_name = config['container_name']
        port = config['port']
        vllm_params = config['vllm_params']
        
        # Остановка существующих контейнеров
        self.run_command(f"docker stop {container_name}")
        self.run_command(f"docker rm {container_name}")
        
        # Проверка памяти перед запуском
        gpu_info = self.check_gpu_memory()
        if gpu_info:
            print(f"💾 GPU память: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
            print(f"💾 Свободно: {gpu_info['free_mb']} МБ")
        
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
        
        print(f"📦 Контейнер: {container_name}")
        print(f"🌐 Порт: {port}")
        print(f"💾 Размер модели: {config['size_gb']} ГБ")
        print(f"⚙️ Max tokens: {vllm_params['max_model_len']}")
        print(f"🎮 GPU utilization: {vllm_params['gpu_memory_utilization']}")
        
        # Запуск контейнера
        success, output = self.run_command(docker_command)
        
        if not success:
            print(f"❌ Ошибка запуска контейнера: {output}")
            return False
        
        print(f"✅ Контейнер запущен, ожидание готовности...")
        
        # Ожидание готовности
        start_time = time.time()
        last_log_time = start_time
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    launch_time = time.time() - start_time
                    print(f"🎉 Модель готова за {int(launch_time)} секунд!")
                    
                    # Проверка памяти после запуска
                    gpu_info = self.check_gpu_memory()
                    if gpu_info:
                        print(f"💾 GPU память после запуска: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
                    
                    return True
                    
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                print(f"⚠️ Ошибка проверки: {e}")
            
            # Показ логов каждые 30 секунд
            current_time = time.time()
            if current_time - last_log_time > 30:
                elapsed = int(current_time - start_time)
                print(f"⏳ Ожидание {elapsed}/{timeout}с...")
                
                # Показ последних логов
                success_log, logs = self.run_command(f"docker logs {container_name} --tail 3")
                if success_log and logs:
                    print(f"📋 Последние логи: {logs.split()[-1] if logs.split() else 'нет логов'}")
                
                last_log_time = current_time
            
            time.sleep(10)
        
        # Модель не запустилась
        print(f"❌ Модель не готова за {timeout} секунд")
        print(f"📋 Проверка логов...")
        
        success_log, logs = self.run_command(f"docker logs {container_name} --tail 20")
        if success_log:
            print("Последние логи:")
            print(logs)
        
        return False
    
    def test_model_ocr(self, model_name, port, image_path):
        """Тестирование OCR"""
        if not Path(image_path).exists():
            return {"success": False, "error": f"Файл не найден: {image_path}"}
        
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "model": model_name,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this image"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            start_time = time.time()
            response = requests.post(
                f"http://localhost:{port}/v1/chat/completions",
                json=payload,
                timeout=120
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                text = result["choices"][0]["message"]["content"]
                
                return {
                    "success": True,
                    "text": text,
                    "processing_time": round(processing_time, 2),
                    "word_count": len(text.split()),
                    "char_count": len(text),
                    "usage": result.get("usage", {}),
                    "image": Path(image_path).name
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_model_text(self, model_name, port, prompt):
        """Тестирование генерации текста"""
        try:
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
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
                
                return {
                    "success": True,
                    "text": text,
                    "processing_time": round(processing_time, 2),
                    "word_count": len(text.split()),
                    "usage": result.get("usage", {}),
                    "prompt": prompt[:30] + "..."
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_single_model(self, model_name, config):
        """Полное тестирование одной модели"""
        print(f"\n🧪 ТЕСТИРОВАНИЕ МОДЕЛИ: {model_name}")
        print("=" * 60)
        
        # Запуск модели
        if not self.launch_model(model_name, config):
            return {
                "model_name": model_name,
                "launch_success": False,
                "error": "Не удалось запустить модель",
                "ocr_tests": [],
                "text_tests": [],
                "performance": {}
            }
        
        port = config['port']
        model_results = {
            "model_name": model_name,
            "launch_success": True,
            "config": config,
            "ocr_tests": [],
            "text_tests": [],
            "performance": {}
        }
        
        # OCR тесты
        print(f"\n📷 OCR ТЕСТЫ")
        print("-" * 15)
        
        ocr_times = []
        ocr_successes = 0
        
        for image_path in self.test_images:
            if Path(image_path).exists():
                image_name = Path(image_path).name
                print(f"   🖼️ {image_name}...", end=" ")
                
                result = self.test_model_ocr(model_name, port, image_path)
                model_results["ocr_tests"].append(result)
                
                if result["success"]:
                    ocr_successes += 1
                    ocr_times.append(result["processing_time"])
                    print(f"✅ {result['processing_time']}с, {result['word_count']} слов")
                else:
                    print(f"❌ {result['error'][:50]}...")
        
        # Текстовые тесты
        print(f"\n💬 ТЕКСТОВЫЕ ТЕСТЫ")
        print("-" * 20)
        
        text_times = []
        text_successes = 0
        
        for prompt in self.text_prompts:
            print(f"   📝 {prompt[:30]}...", end=" ")
            
            result = self.test_model_text(model_name, port, prompt)
            model_results["text_tests"].append(result)
            
            if result["success"]:
                text_successes += 1
                text_times.append(result["processing_time"])
                print(f"✅ {result['processing_time']}с, {result['word_count']} слов")
            else:
                print(f"❌ {result['error'][:50]}...")
        
        # Расчет производительности
        model_results["performance"] = {
            "ocr_success_rate": round((ocr_successes / len(self.test_images)) * 100, 1) if self.test_images else 0,
            "ocr_avg_time": round(sum(ocr_times) / len(ocr_times), 2) if ocr_times else 0,
            "ocr_avg_words": round(sum(r["word_count"] for r in model_results["ocr_tests"] if r["success"]) / len([r for r in model_results["ocr_tests"] if r["success"]]), 1) if [r for r in model_results["ocr_tests"] if r["success"]] else 0,
            "text_success_rate": round((text_successes / len(self.text_prompts)) * 100, 1),
            "text_avg_time": round(sum(text_times) / len(text_times), 2) if text_times else 0,
            "text_avg_words": round(sum(r["word_count"] for r in model_results["text_tests"] if r["success"]) / len([r for r in model_results["text_tests"] if r["success"]]), 1) if [r for r in model_results["text_tests"] if r["success"]] else 0,
            "total_tests": len(self.test_images) + len(self.text_prompts),
            "total_successes": ocr_successes + text_successes
        }
        
        # Показ результатов
        perf = model_results["performance"]
        print(f"\n📊 РЕЗУЛЬТАТЫ:")
        print(f"   📷 OCR: {perf['ocr_success_rate']}% успех, {perf['ocr_avg_time']}с среднее, {perf['ocr_avg_words']} слов")
        print(f"   💬 Текст: {perf['text_success_rate']}% успех, {perf['text_avg_time']}с среднее, {perf['text_avg_words']} слов")
        print(f"   🎯 Общий результат: {perf['total_successes']}/{perf['total_tests']}")
        
        # Остановка модели
        container_name = config['container_name']
        print(f"\n🛑 Остановка {container_name}...")
        self.run_command(f"docker stop {container_name}")
        self.run_command(f"docker rm {container_name}")
        
        return model_results
    
    def run_comprehensive_test(self):
        """Комплексное тестирование всех моделей"""
        print("🔬 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ ВСЕХ МОДЕЛЕЙ vLLM")
        print("=" * 55)
        
        # Загрузка конфигураций
        try:
            with open('vllm_models_config.json', 'r', encoding='utf-8') as f:
                configs = json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
            return
        
        # Порядок тестирования (от легких к тяжелым)
        test_order = [
            "rednote-hilab/dots.ocr",
            "Qwen/Qwen3-VL-2B-Instruct",
            "Qwen/Qwen2-VL-2B-Instruct", 
            "Qwen/Qwen2.5-VL-7B-Instruct",
            "microsoft/Phi-3.5-vision-instruct",
            "Qwen/Qwen2-VL-7B-Instruct"
        ]
        
        print(f"📋 Планируется тестирование {len([m for m in test_order if m in configs])} моделей")
        print(f"⏱️ Примерное время: {len([m for m in test_order if m in configs]) * 10} минут")
        
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": {},
            "summary": {}
        }
        
        # Тестирование каждой модели
        for i, model_name in enumerate(test_order, 1):
            if model_name not in configs:
                print(f"⚠️ {model_name} - не найдена в конфигурации")
                continue
            
            print(f"\n{'='*70}")
            print(f"🔄 МОДЕЛЬ {i}/{len([m for m in test_order if m in configs])}: {model_name}")
            print(f"{'='*70}")
            
            config = configs[model_name]
            result = self.test_single_model(model_name, config)
            all_results["models"][model_name] = result
            
            # Пауза между моделями
            if i < len([m for m in test_order if m in configs]):
                print(f"\n⏸️ Пауза 10 секунд перед следующей моделью...")
                time.sleep(10)
        
        # Анализ всех результатов
        self.analyze_all_results(all_results)
        
        # Сохранение результатов
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_vllm_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Полные результаты сохранены в: {filename}")
        
        return all_results
    
    def analyze_all_results(self, results):
        """Анализ результатов всех моделей"""
        print(f"\n🏆 ИТОГОВЫЙ АНАЛИЗ ВСЕХ МОДЕЛЕЙ")
        print("=" * 40)
        
        successful_models = []
        failed_models = []
        
        for model_name, result in results["models"].items():
            if result["launch_success"]:
                successful_models.append((model_name, result))
            else:
                failed_models.append(model_name)
        
        print(f"✅ Успешно протестировано: {len(successful_models)} моделей")
        print(f"❌ Не удалось запустить: {len(failed_models)} моделей")
        
        if failed_models:
            print(f"\n❌ НЕУДАЧНЫЕ МОДЕЛИ:")
            for model_name in failed_models:
                print(f"   • {model_name}")
        
        if successful_models:
            print(f"\n📊 РЕЙТИНГ МОДЕЛЕЙ:")
            
            # Сортировка по общему успеху
            successful_models.sort(key=lambda x: x[1]["performance"]["total_successes"], reverse=True)
            
            print(f"\n🎯 ПО ОБЩЕМУ УСПЕХУ:")
            for i, (model_name, result) in enumerate(successful_models, 1):
                perf = result["performance"]
                print(f"   {i}. {model_name}")
                print(f"      Успех: {perf['total_successes']}/{perf['total_tests']}")
                print(f"      OCR: {perf['ocr_success_rate']}% ({perf['ocr_avg_time']}с)")
                print(f"      Текст: {perf['text_success_rate']}% ({perf['text_avg_time']}с)")
            
            # Лучшие по категориям
            best_ocr = max(successful_models, key=lambda x: x[1]["performance"]["ocr_success_rate"])
            fastest_ocr = min([m for m in successful_models if m[1]["performance"]["ocr_avg_time"] > 0], 
                            key=lambda x: x[1]["performance"]["ocr_avg_time"])
            best_text = max(successful_models, key=lambda x: x[1]["performance"]["text_avg_words"])
            
            print(f"\n🏅 ЛУЧШИЕ ПО КАТЕГОРИЯМ:")
            print(f"   📷 Лучший OCR: {best_ocr[0]} ({best_ocr[1]['performance']['ocr_success_rate']}%)")
            print(f"   ⚡ Самый быстрый OCR: {fastest_ocr[0]} ({fastest_ocr[1]['performance']['ocr_avg_time']}с)")
            print(f"   💬 Лучший текст: {best_text[0]} ({best_text[1]['performance']['text_avg_words']} слов)")
            
            # Сохранение сводки
            results["summary"] = {
                "total_tested": len(successful_models),
                "total_failed": len(failed_models),
                "best_ocr_model": best_ocr[0],
                "fastest_ocr_model": fastest_ocr[0],
                "best_text_model": best_text[0]
            }

def main():
    """Основная функция"""
    tester = ComprehensiveModelTester()
    
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ")
    print("=" * 40)
    
    # Проверка GPU
    gpu_info = tester.check_gpu_memory()
    if gpu_info:
        print(f"🎮 GPU память: {gpu_info['used_mb']}/{gpu_info['total_mb']} МБ ({gpu_info['usage_percent']}%)")
        print(f"💾 Свободно: {gpu_info['free_mb']} МБ")
    
    # Запуск тестирования
    results = tester.run_comprehensive_test()
    
    if results:
        print(f"\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print(f"📊 Протестировано моделей: {len(results['models'])}")
    else:
        print(f"\n❌ Тестирование не выполнено")

if __name__ == "__main__":
    main()