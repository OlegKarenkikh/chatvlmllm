#!/usr/bin/env python3
"""
Быстрая проверка здоровья всех vLLM серверов
"""

import requests
import time
import json
from datetime import datetime

def check_server_health(port, model_name):
    """Проверка здоровья одного сервера"""
    try:
        # Проверка health endpoint
        health_url = f"http://localhost:{port}/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {model_name} (порт {port}): Сервер здоров")
            
            # Дополнительная проверка models endpoint
            try:
                models_url = f"http://localhost:{port}/v1/models"
                models_response = requests.get(models_url, timeout=5)
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    print(f"   📊 Доступные модели: {len(models_data.get('data', []))}")
                    for model in models_data.get('data', []):
                        print(f"      • {model.get('id', 'unknown')}")
                else:
                    print(f"   ⚠️ Models endpoint недоступен: {models_response.status_code}")
            except Exception as e:
                print(f"   ⚠️ Ошибка проверки models: {e}")
            
            return True
        else:
            print(f"❌ {model_name} (порт {port}): HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {model_name} (порт {port}): Соединение отклонено")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {model_name} (порт {port}): Таймаут")
        return False
    except Exception as e:
        print(f"❌ {model_name} (порт {port}): Ошибка - {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🔍 ПРОВЕРКА ЗДОРОВЬЯ VLLM СЕРВЕРОВ")
    print("=" * 50)
    print(f"Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Конфигурация серверов
    servers = [
        (8000, "dots.ocr", "rednote-hilab/dots.ocr"),
        (8001, "GOT-OCR2_0", "stepfun-ai/GOT-OCR2_0"),
        (8002, "Qwen3-VL-2B", "Qwen/Qwen3-VL-2B-Instruct"),
        (8003, "Phi3.5-Vision", "microsoft/Phi-3.5-vision-instruct")
    ]
    
    healthy_servers = []
    unhealthy_servers = []
    
    for port, name, model_path in servers:
        print(f"🔄 Проверяем {name}...")
        if check_server_health(port, name):
            healthy_servers.append((port, name, model_path))
        else:
            unhealthy_servers.append((port, name, model_path))
        print()
    
    # Сводка
    print("📊 СВОДКА ПРОВЕРКИ")
    print("=" * 30)
    print(f"✅ Здоровые серверы: {len(healthy_servers)}")
    print(f"❌ Проблемные серверы: {len(unhealthy_servers)}")
    print()
    
    if healthy_servers:
        print("🟢 РАБОТАЮЩИЕ СЕРВЕРЫ:")
        for port, name, model_path in healthy_servers:
            print(f"   • {name}: http://localhost:{port}")
        print()
    
    if unhealthy_servers:
        print("🔴 ПРОБЛЕМНЫЕ СЕРВЕРЫ:")
        for port, name, model_path in unhealthy_servers:
            print(f"   • {name}: http://localhost:{port}")
        print()
        
        print("💡 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
        print("   1. Проверьте логи контейнеров: docker logs <container_name>")
        print("   2. Перезапустите проблемные контейнеры: docker restart <container_name>")
        print("   3. Проверьте использование GPU: nvidia-smi")
        print("   4. Убедитесь, что модели загружены в кеш HuggingFace")
    
    # Тест простого запроса к работающему серверу
    if healthy_servers:
        print("🧪 ТЕСТ ПРОСТОГО ЗАПРОСА")
        print("=" * 30)
        
        # Берем первый здоровый сервер
        port, name, model_path = healthy_servers[0]
        
        try:
            # Создаем простое тестовое изображение
            from PIL import Image, ImageDraw, ImageFont
            import base64
            import io
            
            # Создаем изображение с текстом
            img = Image.new('RGB', (300, 100), color='white')
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((10, 30), "TEST OCR", fill='black', font=font)
            
            # Конвертируем в base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Отправляем запрос
            payload = {
                "model": model_path,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract text from this image"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }],
                "max_tokens": 100
            }
            
            print(f"🔄 Отправляем тестовый запрос к {name}...")
            response = requests.post(
                f"http://localhost:{port}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ Ответ получен: {content}")
                print(f"🎉 Сервер {name} полностью функционален!")
            else:
                print(f"❌ Ошибка запроса: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
    
    print("\n✅ Проверка завершена!")

if __name__ == "__main__":
    main()