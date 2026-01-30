#!/usr/bin/env python3
"""
Специальный тест интеграции с vLLM API моделями
"""

import requests
import json
import time
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

class VLLMAPITester:
    def __init__(self):
        self.vllm_endpoints = {
            "dots.ocr": "http://localhost:8000",
            "Qwen3-VL-2B": "http://localhost:8010", 
            "Qwen2-VL-2B": "http://localhost:8011"
        }
        self.test_image_path = "test_vllm_integration.png"
        self.results = {}
        
        # Создание тестового изображения
        self.create_test_image()
    
    def create_test_image(self):
        """Создание тестового изображения для vLLM"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            font_title = ImageFont.truetype("arialbd.ttf", 24)
        except:
            font = font_title = ImageFont.load_default()
        
        # Заголовок
        draw.text((50, 30), "vLLM INTEGRATION TEST", fill='black', font=font_title)
        
        # Тестовый контент
        content = """
ТЕСТОВЫЙ ДОКУМЕНТ ДЛЯ vLLM

Этот документ создан для тестирования интеграции с vLLM API.

Основная информация:
• Дата создания: 24.01.2026
• Номер документа: VLM-2026-001
• Статус: АКТИВНЫЙ

Многоязычный контент:
• Русский: Привет, мир!
• English: Hello, world!
• Français: Bonjour le monde!

Числовые данные:
• Количество: 42
• Цена: 1,234.56 ₽
• Процент: 95.7%

