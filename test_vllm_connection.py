#!/usr/bin/env python3
"""
Простой тест подключения к vLLM серверу
"""

import requests
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import io

def create_simple_test_image():
    """Создаем простое тестовое изображение."""
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 30), "Hello World!", fill='black', font=font)
    draw.text((20, 60), "Test Document", fill='black', font=font)
    
    return img

def test_vllm_direct():
    """Прямой тест vLLM API."""
    print("🧪 ПРЯМОЙ ТЕСТ vLLM API")
    print("=" * 40)
    
    # Проверяем здоровье сервера
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Сервер здоров: {response.status_code}")
    except Exception as e:
        print(f"❌ Сервер недоступен: {e}")
        return False
    
    # Получаем список моделей
    try:
        response = requests.get("http://localhost:8000/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"📋 Доступные модели: {[m['id'] for m in models.get('data', [])]}")
        else:
            print(f"❌ Ошибка получения моделей: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса моделей: {e}")
    
    # Создаем тестовое изображение
    test_image = create_simple_test_image()
    test_image.save("test_vllm_connection.png")
    
    # Конвертируем в base64
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Тестируем разные промпты
    test_prompts = [
        "Extract all text from this image.",
        "What do you see in this image?",
        "Read the text in this image."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 Тест {i}: {prompt}")
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/v1/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ Успех: {content}")
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"Ответ: {response.text}")
                
        except Exception as e:
            print(f"❌ Исключение: {e}")
    
    return True

if __name__ == "__main__":
    test_vllm_direct()