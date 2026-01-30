#!/usr/bin/env python3
"""
Удобный клиент для работы с dots.ocr через vLLM
"""

import requests
import base64
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

class DotsOCRClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.model_name = "rednote-hilab/dots.ocr"
    
    def health_check(self) -> bool:
        """Проверка доступности сервера"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_models(self) -> Dict[str, Any]:
        """Получение списка доступных моделей"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def process_image(self, image_path: str, prompt: str = "Extract all text from this image", 
                     max_tokens: int = 1000) -> Dict[str, Any]:
        """Обработка изображения через OCR"""
        
        # Проверка файла
        if not Path(image_path).exists():
            return {"success": False, "error": f"Файл не найден: {image_path}"}
        
        try:
            # Кодирование изображения
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Определение MIME типа
            ext = Path(image_path).suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg', 
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            # Формирование запроса
            payload = {
                "model": self.model_name,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
                    ]
                }],
                "max_tokens": max_tokens,
                "temperature": 0.1
            }
            
            # Отправка запроса
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "text": result["choices"][0]["message"]["content"],
                    "model": self.model_name,
                    "usage": result.get("usage", {}),
                    "image_path": image_path
                }
            else:
                return {
                    "success": False, 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def process_text(self, text: str, max_tokens: int = 500) -> Dict[str, Any]:
        """Обработка текстового запроса"""
        try:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": text}],
                "max_tokens": max_tokens,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "text": result["choices"][0]["message"]["content"],
                    "model": self.model_name,
                    "usage": result.get("usage", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(description="Клиент для dots.ocr через vLLM")
    parser.add_argument("--url", default="http://localhost:8000", help="URL сервера")
    parser.add_argument("--image", help="Путь к изображению для OCR")
    parser.add_argument("--text", help="Текстовый запрос")
    parser.add_argument("--prompt", default="Extract all text from this image", 
                       help="Промпт для OCR")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Максимум токенов")
    parser.add_argument("--health", action="store_true", help="Проверка здоровья сервера")
    parser.add_argument("--models", action="store_true", help="Список моделей")
    parser.add_argument("--output", help="Файл для сохранения результата")
    
    args = parser.parse_args()
    
    # Создание клиента
    client = DotsOCRClient(args.url)
    
    # Проверка здоровья
    if args.health:
        if client.health_check():
            print("✅ Сервер доступен")
        else:
            print("❌ Сервер недоступен")
        return
    
    # Список моделей
    if args.models:
        models = client.get_models()
        if "error" in models:
            print(f"❌ Ошибка: {models['error']}")
        else:
            print("📊 Доступные модели:")
            for model in models.get("data", []):
                print(f"   • {model.get('id', 'unknown')}")
        return
    
    # Обработка изображения
    if args.image:
        print(f"🔄 Обработка изображения: {args.image}")
        result = client.process_image(args.image, args.prompt, args.max_tokens)
        
        if result["success"]:
            print(f"✅ OCR результат:")
            print(f"📝 {result['text']}")
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 Результат сохранен в: {args.output}")
        else:
            print(f"❌ Ошибка: {result['error']}")
        return
    
    # Обработка текста
    if args.text:
        print(f"🔄 Обработка текста: {args.text}")
        result = client.process_text(args.text, args.max_tokens)
        
        if result["success"]:
            print(f"✅ Результат:")
            print(f"📝 {result['text']}")
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 Результат сохранен в: {args.output}")
        else:
            print(f"❌ Ошибка: {result['error']}")
        return
    
    # Интерактивный режим
    print("🚀 DOTS.OCR КЛИЕНТ")
    print("=" * 25)
    
    if not client.health_check():
        print("❌ Сервер недоступен на", args.url)
        print("💡 Убедитесь, что контейнер запущен: docker ps | findstr dots-ocr")
        return
    
    print("✅ Сервер доступен")
    
    # Показать доступные модели
    models = client.get_models()
    if "error" not in models:
        print(f"📊 Доступные модели: {len(models.get('data', []))}")
    
    print("\n💡 Примеры использования:")
    print("   python dots_ocr_client.py --image image.png")
    print("   python dots_ocr_client.py --text 'Привет, как дела?'")
    print("   python dots_ocr_client.py --health")
    print("   python dots_ocr_client.py --models")

if __name__ == "__main__":
    main()