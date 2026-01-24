#!/usr/bin/env python3
"""
Тест чата с vLLM через адаптер
"""

import requests
import base64
import time
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image_with_text():
    """Создание тестового изображения с текстом для чата"""
    img = Image.new('RGB', (500, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Добавляем разный контент для тестирования чата
    draw.text((20, 20), "ДОКУМЕНТ: Водительское удостоверение", fill='black', font=font)
    draw.text((20, 50), "ФИО: Иванов Иван Иванович", fill='black', font=font)
    draw.text((20, 80), "Дата рождения: 15.03.1985", fill='black', font=font)
    draw.text((20, 110), "Категории: B, C", fill='black', font=font)
    draw.text((20, 140), "Выдано: 10.01.2020", fill='black', font=font)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def test_vllm_chat_api():
    """Тест чата через vLLM API"""
    print("🧪 Тестирование чата с vLLM API...")
    
    # Создание тестового изображения
    image_base64 = create_test_image_with_text()
    print("✅ Тестовое изображение создано")
    
    # Различные типы вопросов для тестирования
    test_questions = [
        "Какое имя указано в документе?",
        "Когда родился человек?",
        "Какие категории водительских прав у него есть?",
        "Опиши что ты видишь на изображении",
        "Извлеки все данные из документа"
    ]
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Вопрос {i}: {question}")
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        try:
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                print(f"✅ Ответ получен за {processing_time:.1f}с")
                print(f"📄 Ответ: {content[:100]}...")
                
                results.append({
                    "question": question,
                    "answer": content,
                    "processing_time": processing_time,
                    "success": True
                })
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"❌ Ответ: {response.text}")
                results.append({
                    "question": question,
                    "error": f"HTTP {response.status_code}",
                    "success": False
                })
                
        except Exception as e:
            print(f"❌ Ошибка запроса: {e}")
            results.append({
                "question": question,
                "error": str(e),
                "success": False
            })
    
    return results

def test_vllm_adapter():
    """Тест через VLLMStreamlitAdapter"""
    print("\n🔧 Тестирование VLLMStreamlitAdapter...")
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        from PIL import Image
        import io
        
        # Создание адаптера
        adapter = VLLMStreamlitAdapter()
        
        # Создание изображения
        image_data = create_test_image_with_text()
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Тест чата
        test_prompts = [
            "Что написано в документе?",
            "Какая дата рождения указана?",
            "Опиши содержимое изображения"
        ]
        
        adapter_results = []
        
        for prompt in test_prompts:
            print(f"\n💬 Тест: {prompt}")
            
            result = adapter.chat_with_image(image, prompt)
            
            if result and result["success"]:
                print(f"✅ Успешно за {result['processing_time']:.1f}с")
                print(f"📄 Ответ: {result['text'][:100]}...")
                adapter_results.append({
                    "prompt": prompt,
                    "success": True,
                    "processing_time": result['processing_time']
                })
            else:
                print(f"❌ Ошибка адаптера")
                adapter_results.append({
                    "prompt": prompt,
                    "success": False
                })
        
        return adapter_results
        
    except Exception as e:
        print(f"❌ Ошибка VLLMStreamlitAdapter: {e}")
        return []

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ЧАТА С vLLM")
    print("=" * 40)
    
    # Проверка доступности vLLM сервера
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ vLLM сервер недоступен")
            return
        print("✅ vLLM сервер доступен")
    except Exception as e:
        print(f"❌ Не удается подключиться к vLLM: {e}")
        return
    
    # Тест прямого API
    api_results = test_vllm_chat_api()
    
    # Тест адаптера
    adapter_results = test_vllm_adapter()
    
    # Итоги
    print("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 30)
    
    # API результаты
    api_success = sum(1 for r in api_results if r.get("success", False))
    print(f"🌐 Прямой API: {api_success}/{len(api_results)} успешно")
    
    if api_success > 0:
        avg_time = sum(r.get("processing_time", 0) for r in api_results if r.get("success", False)) / api_success
        print(f"   ⏱️ Среднее время: {avg_time:.1f}с")
    
    # Адаптер результаты
    adapter_success = sum(1 for r in adapter_results if r.get("success", False))
    print(f"🔧 Адаптер: {adapter_success}/{len(adapter_results)} успешно")
    
    if adapter_success > 0:
        avg_time = sum(r.get("processing_time", 0) for r in adapter_results if r.get("success", False)) / adapter_success
        print(f"   ⏱️ Среднее время: {avg_time:.1f}с")
    
    # Общий результат
    total_success = api_success + adapter_success
    total_tests = len(api_results) + len(adapter_results)
    
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {total_success}/{total_tests} тестов прошли")
    
    if total_success == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ЧАТА ПРОШЛИ УСПЕШНО!")
        print("\n💡 Чат с vLLM готов к использованию:")
        print("   1. Откройте http://localhost:8501")
        print("   2. Выберите 'vLLM (Рекомендуется)' в режиме выполнения")
        print("   3. Перейдите в 'Режим чата'")
        print("   4. Загрузите изображение и задавайте вопросы")
    else:
        print("⚠️ Некоторые тесты не прошли")
        print("💡 Проверьте логи vLLM сервера: docker logs dots-ocr-fixed")

if __name__ == "__main__":
    main()