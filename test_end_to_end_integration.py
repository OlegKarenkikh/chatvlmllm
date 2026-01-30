#!/usr/bin/env python3
"""
Комплексное end-to-end тестирование интеграции интерфейса и API
"""

import requests
import time
import json
import os
import subprocess
import threading
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from typing import Dict, List, Any, Optional

class EndToEndTester:
    def __init__(self):
        self.api_url = "http://localhost:8001"
        self.streamlit_url = "http://localhost:8501"
        self.test_images_dir = Path("test_documents")
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
        
        # Создание тестовых изображений если их нет
        self.ensure_test_images()
    
    def ensure_test_images(self):
        """Создание тестовых изображений для тестирования"""
        self.test_images_dir.mkdir(exist_ok=True)
        
        # Создание простого текстового документа
        simple_text_path = self.test_images_dir / "simple_text.png"
        if not simple_text_path.exists():
            self.create_simple_text_image(simple_text_path)
        
        # Создание документа с таблицей
        table_path = self.test_images_dir / "table_document.png"
        if not table_path.exists():
            self.create_table_image(table_path)
        
        # Создание многоязычного документа
        multilingual_path = self.test_images_dir / "multilingual.png"
        if not multilingual_path.exists():
            self.create_multilingual_image(multilingual_path)
    
    def create_simple_text_image(self, path: Path):
        """Создание простого текстового изображения"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = """ТЕСТОВЫЙ ДОКУМЕНТ
        
Это простой текстовый документ для тестирования OCR.
Содержит кириллический и латинский текст.

Номер документа: 1234567890
Дата: 24.01.2026
Статус: АКТИВЕН

Test text in English for multilingual testing.
Numbers: 123, 456.78, 999
Special chars: @#$%^&*()"""
        
        draw.multiline_text((50, 50), text, fill='black', font=font, spacing=10)
        img.save(path)
        print(f"✅ Создано тестовое изображение: {path}")
    
    def create_table_image(self, path: Path):
        """Создание изображения с таблицей"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            font_bold = ImageFont.truetype("arialbd.ttf", 20)
        except:
            font = font_bold = ImageFont.load_default()
        
        # Заголовок
        draw.text((50, 30), "ТАБЛИЦА ДАННЫХ", fill='black', font=font_bold)
        
        # Таблица
        table_data = [
            ["№", "Название", "Количество", "Цена"],
            ["1", "Товар А", "10", "100.00"],
            ["2", "Товар Б", "5", "250.50"],
            ["3", "Товар В", "15", "75.25"],
            ["", "ИТОГО:", "30", "425.75"]
        ]
        
        y = 80
        for row in table_data:
            x = 50
            for cell in row:
                draw.text((x, y), cell, fill='black', font=font)
                x += 150
            y += 30
            
            # Линия под заголовком
            if y == 110:
                draw.line([(50, y-5), (650, y-5)], fill='black', width=2)
        
        img.save(path)
        print(f"✅ Создано изображение таблицы: {path}")
    
    def create_multilingual_image(self, path: Path):
        """Создание многоязычного документа"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        text = """МНОГОЯЗЫЧНЫЙ ДОКУМЕНТ / MULTILINGUAL DOCUMENT

Русский текст: Привет, мир!
English text: Hello, world!
Français: Bonjour le monde!
Deutsch: Hallo Welt!
Español: ¡Hola mundo!

Цифры и даты:
- Дата: 24.01.2026
- Время: 15:30:45
- Номер: +7 (999) 123-45-67
- Email: test@example.com
- URL: https://example.com

