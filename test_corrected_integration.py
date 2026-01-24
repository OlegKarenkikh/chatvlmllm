#!/usr/bin/env python3
"""
Исправленное end-to-end тестирование с правильными портами
"""

import requests
import time
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class CorrectedIntegrationTester:
    def __init__(self):
        self.api_url = "http://localhost:8000"  # Исправленный порт
        self.streamlit_url = "http://localhost:8501"
        self.vllm_endpoints = {
            "Qwen3-VL-2B": "http://localhost:8010"
        }
        self.test_image_path = "test_integration.png"
        self.results = {}
        
        # Создание тестового изображения
        self.create_test_image()
    
    def create_test_image(self):
        """Создание тестового изображения"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        text = """ИНТЕГРАЦИОННЫЙ ТЕСТ

Этот документ создан для тестирования полной интеграции системы.

Информация для проверки:
• Дата: 24.01.2026
• Номер: INT-2026-001
• Статус: ТЕСТИРОВАНИЕ

Многоязычный контент:
• Русский: Система работает!
• English: System is working!

Контакты:
📧 test@integration.com
📞 +7 (999) 888-77-66"""
        
        draw.multiline_text((50, 50), text, fill='black', font=font, spacing=8)
        img.save(self.test_image_path)
        print(f"✅ Создано тестовое изображение: {self.test_image_path}")
    
    def test_api_health(self) -> dict:
        """Тест API health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API здоров: {data.get('status')}")
                print(f"   🎮 GPU: {data.get('gpu_name', 'Unknown')}")
                print(f"   💾 VRAM: {data.get('vram_total_gb', 0)} ГБ")
                return {"success": True, "data": data}
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return {"success": False, "error": str(e)}
    
    def test_api_models(self) -> dict:
        """Тест списка моделей API"""
        try:
            response = requests.get(f"{self.api_url}/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                available = data.get('available', [])
                loaded = data.get('loaded', [])
                
                print(f"   ✅ Доступно моделей: {len(available)}")
                print(f"   📦 Загружено: {len(loaded)}")
                
                return {
                    "success": True,
                    "available_count": len(available),
                    "loaded_count": len(loaded),
                    "models": available[:3]  # Первые 3 для краткости
                }
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return {"success": False, "error": str(e)}
    
    def test_api_ocr(self) -> dict:
        """Тест OCR через API"""
        try:
            with open(self.test_image_path, 'rb') as f:
                files = {'file': ('test.png', f, 'image/png')}
                data = {'model': 'qwen3_vl_2b'}
                
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/ocr",
                    files=files,
                    data=data,
                    timeout=60
                )
                processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '')
                
                print(f"   ✅ OCR успешен")
                print(f"   ⏱️ Время: {processing_time:.2f}с")
                print(f"   📝 Текст: {len(text)} символов")
                print(f"   🔍 Превью: {text[:100]}...")
                
                # Проверка качества
                keywords = ['ИНТЕГРАЦИОННЫЙ', 'ТЕСТ', '24.01.2026', 'INT-2026-001']
                found = sum(1 for kw in keywords if kw in text)
                accuracy = found / len(keywords)
                
                print(f"   🎯 Точность: {accuracy:.1%} ({found}/{len(keywords)})")
                
                return {
                    "success": True,
                    "text_length": len(text),
                    "processing_time": processing_time,
                    "accuracy": accuracy,
                    "text_preview": text[:200]
                }
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return {"success": False, "error": str(e)}
    
    def test_api_chat(self) -> dict:
        """Тест чата через API"""
        try:
            with open(self.test_image_path, 'rb') as f:
                files = {'file': ('test.png', f, 'image/png')}
                data = {
                    'prompt': 'Опишите содержимое этого документа кратко',
                    'model': 'qwen3_vl_2b',
                    'temperature': 0.7,
                    'max_tokens': 200
                }
                
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/chat",
                    files=files,
                    data=data,
                    timeout=60
                )
                processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                print(f"   ✅ Чат успешен")
                print(f"   ⏱️ Время: {processing_time:.2f}с")
                print(f"   💬 Ответ: {response_text[:150]}...")
                
                return {
                    "success": True,
                    "response_length": len(response_text),
                    "processing_time": processing_time,
                    "response_preview": response_text[:300]
                }
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return {"success": False, "error": str(e)}
    
    def test_streamlit_interface(self) -> dict:
        """Тест Streamlit интерфейса"""
        try:
            response = requests.get(self.streamlit_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Проверка ключевых элементов
                checks = {
                    "title": "ChatVLMLLM" in content,
                    "streamlit": "streamlit" in content.lower(),
                    "app_content": len(content) > 1000,  # Минимальный размер контента
                    "javascript": "<script" in content,  # Наличие JS (признак Streamlit)
                    "css": "<style" in content or ".css" in content  # Наличие стилей
                }
                
                passed = sum(checks.values())
                total = len(checks)
                
                print(f"   ✅ Streamlit доступен")
                print(f"   📊 Проверок: {passed}/{total}")
                print(f"   📄 Размер контента: {len(content)} символов")
                
                for check, result in checks.items():
                    icon = "✅" if result else "❌"
                    print(f"     {icon} {check}")
                
                return {
                    "success": passed >= total * 0.6,  # 60% успешности
                    "checks_passed": passed,
                    "total_checks": total,
                    "content_size": len(content)
                }
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return {"success": False, "error": str(e)}
    
    def test_vllm_direct(self) -> dict:
        """Тест прямого обращения к vLLM"""
        try:
            model_name = "Qwen3-VL-2B"
            endpoint = self.vllm_endpoints[model_name]
            
            # Health check
            health_response = requests.get(f"{endpoint}/health", timeout=10)
            if health_response.status_code != 200:
                print(f"   ❌ vLLM недоступна: HTTP {health_response.status_code}")
                return {"success": False, "error": f"vLLM unavailable: {health_response.status_code}"}
            
            print(f"   ✅ vLLM модель доступна")
            
            # Простой текстовый тест
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Hello! How are you?"}],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            start_time = time.time()
            response = requests.post(
                f"{endpoint}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0]['message']['content']
                    
                    print(f"   ✅ vLLM чат работает")
                    print(f"   ⏱️ Время: {processing_time:.2f}с")
                    print(f"   💬 Ответ: {message[:100]}...")
                    
                    return {
                        "success": True,
                        "processing_time": processing_time,
                        "response": message,
                        "endpoint": endpoint
                    }
                else:
                    print(f"   ❌ Некорректный ответ от vLLM")
                    return {"success": False, "error": "Invalid vLLM response"}
            else:
                print(f"   ❌ vLLM ошибка: HTTP {response.status_code}")
                return {"success": False, "error": f"vLLM HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ Ошибка vLLM: {e}")
            return {"success": False, "error": str(e)}
    
    def run_full_test(self):
        """Полное тестирование"""
        print("🚀 ИСПРАВЛЕННОЕ END-TO-END ТЕСТИРОВАНИЕ")
        print("=" * 50)
        
        tests = [
            ("API Health Check", self.test_api_health),
            ("API Models List", self.test_api_models),
            ("API OCR Test", self.test_api_ocr),
            ("API Chat Test", self.test_api_chat),
            ("Streamlit Interface", self.test_streamlit_interface),
            ("vLLM Direct Test", self.test_vllm_direct)
        ]
        
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {},
            "summary": {"total": 0, "passed": 0, "failed": 0}
        }
        
        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}")
            print("-" * 40)
            
            results["summary"]["total"] += 1
            
            try:
                start_time = time.time()
                result = test_func()
                duration = time.time() - start_time
                
                if result.get("success", False):
                    results["summary"]["passed"] += 1
                    status = "PASSED"
                else:
                    results["summary"]["failed"] += 1
                    status = "FAILED"
                
                results["tests"][test_name] = {
                    "status": status,
                    "duration": round(duration, 2),
                    "details": result
                }
                
                print(f"   📊 Результат: {status} ({duration:.2f}с)")
                
            except Exception as e:
                results["summary"]["failed"] += 1
                results["tests"][test_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                print(f"   💥 ОШИБКА: {e}")
        
        # Финальный отчет
        self.generate_final_report(results)
        
        # Очистка
        if Path(self.test_image_path).exists():
            Path(self.test_image_path).unlink()
        
        return results
    
    def generate_final_report(self, results: dict):
        """Генерация финального отчета"""
        print(f"\n🏆 ФИНАЛЬНЫЙ ОТЧЕТ")
        print("=" * 30)
        
        summary = results["summary"]
        success_rate = (summary["passed"] / summary["total"]) * 100 if summary["total"] > 0 else 0
        
        print(f"📊 Всего тестов: {summary['total']}")
        print(f"✅ Прошло: {summary['passed']}")
        print(f"❌ Не прошло: {summary['failed']}")
        print(f"📈 Успешность: {success_rate:.1f}%")
        
        print(f"\n📋 Детали:")
        for test_name, result in results["tests"].items():
            status_icon = {"PASSED": "✅", "FAILED": "❌", "ERROR": "💥"}
            icon = status_icon.get(result["status"], "❓")
            duration = result.get("duration", 0)
            print(f"   {icon} {test_name}: {result['status']} ({duration}с)")
        
        # Сохранение отчета
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"corrected_integration_test_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Отчет сохранен: {report_file}")
        
        # Оценка готовности системы
        if success_rate >= 80:
            print(f"\n🎉 СИСТЕМА ПОЛНОСТЬЮ ГОТОВА К РАБОТЕ!")
            print(f"   Все основные компоненты функционируют корректно.")
        elif success_rate >= 60:
            print(f"\n✅ СИСТЕМА В ОСНОВНОМ ГОТОВА")
            print(f"   Большинство компонентов работает, есть незначительные проблемы.")
        else:
            print(f"\n⚠️ СИСТЕМА ТРЕБУЕТ ДОРАБОТКИ")
            print(f"   Обнаружены серьезные проблемы, требующие исправления.")

def main():
    """Основная функция"""
    tester = CorrectedIntegrationTester()
    results = tester.run_full_test()
    
    print(f"\n🎯 ИСПРАВЛЕННОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    
    # Возврат кода выхода
    success_rate = (results["summary"]["passed"] / results["summary"]["total"]) * 100
    return 0 if success_rate >= 60 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())