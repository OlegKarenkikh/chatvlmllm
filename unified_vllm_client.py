#!/usr/bin/env python3
"""
Унифицированный клиент для всех моделей vLLM
"""

import requests
import base64
import json
from pathlib import Path
from typing import Dict, Any, Optional

class UnifiedVLLMClient:
    def __init__(self):
        self.models = {}
        self.load_model_configs()
    
    def load_model_configs(self):
        """Загрузка конфигураций моделей"""
        try:
            with open('vllm_models_config.json', 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            for model_name, config in configs.items():
                self.models[model_name] = {
                    'url': f"http://localhost:{config['port']}",
                    'category': config['category'],
                    'port': config['port']
                }
        except Exception as e:
            print(f"❌ Ошибка загрузки конфигураций: {e}")
    
    def check_model_health(self, model_name: str) -> bool:
        """Проверка доступности модели"""
        if model_name not in self.models:
            return False
        
        try:
            url = self.models[model_name]['url']
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Получение списка доступных моделей"""
        available = {}
        for model_name, config in self.models.items():
            if self.check_model_health(model_name):
                available[model_name] = config
        return available
    
    def process_image(self, model_name: str, image_path: str, 
                     prompt: str = "Extract all text from this image") -> Dict[str, Any]:
        """Обработка изображения"""
        if not self.check_model_health(model_name):
            return {"success": False, "error": f"Модель {model_name} недоступна"}
        
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            ext = Path(image_path).suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg', 
                '.jpeg': 'image/jpeg'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')
            
            payload = {
                "model": model_name,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
                    ]
                }],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            url = self.models[model_name]['url']
            response = requests.post(f"{url}/v1/chat/completions", json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "text": result["choices"][0]["message"]["content"],
                    "model": model_name,
                    "usage": result.get("usage", {})
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    client = UnifiedVLLMClient()
    
    print("🚀 УНИФИЦИРОВАННЫЙ КЛИЕНТ VLLM")
    print("=" * 35)
    
    available = client.get_available_models()
    if available:
        print("✅ Доступные модели:")
        for model_name, config in available.items():
            print(f"   • {model_name} (порт {config['port']}, {config['category']})")
    else:
        print("❌ Нет доступных моделей")

if __name__ == "__main__":
    main()
