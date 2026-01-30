#!/usr/bin/env python3
"""
Исправленный тест vLLM API с правильными именами моделей
"""

import requests
import json
import time
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

class FixedVLLMTester:
    def __init__(self):
        self.vllm_endpoints = {
            "dots.ocr": "http://localhost:8000",
            "Qwen3-VL-2B": "http://localhost:8010", 
            "Qwen2-VL-2B": "http://localhost:8011"
        }
        self.test_image_path = "test_vllm_fixed.png"
        self.model_names_cache = {}  # Кеш правильных имен моделей
        
        # Создание тестового изображения
        self.create_test_image()
    
    def create_test_image(self):
        """Создание тестового изображения"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            font_title = ImageFont.truetype("arialbd.ttf", 24)
        except:
            font = font_title = ImageFont.load_default()
        
        # Заголовок
        draw.text((50, 30), "vLLM FIXED INTEGRATION TEST", fill='black', font=font_title)
        
        # Тестовый контент
        content = """
ИСПРАВЛЕННЫЙ ТЕСТ vLLM API

Этот документ создан для тестирования исправленной интеграции с vLLM.

Основная информация:
• Дата создания: 24.01.2026
• Номер документа: VLLM-FIX-2026-001
• Статус: ТЕСТИРОВАНИЕ

Многоязычный контент:
• Русский: Система исправлена!
• English: System is fixed!
• Français: Le système est réparé!

Числовые данные:
• Количество: 42
• Цена: 1,234.56 ₽
• Процент: 95.7%