Специальные символы: ©®™€$¥£"""
        
        draw.multiline_text((50, 50), text, fill='black', font=font, spacing=8)
        img.save(path)
        print(f"✅ Создано многоязычное изображение: {path}")
    
    def run_test(self, test_name: str, test_func):
        """Запуск отдельного теста с обработкой ошибок"""
        print(f"\n🧪 Тест: {test_name}")
        print("-" * 50)
        
        self.results["summary"]["total"] += 1
        
        try:
            start_time = time.time()
            result = test_func()
            duration = time.time() - start_time
            
            self.results["tests"][test_name] = {
                "status": "PASSED" if result else "FAILED",
                "duration": round(duration, 2),
                "details": result if isinstance(result, dict) else {"success": result}
            }
            
            if result:
                print(f"✅ ПРОШЕЛ за {duration:.2f}с")
                self.results["summary"]["passed"] += 1
            else:
                print(f"❌ НЕ ПРОШЕЛ за {duration:.2f}с")
                self.results["summary"]["failed"] += 1
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            print(f"💥 ОШИБКА: {error_msg}")
            
            self.results["tests"][test_name] = {
                "status": "ERROR",
                "duration": round(duration, 2),
                "error": error_msg
            }
            
            self.results["summary"]["failed"] += 1
            self.results["summary"]["errors"].append(f"{test_name}: {error_msg}")
    
    def test_api_health(self) -> bool:
        """Тест здоровья API"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   API статус: {data.get('status', 'unknown')}")
                print(f"   GPU доступен: {data.get('gpu_available', False)}")
                print(f"   Загружено моделей: {data.get('models_loaded', 0)}")
                return data.get('status') == 'healthy'
            return False
        except Exception as e:
            print(f"   Ошибка подключения к API: {e}")
            return False
    
    def test_api_models_list(self) -> bool:
        """Тест получения списка моделей"""
        try:
            response = requests.get(f"{self.api_url}/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                available = data.get('available', [])
                loaded = data.get('loaded', [])
                
                print(f"   Доступно моделей: {len(available)}")
                print(f"   Загружено моделей: {len(loaded)}")
                
                # Проверка структуры данных
                if available and isinstance(available[0], dict):
                    required_fields = ['id', 'name', 'params']
                    first_model = available[0]
                    has_required = all(field in first_model for field in required_fields)
                    print(f"   Структура данных корректна: {has_required}")
                    return has_required
                
                return len(available) > 0
            return False
        except Exception as e:
            print(f"   Ошибка получения списка моделей: {e}")
            return False
    
    def test_api_ocr_simple(self) -> Dict[str, Any]:
        """Тест простого OCR через API"""
        try:
            image_path = self.test_images_dir / "simple_text.png"
            
            with open(image_path, 'rb') as f:
                files = {'file': ('simple_text.png', f, 'image/png')}
                data = {'model': 'qwen3_vl_2b'}
                
                response = requests.post(
                    f"{self.api_url}/ocr",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '')
                processing_time = result.get('processing_time', 0)
                
                print(f"   Время обработки: {processing_time:.2f}с")
                print(f"   Длина текста: {len(text)} символов")
                print(f"   Модель: {result.get('model', 'unknown')}")
                
                # Проверка качества OCR
                expected_words = ['ТЕСТОВЫЙ', 'ДОКУМЕНТ', '1234567890', '24.01.2026']
                found_words = sum(1 for word in expected_words if word in text)
                accuracy = found_words / len(expected_words)
                
                print(f"   Точность: {accuracy:.1%} ({found_words}/{len(expected_words)} слов)")
                
                return {
                    "success": True,
                    "text_length": len(text),
                    "processing_time": processing_time,
                    "accuracy": accuracy,
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                }
            else:
                print(f"   HTTP ошибка: {response.status_code}")
                print(f"   Ответ: {response.text[:200]}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   Ошибка OCR теста: {e}")
            return {"success": False, "error": str(e)}
    
    def test_api_chat(self) -> Dict[str, Any]:
        """Тест чата через API"""
        try:
            image_path = self.test_images_dir / "simple_text.png"
            
            with open(image_path, 'rb') as f:
                files = {'file': ('simple_text.png', f, 'image/png')}
                data = {
                    'prompt': 'Опишите содержимое этого документа кратко',
                    'model': 'qwen3_vl_2b',
                    'temperature': 0.7,
                    'max_tokens': 200
                }
                
                response = requests.post(
                    f"{self.api_url}/chat",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                processing_time = result.get('processing_time', 0)
                
                print(f"   Время обработки: {processing_time:.2f}с")
                print(f"   Длина ответа: {len(response_text)} символов")
                print(f"   Ответ: {response_text[:150]}...")
                
                # Проверка качества ответа
                quality_indicators = ['документ', 'текст', 'содержит', 'номер']
                quality_score = sum(1 for indicator in quality_indicators 
                                  if indicator.lower() in response_text.lower())
                quality = quality_score / len(quality_indicators)
                
                print(f"   Качество ответа: {quality:.1%}")
                
                return {
                    "success": True,
                    "response_length": len(response_text),
                    "processing_time": processing_time,
                    "quality": quality,
                    "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                }
            else:
                print(f"   HTTP ошибка: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   Ошибка чат теста: {e}")
            return {"success": False, "error": str(e)}
    
    def test_api_batch_ocr(self) -> Dict[str, Any]:
        """Тест пакетной обработки OCR"""
        try:
            files_data = []
            
            # Подготовка нескольких файлов
            test_files = ['simple_text.png', 'table_document.png', 'multilingual.png']
            
            for filename in test_files:
                file_path = self.test_images_dir / filename
                if file_path.exists():
                    files_data.append(('files', (filename, open(file_path, 'rb'), 'image/png')))
            
            if not files_data:
                return {"success": False, "error": "No test files available"}
            
            data = {'model': 'qwen3_vl_2b'}
            
            response = requests.post(
                f"{self.api_url}/batch/ocr",
                files=files_data,
                data=data,
                timeout=120
            )
            
            # Закрытие файлов
            for _, (_, file_obj, _) in files_data:
                file_obj.close()
            
            if response.status_code == 200:
                result = response.json()
                total = result.get('total', 0)
                successful = result.get('successful', 0)
                failed = result.get('failed', 0)
                results = result.get('results', [])
                
                print(f"   Всего файлов: {total}")
                print(f"   Успешно: {successful}")
                print(f"   Неудачно: {failed}")
                
                # Анализ результатов
                avg_time = 0
                if results:
                    processing_times = [r.get('processing_time', 0) for r in results if r.get('status') == 'success']
                    if processing_times:
                        avg_time = sum(processing_times) / len(processing_times)
                
                print(f"   Среднее время: {avg_time:.2f}с")
                
                return {
                    "success": successful > 0,
                    "total": total,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": successful / total if total > 0 else 0,
                    "avg_processing_time": avg_time
                }
            else:
                print(f"   HTTP ошибка: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   Ошибка пакетного теста: {e}")
            return {"success": False, "error": str(e)}
    
    def test_streamlit_accessibility(self) -> bool:
        """Тест доступности Streamlit интерфейса"""
        try:
            response = requests.get(self.streamlit_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Проверка ключевых элементов интерфейса
                checks = {
                    "title": "ChatVLMLLM" in content,
                    "navigation": "Навигация" in content or "Navigation" in content,
                    "ocr_mode": "OCR" in content,
                    "chat_mode": "чат" in content or "chat" in content,
                    "file_upload": "file_uploader" in content or "загрузить" in content.lower()
                }
                
                passed_checks = sum(checks.values())
                total_checks = len(checks)
                
                print(f"   Проверок пройдено: {passed_checks}/{total_checks}")
                for check, result in checks.items():
                    print(f"   {check}: {'✅' if result else '❌'}")
                
                return passed_checks >= total_checks * 0.8  # 80% успешности
            else:
                print(f"   HTTP ошибка: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   Ошибка доступности Streamlit: {e}")
            return False
    
    def test_model_loading_integration(self) -> Dict[str, Any]:
        """Тест интеграции загрузки моделей"""
        try:
            from models.model_loader import ModelLoader
            
            # Тест загрузки модели
            test_model = 'qwen3_vl_2b'
            
            print(f"   Загрузка модели: {test_model}")
            start_time = time.time()
            
            model = ModelLoader.load_model(test_model)
            load_time = time.time() - start_time
            
            print(f"   Время загрузки: {load_time:.2f}с")
            
            # Проверка методов модели
            has_chat = hasattr(model, 'chat')
            has_extract = hasattr(model, 'extract_text')
            has_process = hasattr(model, 'process_image')
            
            print(f"   Методы модели:")
            print(f"     chat: {'✅' if has_chat else '❌'}")
            print(f"     extract_text: {'✅' if has_extract else '❌'}")
            print(f"     process_image: {'✅' if has_process else '❌'}")
            
            # Тест простой обработки
            test_image_path = self.test_images_dir / "simple_text.png"
            if test_image_path.exists():
                from PIL import Image
                image = Image.open(test_image_path)
                
                start_time = time.time()
                if has_extract:
                    result = model.extract_text(image)
                elif has_chat:
                    result = model.chat(image, "Extract text from this image")
                elif has_process:
                    result = model.process_image(image)
                else:
                    result = "No suitable method found"
                
                process_time = time.time() - start_time
                
                print(f"   Время обработки: {process_time:.2f}с")
                print(f"   Результат: {len(str(result))} символов")
                
                return {
                    "success": True,
                    "load_time": load_time,
                    "process_time": process_time,
                    "has_methods": has_chat or has_extract or has_process,
                    "result_length": len(str(result))
                }
            else:
                return {
                    "success": True,
                    "load_time": load_time,
                    "has_methods": has_chat or has_extract or has_process,
                    "note": "No test image for processing"
                }
                
        except Exception as e:
            print(f"   Ошибка интеграции модели: {e}")
            return {"success": False, "error": str(e)}
    
    def test_vllm_integration(self) -> Dict[str, Any]:
        """Тест интеграции с vLLM моделями"""
        try:
            # Проверка доступности vLLM моделей
            vllm_models = [
                ("dots.ocr", "http://localhost:8000"),
                ("Qwen3-VL-2B", "http://localhost:8010"),
                ("Qwen2-VL-2B", "http://localhost:8011")
            ]
            
            working_models = []
            
            for model_name, url in vllm_models:
                try:
                    health_response = requests.get(f"{url}/health", timeout=5)
                    if health_response.status_code == 200:
                        working_models.append(model_name)
                        print(f"   ✅ {model_name}: Доступна на {url}")
                        
                        # Тест простого запроса
                        test_payload = {
                            "model": model_name,
                            "messages": [{"role": "user", "content": "Hello"}],
                            "max_tokens": 50
                        }
                        
                        chat_response = requests.post(
                            f"{url}/v1/chat/completions",
                            json=test_payload,
                            timeout=30
                        )
                        
                        if chat_response.status_code == 200:
                            result = chat_response.json()
                            response_text = result["choices"][0]["message"]["content"]
                            print(f"     Ответ: {response_text[:50]}...")
                        else:
                            print(f"     Ошибка чата: {chat_response.status_code}")
                    else:
                        print(f"   ❌ {model_name}: Недоступна на {url}")
                except Exception as e:
                    print(f"   ❌ {model_name}: Ошибка подключения - {e}")
            
            return {
                "success": len(working_models) > 0,
                "working_models": working_models,
                "total_tested": len(vllm_models),
                "success_rate": len(working_models) / len(vllm_models)
            }
            
        except Exception as e:
            print(f"   Ошибка vLLM интеграции: {e}")
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 ЗАПУСК КОМПЛЕКСНОГО END-TO-END ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        # Список всех тестов
        tests = [
            ("API Health Check", self.test_api_health),
            ("API Models List", self.test_api_models_list),
            ("API OCR Simple", self.test_api_ocr_simple),
            ("API Chat", self.test_api_chat),
            ("API Batch OCR", self.test_api_batch_ocr),
            ("Streamlit Accessibility", self.test_streamlit_accessibility),
            ("Model Loading Integration", self.test_model_loading_integration),
            ("vLLM Integration", self.test_vllm_integration)
        ]
        
        # Запуск тестов
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Финальный отчет
        self.generate_final_report()
    
    def generate_final_report(self):
        """Генерация финального отчета"""
        print(f"\n🏆 ФИНАЛЬНЫЙ ОТЧЕТ")
        print("=" * 40)
        
        summary = self.results["summary"]
        print(f"📊 Всего тестов: {summary['total']}")
        print(f"✅ Прошло: {summary['passed']}")
        print(f"❌ Не прошло: {summary['failed']}")
        
        if summary['total'] > 0:
            success_rate = (summary['passed'] / summary['total']) * 100
            print(f"📈 Успешность: {success_rate:.1f}%")
        
        # Детали по тестам
        print(f"\n📋 ДЕТАЛИ ТЕСТОВ:")
        for test_name, result in self.results["tests"].items():
            status_icon = {"PASSED": "✅", "FAILED": "❌", "ERROR": "💥"}
            icon = status_icon.get(result["status"], "❓")
            duration = result["duration"]
            print(f"   {icon} {test_name}: {result['status']} ({duration}с)")
        
        # Ошибки
        if summary['errors']:
            print(f"\n🚨 ОШИБКИ:")
            for error in summary['errors']:
                print(f"   • {error}")
        
        # Сохранение отчета
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = f"end_to_end_test_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Отчет сохранен: {report_file}")
        
        # Рекомендации
        self.generate_recommendations()
    
    def generate_recommendations(self):
        """Генерация рекомендаций на основе результатов"""
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        
        summary = self.results["summary"]
        
        if summary['passed'] == summary['total']:
            print("   🎉 Все тесты прошли успешно! Система готова к продакшену.")
        elif summary['passed'] / summary['total'] >= 0.8:
            print("   ✅ Большинство тестов прошло. Система в основном готова.")
            print("   🔧 Рекомендуется исправить оставшиеся проблемы.")
        elif summary['passed'] / summary['total'] >= 0.5:
            print("   ⚠️ Половина тестов прошла. Требуется дополнительная работа.")
            print("   🛠️ Сосредоточьтесь на критических компонентах.")
        else:
            print("   🚨 Много проблем обнаружено. Система не готова.")
            print("   🔨 Требуется серьезная отладка и исправления.")
        
        # Специфические рекомендации
        failed_tests = [name for name, result in self.results["tests"].items() 
                       if result["status"] != "PASSED"]
        
        if "API Health Check" in failed_tests:
            print("   🔧 Запустите API сервер: uvicorn api:app --host 0.0.0.0 --port 8001")
        
        if "Streamlit Accessibility" in failed_tests:
            print("   🔧 Запустите Streamlit: streamlit run app.py")
        
        if "Model Loading Integration" in failed_tests:
            print("   🔧 Проверьте установку моделей и зависимостей")
        
        if "vLLM Integration" in failed_tests:
            print("   🔧 Запустите vLLM модели: python launch_working_models.py")

def main():
    """Основная функция"""
    tester = EndToEndTester()
    
    print("🔍 Подготовка к тестированию...")
    print(f"📁 Тестовые изображения: {tester.test_images_dir}")
    print(f"🌐 API URL: {tester.api_url}")
    print(f"🖥️ Streamlit URL: {tester.streamlit_url}")
    
    # Запуск всех тестов
    tester.run_all_tests()
    
    print(f"\n🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    main()