Контактная информация:
📧 Email: test@vllm-integration.com
📞 Телефон: +7 (999) 123-45-67
🌐 Сайт: https://vllm-test.example.com
        """
        
        draw.multiline_text((50, 80), content.strip(), fill='black', font=font, spacing=5)
        
        # Рамка
        draw.rectangle([(30, 20), (770, 580)], outline='black', width=2)
        
        img.save(self.test_image_path)
        print(f"✅ Создано тестовое изображение: {self.test_image_path}")
    
    def encode_image_base64(self, image_path: str) -> str:
        """Кодирование изображения в base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def test_vllm_health(self, model_name: str, endpoint: str) -> dict:
        """Тест health endpoint vLLM модели"""
        try:
            response = requests.get(f"{endpoint}/health", timeout=10)
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "details": response.json() if response.content else {}
                }
            else:
                return {
                    "status": "unhealthy",
                    "http_code": response.status_code,
                    "error": response.text[:200]
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_vllm_models_endpoint(self, model_name: str, endpoint: str) -> dict:
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
    
    def test_vllm_text_completion(self, model_name: str, endpoint: str) -> dict:
        """Тест текстового completion"""
        try:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": "Hello! How are you today?"}
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
    
    def test_vllm_vision_completion(self, model_name: str, endpoint: str) -> dict:
        """Тест vision completion с изображением"""
        try:
            # Кодирование изображения
            image_base64 = self.encode_image_base64(self.test_image_path)
            
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
                timeout=120  # Больше времени для vision задач
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if 'choices' in data and len(data['choices']) > 0:
                    message = data['choices'][0].get('message', {})
                    content = message.get('content', '')
                    
                    # Анализ качества OCR
                    expected_keywords = [
                        'vLLM', 'INTEGRATION', 'TEST', 'ТЕСТОВЫЙ', 'ДОКУМЕНТ',
                        '24.01.2026', 'VLM-2026-001', 'АКТИВНЫЙ',
                        'test@vllm-integration.com', '+7 (999) 123-45-67'
                    ]
                    
                    found_keywords = sum(1 for keyword in expected_keywords 
                                       if keyword.lower() in content.lower())
                    accuracy = found_keywords / len(expected_keywords)
                    
                    return {
                        "status": "success",
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
            "tests": {}
        }
        
        # 1. Health check
        print("   1️⃣ Health check...")
        health_result = self.test_vllm_health(model_name, endpoint)
        model_results["tests"]["health"] = health_result
        
        if health_result["status"] == "healthy":
            print(f"      ✅ Модель здорова ({health_result['response_time']:.2f}с)")
        else:
            print(f"      ❌ Модель недоступна: {health_result.get('error', 'Unknown error')}")
            return model_results
        
        # 2. Models endpoint
        print("   2️⃣ Models endpoint...")
        models_result = self.test_vllm_models_endpoint(model_name, endpoint)
        model_results["tests"]["models"] = models_result
        
        if models_result["status"] == "success":
            print(f"      ✅ Найдено моделей: {models_result['models_count']}")
        else:
            print(f"      ❌ Ошибка models endpoint: {models_result.get('error', 'Unknown')}")
        
        # 3. Text completion
        print("   3️⃣ Text completion...")
        text_result = self.test_vllm_text_completion(model_name, endpoint)
        model_results["tests"]["text_completion"] = text_result
        
        if text_result["status"] == "success":
            response_preview = text_result["response"][:100] + "..." if len(text_result["response"]) > 100 else text_result["response"]
            print(f"      ✅ Текст: {response_preview}")
            print(f"      ⏱️ Время: {text_result['processing_time']:.2f}с")
        else:
            print(f"      ❌ Ошибка text completion: {text_result.get('error', 'Unknown')}")
        
        # 4. Vision completion (если поддерживается)
        print("   4️⃣ Vision completion...")
        vision_result = self.test_vllm_vision_completion(model_name, endpoint)
        model_results["tests"]["vision_completion"] = vision_result
        
        if vision_result["status"] == "success":
            print(f"      ✅ Vision OCR точность: {vision_result['ocr_accuracy']:.1%}")
            print(f"      ⏱️ Время: {vision_result['processing_time']:.2f}с")
            print(f"      📝 Найдено ключевых слов: {vision_result['found_keywords']}/{vision_result['total_keywords']}")
        else:
            print(f"      ❌ Ошибка vision completion: {vision_result.get('error', 'Unknown')}")
        
        # Общая оценка модели
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
        print("🚀 ТЕСТИРОВАНИЕ vLLM API ИНТЕГРАЦИИ")
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
        results_file = f"vllm_api_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # Финальный отчет
        self.generate_final_report(all_results, results_file)
        
        return all_results
    
    def generate_final_report(self, results: dict, results_file: str):
        """Генерация финального отчета"""
        print(f"\n🏆 ФИНАЛЬНЫЙ ОТЧЕТ vLLM API ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
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
            
            # Детали по тестам
            for test_name, test_result in result["tests"].items():
                test_status = test_result.get("status", "unknown")
                test_icon = "✅" if test_status in ["success", "healthy"] else "❌"
                print(f"      {test_icon} {test_name}: {test_status}")
        
        print(f"\n💾 Результаты сохранены: {results_file}")
        
        # Рекомендации
        print(f"\n💡 Рекомендации:")
        
        if summary["working_models"] == summary["total_models"]:
            print("   🎉 Все модели работают отлично! Система готова к продакшену.")
        elif summary["working_models"] >= summary["total_models"] * 0.5:
            print("   ✅ Большинство моделей работает. Система готова к использованию.")
            print("   🔧 Рекомендуется исправить проблемы с неработающими моделями.")
        else:
            print("   ⚠️ Много проблем с моделями. Требуется диагностика.")
            print("   🛠️ Проверьте запуск vLLM контейнеров и конфигурацию.")
        
        if summary["available_models"] == 0:
            print("   🚨 Ни одна модель недоступна!")
            print("   🔧 Запустите модели: python launch_working_models.py")

def main():
    """Основная функция"""
    tester = VLLMAPITester()
    
    print("🔍 Подготовка к тестированию vLLM API...")
    print(f"📁 Тестовое изображение: {tester.test_image_path}")
    print(f"🎯 Модели для тестирования: {list(tester.vllm_endpoints.keys())}")
    
    # Запуск тестов
    results = tester.run_all_tests()
    
    # Очистка
    if Path(tester.test_image_path).exists():
        Path(tester.test_image_path).unlink()
        print(f"🧹 Тестовое изображение удалено")
    
    print(f"\n🎯 vLLM API ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    
    # Возврат кода выхода
    summary = results["summary"]
    if summary["working_models"] >= summary["total_models"] * 0.5:
        return 0  # Успех
    else:
        return 1  # Проблемы

if __name__ == "__main__":
    import sys
    sys.exit(main())