Контактная информация:
📧 Email: fixed@vllm-test.com
📞 Телефон: +7 (999) 111-22-33
🌐 Сайт: https://vllm-fixed.example.com
        """
        
        draw.multiline_text((50, 80), content.strip(), fill='black', font=font, spacing=5)
        
        # Рамка
        draw.rectangle([(30, 20), (770, 580)], outline='black', width=2)
        
        img.save(self.test_image_path)
        print(f"✅ Создано тестовое изображение: {self.test_image_path}")
    
    def get_model_name(self, endpoint: str) -> str:
        """Получение правильного имени модели через /v1/models"""
        if endpoint in self.model_names_cache:
            return self.model_names_cache[endpoint]
        
        try:
            response = requests.get(f"{endpoint}/v1/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                if models:
                    model_name = models[0].get('id', 'unknown')
                    self.model_names_cache[endpoint] = model_name
                    print(f"   📝 Получено имя модели: {model_name}")
                    return model_name
            
            print(f"   ⚠️ Не удалось получить имя модели, используем fallback")
            return "unknown"
            
        except Exception as e:
            print(f"   ❌ Ошибка получения имени модели: {e}")
            return "unknown"
    
    def test_vllm_health(self, model_name: str, endpoint: str) -> dict:
        """Тест health endpoint"""
        try:
            response = requests.get(f"{endpoint}/health", timeout=10)
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "unhealthy",
                    "http_code": response.status_code
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_vllm_models_endpoint(self, endpoint: str) -> dict:
        """Тест /v1/models endpoint"""
        try:
            response = requests.get(f"{endpoint}/v1/models", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                
                return {
                    "status": "success",
                    "models_count": len(models),
                    "models": [m.get('id', 'unknown') for m in models],
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "status": "error",
                    "http_code": response.status_code,
                    "error": response.text[:200]
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_vllm_text_completion(self, endpoint: str) -> dict:
        """Тест текстового completion с правильным именем модели"""
        try:
            # Получаем правильное имя модели
            model_name = self.get_model_name(endpoint)
            if model_name == "unknown":
                return {"status": "error", "error": "Could not get model name"}
            
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": "Hello! How are you today? Please respond briefly."}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            start_time = time.time()
            response = requests.post(
                f"{endpoint}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if 'choices' in data and len(data['choices']) > 0:
                    message = data['choices'][0].get('message', {})
                    content = message.get('content', '')
                    
                    return {
                        "status": "success",
                        "model_name": model_name,
                        "response": content,
                        "response_length": len(content),
                        "processing_time": processing_time,
                        "usage": data.get('usage', {})
                    }
                else:
                    return {
                        "status": "error",
                        "error": "No choices in response",
                        "response": data
                    }
            else:
                return {
                    "status": "error",
                    "http_code": response.status_code,
                    "error": response.text[:300]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_vllm_vision_completion(self, endpoint: str) -> dict:
        """Тест vision completion с изображением"""
        try:
            # Получаем правильное имя модели
            model_name = self.get_model_name(endpoint)
            if model_name == "unknown":
                return {"status": "error", "error": "Could not get model name"}
            
            # Кодирование изображения
            with open(self.test_image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract all text from this image and describe what you see."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1
            }
            
            start_time = time.time()
            response = requests.post(
                f"{endpoint}/v1/chat/completions",
                json=payload,
                timeout=120
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if 'choices' in data and len(data['choices']) > 0:
                    message = data['choices'][0].get('message', {})
                    content = message.get('content', '')
                    
                    # Анализ качества OCR
                    expected_keywords = [
                        'vLLM', 'FIXED', 'INTEGRATION', 'TEST', 'ИСПРАВЛЕННЫЙ',
                        '24.01.2026', 'VLLM-FIX-2026-001', 'ТЕСТИРОВАНИЕ',
                        'fixed@vllm-test.com', '+7 (999) 111-22-33'
                    ]
                    
                    found_keywords = sum(1 for keyword in expected_keywords 
                                       if keyword.lower() in content.lower())
                    accuracy = found_keywords / len(expected_keywords)
                    
                    return {
                        "status": "success",
                        "model_name": model_name,
                        "response": content,
                        "response_length": len(content),
                        "processing_time": processing_time,
                        "ocr_accuracy": accuracy,
                        "found_keywords": found_keywords,
                        "total_keywords": len(expected_keywords),
                        "usage": data.get('usage', {})
                    }
                else:
                    return {
                        "status": "error",
                        "error": "No choices in response",
                        "response": data
                    }
            else:
                return {
                    "status": "error",
                    "http_code": response.status_code,
                    "error": response.text[:300]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_single_model(self, model_name: str, endpoint: str) -> dict:
        """Полное тестирование одной модели"""
        print(f"\n🧪 Тестирование модели: {model_name}")
        print(f"🌐 Endpoint: {endpoint}")
        print("-" * 50)
        
        model_results = {
            "model_name": model_name,
            "endpoint": endpoint,
            "tests": {},
            "success_rate": 0,
            "successful_tests": 0,
            "total_tests": 0
        }
        
        # 1. Health check
        print("   1️⃣ Health check...")
        health_result = self.test_vllm_health(model_name, endpoint)
        model_results["tests"]["health"] = health_result
        
        if health_result["status"] == "healthy":
            print(f"      ✅ Модель здорова ({health_result['response_time']:.2f}с)")
        else:
            print(f"      ❌ Модель недоступна: {health_result.get('error', 'Unknown error')}")
            model_results["success_rate"] = 0
            model_results["total_tests"] = 1
            return model_results
        
        # 2. Models endpoint
        print("   2️⃣ Models endpoint...")
        models_result = self.test_vllm_models_endpoint(endpoint)
        model_results["tests"]["models"] = models_result
        
        if models_result["status"] == "success":
            print(f"      ✅ Найдено моделей: {models_result['models_count']}")
            if models_result["models"]:
                print(f"      📝 Модели: {', '.join(models_result['models'])}")
        else:
            print(f"      ❌ Ошибка models endpoint: {models_result.get('error', 'Unknown')}")
        
        # 3. Text completion
        print("   3️⃣ Text completion...")
        text_result = self.test_vllm_text_completion(endpoint)
        model_results["tests"]["text_completion"] = text_result
        
        if text_result["status"] == "success":
            response_preview = text_result["response"][:100] + "..." if len(text_result["response"]) > 100 else text_result["response"]
            print(f"      ✅ Текст: {response_preview}")
            print(f"      ⏱️ Время: {text_result['processing_time']:.2f}с")
            print(f"      🤖 Модель: {text_result['model_name']}")
        else:
            print(f"      ❌ Ошибка text completion: {text_result.get('error', 'Unknown')}")
        
        # 4. Vision completion
        print("   4️⃣ Vision completion...")
        vision_result = self.test_vllm_vision_completion(endpoint)
        model_results["tests"]["vision_completion"] = vision_result
        
        if vision_result["status"] == "success":
            print(f"      ✅ Vision OCR точность: {vision_result['ocr_accuracy']:.1%}")
            print(f"      ⏱️ Время: {vision_result['processing_time']:.2f}с")
            print(f"      📝 Найдено ключевых слов: {vision_result['found_keywords']}/{vision_result['total_keywords']}")
            print(f"      🤖 Модель: {vision_result['model_name']}")
        else:
            print(f"      ❌ Ошибка vision completion: {vision_result.get('error', 'Unknown')}")
        
        # Подсчет успешности
        successful_tests = sum(1 for test in model_results["tests"].values() 
                             if test.get("status") in ["success", "healthy"])
        total_tests = len(model_results["tests"])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        model_results["success_rate"] = success_rate
        model_results["successful_tests"] = successful_tests
        model_results["total_tests"] = total_tests
        
        print(f"   📊 Успешность: {success_rate:.1%} ({successful_tests}/{total_tests})")
        
        return model_results
    
    def run_all_tests(self):
        """Запуск тестов для всех моделей"""
        print("🚀 ИСПРАВЛЕННОЕ ТЕСТИРОВАНИЕ vLLM API")
        print("=" * 50)
        
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_image": self.test_image_path,
            "models": {},
            "summary": {
                "total_models": len(self.vllm_endpoints),
                "available_models": 0,
                "working_models": 0,
                "avg_success_rate": 0
            }
        }
        
        # Тестирование каждой модели
        for model_name, endpoint in self.vllm_endpoints.items():
            model_result = self.test_single_model(model_name, endpoint)
            all_results["models"][model_name] = model_result
            
            # Обновление статистики
            if model_result["tests"]["health"]["status"] == "healthy":
                all_results["summary"]["available_models"] += 1
                
                if model_result["success_rate"] >= 0.75:  # 75% успешности
                    all_results["summary"]["working_models"] += 1
        
        # Расчет средней успешности
        success_rates = [result["success_rate"] for result in all_results["models"].values()]
        if success_rates:
            all_results["summary"]["avg_success_rate"] = sum(success_rates) / len(success_rates)
        
        # Сохранение результатов
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"vllm_fixed_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # Финальный отчет
        self.generate_final_report(all_results, results_file)
        
        return all_results
    
    def generate_final_report(self, results: dict, results_file: str):
        """Генерация финального отчета"""
        print(f"\n🏆 ФИНАЛЬНЫЙ ОТЧЕТ ИСПРАВЛЕННОГО vLLM ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        summary = results["summary"]
        
        print(f"📊 Общая статистика:")
        print(f"   Всего моделей: {summary['total_models']}")
        print(f"   Доступных: {summary['available_models']}")
        print(f"   Работающих: {summary['working_models']}")
        print(f"   Средняя успешность: {summary['avg_success_rate']:.1%}")
        
        print(f"\n📋 Детали по моделям:")
        for model_name, result in results["models"].items():
            status_icon = "✅" if result["success_rate"] >= 0.75 else "⚠️" if result["success_rate"] >= 0.5 else "❌"
            print(f"   {status_icon} {model_name}: {result['success_rate']:.1%} ({result['successful_tests']}/{result['total_tests']})")
            
            # Показать правильное имя модели если получено
            for test_name, test_result in result["tests"].items():
                if test_result.get("model_name") and test_result["model_name"] != "unknown":
                    print(f"      🤖 Реальное имя модели: {test_result['model_name']}")
                    break
        
        print(f"\n💾 Результаты сохранены: {results_file}")
        
        # Рекомендации
        print(f"\n💡 Рекомендации:")
        
        if summary["working_models"] == summary["total_models"]:
            print("   🎉 Все модели работают отлично! vLLM интеграция полностью готова.")
        elif summary["working_models"] >= summary["total_models"] * 0.5:
            print("   ✅ Большинство моделей работает. vLLM интеграция в основном готова.")
            print("   🔧 Рекомендуется исправить проблемы с неработающими моделями.")
        else:
            print("   ⚠️ Много проблем с моделями. Требуется диагностика vLLM.")
            print("   🛠️ Проверьте запуск vLLM контейнеров и конфигурацию.")
        
        if summary["available_models"] == 0:
            print("   🚨 Ни одна vLLM модель недоступна!")
            print("   🔧 Запустите модели: python launch_working_models.py")
        
        # Показать правильные имена моделей
        if self.model_names_cache:
            print(f"\n📝 ПРАВИЛЬНЫЕ ИМЕНА МОДЕЛЕЙ:")
            for endpoint, model_name in self.model_names_cache.items():
                print(f"   {endpoint} → {model_name}")

def main():
    """Основная функция"""
    tester = FixedVLLMTester()
    
    print("🔍 Подготовка к исправленному тестированию vLLM API...")
    print(f"📁 Тестовое изображение: {tester.test_image_path}")
    print(f"🎯 Модели для тестирования: {list(tester.vllm_endpoints.keys())}")
    
    # Запуск тестов
    results = tester.run_all_tests()
    
    # Очистка
    if Path(tester.test_image_path).exists():
        Path(tester.test_image_path).unlink()
        print(f"🧹 Тестовое изображение удалено")
    
    print(f"\n🎯 ИСПРАВЛЕННОЕ vLLM API ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    
    # Возврат кода выхода
    summary = results["summary"]
    if summary["working_models"] >= summary["total_models"] * 0.5:
        return 0  # Успех
    else:
        return 1  # Проблемы

if __name__ == "__main__":
    import sys
    sys.exit(main())