#!/usr/bin/env python3
"""
Тестирование двух запущенных моделей: dots.ocr и Qwen3-VL
"""

import requests
import base64
import time
import json
from pathlib import Path

class TwoModelTester:
    def __init__(self):
        self.models = {
            "dots.ocr": {
                "url": "http://localhost:8000",
                "model_name": "rednote-hilab/dots.ocr",
                "category": "OCR"
            },
            "qwen3-vl": {
                "url": "http://localhost:8003", 
                "model_name": "Qwen/Qwen3-VL-2B-Instruct",
                "category": "VLM"
            }
        }
        
    def check_health(self, model_key):
        """Проверка доступности модели"""
        try:
            url = self.models[model_key]["url"]
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_image_ocr(self, model_key, image_path, prompt="Extract all text from this image"):
        """Тестирование OCR на изображении"""
        if not Path(image_path).exists():
            return {"success": False, "error": f"Файл не найден: {image_path}"}
        
        model_info = self.models[model_key]
        
        try:
            # Кодирование изображения
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Формирование запроса
            payload = {
                "model": model_info["model_name"],
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            start_time = time.time()
            response = requests.post(
                f"{model_info['url']}/v1/chat/completions",
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
                    "model": model_key
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_text_generation(self, model_key, prompt):
        """Тестирование генерации текста"""
        model_info = self.models[model_key]
        
        try:
            payload = {
                "model": model_info["model_name"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            start_time = time.time()
            response = requests.post(
                f"{model_info['url']}/v1/chat/completions",
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
                    "model": model_key
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_comparison_test(self):
        """Сравнительное тестирование моделей"""
        print("🔥 СРАВНИТЕЛЬНОЕ ТЕСТИРОВАНИЕ МОДЕЛЕЙ")
        print("=" * 45)
        
        # Проверка доступности
        available_models = []
        for model_key, model_info in self.models.items():
            if self.check_health(model_key):
                print(f"✅ {model_key} ({model_info['category']}) - доступна")
                available_models.append(model_key)
            else:
                print(f"❌ {model_key} ({model_info['category']}) - недоступна")
        
        if len(available_models) < 2:
            print(f"\n⚠️ Недостаточно моделей для сравнения ({len(available_models)}/2)")
            return
        
        print(f"\n🎯 Тестирование {len(available_models)} моделей...")
        
        # Тестовые изображения
        test_images = [
            "test_documents/01_simple_text.png",
            "test_documents/02_table.png",
            "test_documents/04_numbers.png"
        ]
        
        # Тестовые текстовые запросы
        text_prompts = [
            "Привет! Как дела?",
            "Что такое искусственный интеллект?",
            "Опиши процесс машинного обучения"
        ]
        
        results = {}
        
        # OCR тесты
        print(f"\n📷 OCR ТЕСТЫ")
        print("-" * 15)
        
        for image_path in test_images:
            if Path(image_path).exists():
                image_name = Path(image_path).name
                print(f"\n🖼️ Тест: {image_name}")
                
                for model_key in available_models:
                    print(f"   🔄 {model_key}...", end=" ")
                    
                    result = self.test_image_ocr(model_key, image_path)
                    
                    if model_key not in results:
                        results[model_key] = {"ocr": [], "text": []}
                    
                    results[model_key]["ocr"].append(result)
                    
                    if result["success"]:
                        print(f"✅ {result['processing_time']}с, {result['word_count']} слов")
                    else:
                        print(f"❌ {result['error'][:50]}...")
        
        # Текстовые тесты
        print(f"\n💬 ТЕКСТОВЫЕ ТЕСТЫ")
        print("-" * 20)
        
        for prompt in text_prompts:
            print(f"\n📝 Запрос: {prompt[:30]}...")
            
            for model_key in available_models:
                print(f"   🔄 {model_key}...", end=" ")
                
                result = self.test_text_generation(model_key, prompt)
                
                if model_key not in results:
                    results[model_key] = {"ocr": [], "text": []}
                
                results[model_key]["text"].append(result)
                
                if result["success"]:
                    print(f"✅ {result['processing_time']}с, {result['word_count']} слов")
                else:
                    print(f"❌ {result['error'][:50]}...")
        
        # Анализ результатов
        self.analyze_results(results)
        
        return results
    
    def analyze_results(self, results):
        """Анализ и сравнение результатов"""
        print(f"\n📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("=" * 25)
        
        for model_key, model_results in results.items():
            model_info = self.models[model_key]
            print(f"\n🤖 {model_key.upper()} ({model_info['category']})")
            print("-" * 30)
            
            # OCR статистика
            ocr_results = model_results.get("ocr", [])
            ocr_successes = [r for r in ocr_results if r["success"]]
            
            if ocr_results:
                ocr_success_rate = len(ocr_successes) / len(ocr_results) * 100
                avg_ocr_time = sum(r["processing_time"] for r in ocr_successes) / len(ocr_successes) if ocr_successes else 0
                avg_ocr_words = sum(r["word_count"] for r in ocr_successes) / len(ocr_successes) if ocr_successes else 0
                
                print(f"📷 OCR: {ocr_success_rate:.1f}% успех ({len(ocr_successes)}/{len(ocr_results)})")
                print(f"   Среднее время: {avg_ocr_time:.2f}с")
                print(f"   Среднее слов: {avg_ocr_words:.1f}")
            
            # Текстовая статистика
            text_results = model_results.get("text", [])
            text_successes = [r for r in text_results if r["success"]]
            
            if text_results:
                text_success_rate = len(text_successes) / len(text_results) * 100
                avg_text_time = sum(r["processing_time"] for r in text_successes) / len(text_successes) if text_successes else 0
                avg_text_words = sum(r["word_count"] for r in text_successes) / len(text_successes) if text_successes else 0
                
                print(f"💬 Текст: {text_success_rate:.1f}% успех ({len(text_successes)}/{len(text_results)})")
                print(f"   Среднее время: {avg_text_time:.2f}с")
                print(f"   Среднее слов: {avg_text_words:.1f}")
        
        # Сравнение
        if len(results) == 2:
            print(f"\n🏆 СРАВНЕНИЕ")
            print("-" * 15)
            
            model_keys = list(results.keys())
            model1, model2 = model_keys[0], model_keys[1]
            
            # OCR сравнение
            ocr1 = results[model1].get("ocr", [])
            ocr2 = results[model2].get("ocr", [])
            
            if ocr1 and ocr2:
                success1 = len([r for r in ocr1 if r["success"]])
                success2 = len([r for r in ocr2 if r["success"]])
                
                if success1 > success2:
                    print(f"📷 OCR лидер: {model1} ({success1} vs {success2})")
                elif success2 > success1:
                    print(f"📷 OCR лидер: {model2} ({success2} vs {success1})")
                else:
                    print(f"📷 OCR: равный результат ({success1})")
            
            # Скорость сравнение
            times1 = [r["processing_time"] for r in ocr1 + results[model1].get("text", []) if r["success"]]
            times2 = [r["processing_time"] for r in ocr2 + results[model2].get("text", []) if r["success"]]
            
            if times1 and times2:
                avg_time1 = sum(times1) / len(times1)
                avg_time2 = sum(times2) / len(times2)
                
                if avg_time1 < avg_time2:
                    print(f"⚡ Скорость лидер: {model1} ({avg_time1:.2f}с vs {avg_time2:.2f}с)")
                else:
                    print(f"⚡ Скорость лидер: {model2} ({avg_time2:.2f}с vs {avg_time1:.2f}с)")

def main():
    """Основная функция"""
    tester = TwoModelTester()
    
    print("🚀 ТЕСТИРОВАНИЕ ДВУХ МОДЕЛЕЙ")
    print("=" * 30)
    
    results = tester.run_comparison_test()
    
    if results:
        # Сохранение результатов
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"two_models_comparison_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Результаты сохранены в: {filename}")
        print(f"✅ Тестирование завершено!")
    else:
        print(f"\n❌ Тестирование не выполнено")

if __name__ == "__main__":
    main()