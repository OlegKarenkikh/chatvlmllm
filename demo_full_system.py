#!/usr/bin/env python3
"""
Демонстрация полной системы end-to-end
"""

import requests
import time
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64

class SystemDemo:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.streamlit_url = "http://localhost:8501"
        self.vllm_url = "http://localhost:8010"
        self.demo_image = "demo_system.png"
        
        # Создание демо изображения
        self.create_demo_image()
    
    def create_demo_image(self):
        """Создание демонстрационного изображения"""
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 18)
            font_title = ImageFont.truetype("arialbd.ttf", 22)
        except:
            font = font_title = ImageFont.load_default()
        
        # Заголовок
        draw.text((50, 30), "СИСТЕМА ГОТОВА К РАБОТЕ!", fill='black', font=font_title)
        
        # Демо контент
        content = """
🎉 ПОЛНАЯ ИНТЕГРАЦИЯ ЗАВЕРШЕНА

Эта система демонстрирует полную интеграцию:
• FastAPI Backend (порт 8000)
• Streamlit Interface (порт 8501)  
• vLLM Models (порт 8010)

Возможности системы:
✅ OCR извлечение текста
✅ Интерактивный чат с VLM
✅ Batch обработка документов
✅ REST API интеграция
✅ Многоязычная поддержка

Технические характеристики:
• GPU: RTX 5070 Ti (12.82 ГБ)
• Модели: Qwen3-VL-2B-Instruct
• Точность OCR: 85-95%
• Время обработки: 6-24 секунды

Контакты:
📧 demo@system-ready.com
📞 +7 (999) 000-11-22
🌐 https://system-demo.example.com

Статус: ГОТОВО К ПРОДАКШЕНУ! 🚀
        """
        
        draw.multiline_text((50, 80), content.strip(), fill='black', font=font, spacing=4)
        
        # Рамка
        draw.rectangle([(30, 20), (770, 580)], outline='green', width=3)
        
        img.save(self.demo_image)
        print(f"✅ Создано демо изображение: {self.demo_image}")
    
    def check_services(self):
        """Проверка всех сервисов"""
        print("🔍 ПРОВЕРКА СЕРВИСОВ")
        print("=" * 30)
        
        services = {
            "FastAPI": self.api_url + "/health",
            "Streamlit": self.streamlit_url,
            "vLLM": self.vllm_url + "/health"
        }
        
        results = {}
        
        for service, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service}: Работает")
                    results[service] = True
                else:
                    print(f"❌ {service}: HTTP {response.status_code}")
                    results[service] = False
            except Exception as e:
                print(f"❌ {service}: Недоступен ({e})")
                results[service] = False
        
        return results
    
    def demo_api_ocr(self):
        """Демонстрация OCR через API"""
        print(f"\n📄 ДЕМО: OCR ЧЕРЕЗ API")
        print("-" * 25)
        
        try:
            with open(self.demo_image, 'rb') as f:
                files = {'file': ('demo.png', f, 'image/png')}
                data = {'model': 'qwen3_vl_2b'}
                
                print("🚀 Отправка запроса...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.api_url}/ocr",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '')
                
                print(f"✅ OCR успешен за {duration:.2f}с")
                print(f"📝 Извлечено {len(text)} символов")
                print(f"🔍 Превью текста:")
                print(f"   {text[:200]}...")
                
                # Проверка ключевых слов
                keywords = ['СИСТЕМА', 'ГОТОВА', 'ИНТЕГРАЦИЯ', 'FastAPI', 'Streamlit', 'vLLM']
                found = sum(1 for kw in keywords if kw in text)
                print(f"🎯 Найдено ключевых слов: {found}/{len(keywords)}")
                
                return True
            else:
                print(f"❌ Ошибка OCR: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка OCR: {e}")
            return False
    
    def demo_api_chat(self):
        """Демонстрация чата через API"""
        print(f"\n💬 ДЕМО: ЧАТ ЧЕРЕЗ API")
        print("-" * 22)
        
        try:
            with open(self.demo_image, 'rb') as f:
                files = {'file': ('demo.png', f, 'image/png')}
                data = {
                    'prompt': 'Опишите статус этой системы и её готовность',
                    'model': 'qwen3_vl_2b',
                    'temperature': 0.7,
                    'max_tokens': 150
                }
                
                print("🚀 Отправка вопроса...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.api_url}/chat",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                print(f"✅ Чат успешен за {duration:.2f}с")
                print(f"🤖 Ответ модели:")
                print(f"   {response_text}")
                
                return True
            else:
                print(f"❌ Ошибка чата: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка чата: {e}")
            return False
    
    def demo_vllm_direct(self):
        """Демонстрация прямого обращения к vLLM"""
        print(f"\n🤖 ДЕМО: ПРЯМОЙ vLLM API")
        print("-" * 26)
        
        try:
            # Получение имени модели
            models_response = requests.get(f"{self.vllm_url}/v1/models", timeout=10)
            if models_response.status_code != 200:
                print(f"❌ Не удалось получить список моделей")
                return False
            
            models_data = models_response.json()
            model_name = models_data['data'][0]['id']
            print(f"🤖 Используем модель: {model_name}")
            
            # Кодирование изображения
            with open(self.demo_image, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Какой статус у этой системы? Ответьте кратко."
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
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print("🚀 Отправка запроса к vLLM...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.vllm_url}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                message = result['choices'][0]['message']['content']
                
                print(f"✅ vLLM ответил за {duration:.2f}с")
                print(f"🤖 Ответ:")
                print(f"   {message}")
                
                return True
            else:
                print(f"❌ Ошибка vLLM: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка vLLM: {e}")
            return False
    
    def demo_system_info(self):
        """Демонстрация информации о системе"""
        print(f"\n📊 ИНФОРМАЦИЯ О СИСТЕМЕ")
        print("-" * 28)
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                print(f"🎮 GPU: {data.get('gpu_name', 'Unknown')}")
                print(f"💾 VRAM: {data.get('vram_total_gb', 0)} ГБ")
                print(f"📦 Загружено моделей: {data.get('models_loaded', 0)}")
                print(f"🔄 Rate limit: {data.get('rate_limit_per_minute', 0)} req/min")
                
                return True
            else:
                print(f"❌ Не удалось получить информацию о системе")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка получения информации: {e}")
            return False
    
    def run_full_demo(self):
        """Полная демонстрация системы"""
        print("🎉 ДЕМОНСТРАЦИЯ ПОЛНОЙ СИСТЕМЫ")
        print("=" * 40)
        
        # Проверка сервисов
        services_status = self.check_services()
        
        # Информация о системе
        self.demo_system_info()
        
        # Демонстрация функций
        demos = []
        
        if services_status.get("FastAPI", False):
            demos.append(("OCR через API", self.demo_api_ocr))
            demos.append(("Чат через API", self.demo_api_chat))
        
        if services_status.get("vLLM", False):
            demos.append(("Прямой vLLM API", self.demo_vllm_direct))
        
        # Запуск демо
        successful_demos = 0
        
        for demo_name, demo_func in demos:
            try:
                if demo_func():
                    successful_demos += 1
            except Exception as e:
                print(f"❌ Ошибка в демо '{demo_name}': {e}")
        
        # Итоги
        print(f"\n🏆 ИТОГИ ДЕМОНСТРАЦИИ")
        print("=" * 25)
        
        total_services = len(services_status)
        working_services = sum(services_status.values())
        
        total_demos = len(demos)
        
        print(f"📊 Сервисы: {working_services}/{total_services} работают")
        print(f"🧪 Демо: {successful_demos}/{total_demos} успешно")
        
        overall_success = (working_services / total_services + successful_demos / total_demos) / 2 if total_demos > 0 else working_services / total_services
        
        print(f"📈 Общая успешность: {overall_success:.1%}")
        
        if overall_success >= 0.8:
            print(f"\n🎉 СИСТЕМА ПОЛНОСТЬЮ ГОТОВА К РАБОТЕ!")
            print(f"   Все основные компоненты функционируют отлично.")
        elif overall_success >= 0.6:
            print(f"\n✅ СИСТЕМА В ОСНОВНОМ ГОТОВА")
            print(f"   Большинство компонентов работает корректно.")
        else:
            print(f"\n⚠️ СИСТЕМА ТРЕБУЕТ ДОРАБОТКИ")
            print(f"   Обнаружены проблемы, требующие исправления.")
        
        # Ссылки для пользователя
        print(f"\n🌐 ДОСТУП К СИСТЕМЕ:")
        if services_status.get("Streamlit", False):
            print(f"   🖥️ Веб-интерфейс: {self.streamlit_url}")
        if services_status.get("FastAPI", False):
            print(f"   📚 API документация: {self.api_url}/docs")
        if services_status.get("vLLM", False):
            print(f"   🤖 vLLM API: {self.vllm_url}/docs")
        
        # Очистка
        if Path(self.demo_image).exists():
            Path(self.demo_image).unlink()
            print(f"\n🧹 Демо изображение удалено")
        
        return overall_success >= 0.6

def main():
    """Основная функция"""
    demo = SystemDemo()
    
    print("🚀 Запуск демонстрации системы...")
    print(f"📁 Демо изображение: {demo.demo_image}")
    
    success = demo.run_full_demo()
    
    print(f"\n🎯 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())