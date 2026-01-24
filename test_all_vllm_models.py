#!/usr/bin/env python3
"""
Тестирование всех моделей vLLM с реальными документами
"""

import json
import time
import requests
import base64
from pathlib import Path
from typing import Dict, Any, List

class VLLMModelTester:
    def __init__(self, config_file: str = "vllm_models_config.json"):
        self.config_file = config_file
        self.configs = self.load_configs()
        self.test_images = [
            "test_documents/01_simple_text.png",
            "test_documents/02_table.png", 
            "test_documents/04_numbers.png"
        ]
        
    def load_configs(self) -> Dict[str, Any]:
        """Загрузка конфигураций моделей"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
            return {}
    
    def check_model_health(self, model_name: str) -> bool:
        """Проверка доступности модели"""
        if model_name not in self.configs:
            return False
        
        port = self.configs[model_name]['port']
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_model_ocr(self, model_name: str, image_path: str) -> Dict[str, Any]:
        """Тестирование OCR модели"""
        if not Path(image_path).exists():
            return {"success": False, "error": f"Файл не найден: {image_path}"}
        
        port = self.configs[model_name]['port']
        
        try:
            # Кодирование изображения
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Формирование запроса
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
                    "image_path": image_path
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_model_text(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """Тестирование текстовой генерации"""
        port = self.configs[model_name]['port']
        
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
                    "usage": result.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Комплексное тестирование всех доступных моделей"""
        print("🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ МОДЕЛЕЙ VLLM")
        print("=" * 45)
        
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models_tested": {},
            "summary": {}
        }
        
        # Проверка доступных моделей
        available_models = []
        for model_name in self.configs:
            if self.check_model_health(model_name):
                available_models.append(model_name)
                print(f"✅ {model_name} - доступна")
            else:
                print(f"❌ {model_name} - недоступна")
        
        if not available_models:
            print("❌ Нет доступных моделей для тестирования")
            return results
        
        print(f"\n🎯 Тестирование {len(available_models)} моделей...")
        
        # Тестирование каждой модели
        for model_name in available_models:
            print(f"\n🔄 Тестирование {model_name}...")
            
            model_results = {
                "model_info": self.configs[model_name],
                "ocr_tests": [],
                "text_tests": [],
                "performance": {}
            }
            
            # OCR тесты
            ocr_times = []
            ocr_successes = 0
            
            for image_path in self.test_images:
                if Path(image_path).exists():
                    print(f"   📷 Тест OCR: {Path(image_path).name}")
                    result = self.test_model_ocr(model_name, image_path)
                    model_results["ocr_tests"].append(result)
                    
                    if result["success"]:
                        ocr_successes += 1
                        ocr_times.append(result["processing_time"])
                        print(f"      ✅ {result['processing_time']}с, {result['word_count']} слов")
                    else:
                        print(f"      ❌ {result['error']}")
            
            # Текстовые тесты
            text_prompts = [
                "Привет! Как дела?",
                "Опиши процесс фотосинтеза",
                "Что такое машинное обучение?"
            ]
            
            text_times = []
            text_successes = 0
            
            for prompt in text_prompts:
                print(f"   💬 Тест текста: {prompt[:30]}...")
                result = self.test_model_text(model_name, prompt)
                model_results["text_tests"].append(result)
                
                if result["success"]:
                    text_successes += 1
                    text_times.append(result["processing_time"])
                    print(f"      ✅ {result['processing_time']}с, {result['word_count']} слов")
                else:
                    print(f"      ❌ {result['error']}")
            
            # Расчет производительности
            model_results["performance"] = {
                "ocr_success_rate": round((ocr_successes / len(self.test_images)) * 100, 1) if self.test_images else 0,
                "ocr_avg_time": round(sum(ocr_times) / len(ocr_times), 2) if ocr_times else 0,
                "text_success_rate": round((text_successes / len(text_prompts)) * 100, 1),
                "text_avg_time": round(sum(text_times) / len(text_times), 2) if text_times else 0,
                "total_tests": len(self.test_images) + len(text_prompts),
                "total_successes": ocr_successes + text_successes
            }
            
            results["models_tested"][model_name] = model_results
            
            perf = model_results["performance"]
            print(f"   📊 OCR: {perf['ocr_success_rate']}% успех, {perf['ocr_avg_time']}с среднее")
            print(f"   📊 Текст: {perf['text_success_rate']}% успех, {perf['text_avg_time']}с среднее")
        
        # Общая сводка
        print(f"\n📈 СВОДКА РЕЗУЛЬТАТОВ")
        print("=" * 25)
        
        summary = {
            "total_models": len(available_models),
            "best_ocr_model": None,
            "best_text_model": None,
            "fastest_model": None
        }
        
        best_ocr_rate = 0
        best_text_rate = 0
        fastest_time = float('inf')
        
        for model_name, model_data in results["models_tested"].items():
            perf = model_data["performance"]
            
            # Лучшая OCR модель
            if perf["ocr_success_rate"] > best_ocr_rate:
                best_ocr_rate = perf["ocr_success_rate"]
                summary["best_ocr_model"] = model_name
            
            # Лучшая текстовая модель
            if perf["text_success_rate"] > best_text_rate:
                best_text_rate = perf["text_success_rate"]
                summary["best_text_model"] = model_name
            
            # Самая быстрая модель
            avg_time = (perf["ocr_avg_time"] + perf["text_avg_time"]) / 2
            if avg_time < fastest_time and avg_time > 0:
                fastest_time = avg_time
                summary["fastest_model"] = model_name
            
            print(f"🏆 {model_name}:")
            print(f"   OCR: {perf['ocr_success_rate']}% ({perf['ocr_avg_time']}с)")
            print(f"   Текст: {perf['text_success_rate']}% ({perf['text_avg_time']}с)")
            print(f"   Общий успех: {perf['total_successes']}/{perf['total_tests']}")
        
        results["summary"] = summary
        
        print(f"\n🥇 ЛУЧШИЕ МОДЕЛИ:")
        if summary["best_ocr_model"]:
            print(f"   OCR: {summary['best_ocr_model']} ({best_ocr_rate}%)")
        if summary["best_text_model"]:
            print(f"   Текст: {summary['best_text_model']} ({best_text_rate}%)")
        if summary["fastest_model"]:
            print(f"   Скорость: {summary['fastest_model']} ({fastest_time:.2f}с)")
        
        return results
    
    def save_results(self, results: Dict[str, Any]):
        """Сохранение результатов тестирования"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # JSON отчет
        json_file = f"vllm_test_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Текстовый отчет
        txt_file = f"vllm_test_summary_{timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ О ТЕСТИРОВАНИИ МОДЕЛЕЙ VLLM\n")
            f.write("=" * 40 + "\n")
            f.write(f"Дата: {results['timestamp']}\n")
            f.write(f"Протестировано моделей: {len(results['models_tested'])}\n\n")
            
            for model_name, model_data in results["models_tested"].items():
                f.write(f"МОДЕЛЬ: {model_name}\n")
                f.write("-" * 30 + "\n")
                
                config = model_data["model_info"]
                f.write(f"Категория: {config['category']}\n")
                f.write(f"Размер: {config['size_gb']} ГБ\n")
                f.write(f"Порт: {config['port']}\n")
                
                perf = model_data["performance"]
                f.write(f"OCR успех: {perf['ocr_success_rate']}%\n")
                f.write(f"OCR время: {perf['ocr_avg_time']}с\n")
                f.write(f"Текст успех: {perf['text_success_rate']}%\n")
                f.write(f"Текст время: {perf['text_avg_time']}с\n")
                f.write(f"Общий результат: {perf['total_successes']}/{perf['total_tests']}\n\n")
        
        print(f"\n💾 Результаты сохранены:")
        print(f"   📄 {json_file}")
        print(f"   📄 {txt_file}")

def main():
    """Основная функция"""
    tester = VLLMModelTester()
    
    if not tester.configs:
        print("❌ Нет конфигураций моделей")
        return
    
    # Запуск тестирования
    results = tester.run_comprehensive_test()
    
    if results["models_tested"]:
        tester.save_results(results)
        print("\n✅ Тестирование завершено!")
    else:
        print("\n❌ Тестирование не выполнено")

if __name__ == "__main__":
    main()