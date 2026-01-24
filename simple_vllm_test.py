#!/usr/bin/env python3
"""
Простой тест vLLM API
"""

import requests
import base64
import time
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image():
    """Создание тестового изображения"""
    img = Image.new('RGB', (400, 150), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "TEST OCR 2026", fill='black', font=font)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def main():
    print("Testing vLLM API...")
    
    # Health check
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Health check: {response.status_code}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Models check
    try:
        response = requests.get("http://localhost:8000/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"Available models: {len(models.get('data', []))}")
            for model in models.get('data', []):
                print(f"  - {model.get('id', 'unknown')}")
        else:
            print(f"Models check failed: {response.status_code}")
    except Exception as e:
        print(f"Models check error: {e}")
        return
    
    # OCR test
    try:
        image_base64 = create_test_image()
        print("Test image created")
        
        payload = {
            "model": "rednote-hilab/dots.ocr",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all text from this image"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            "max_tokens": 100,
            "temperature": 0.1
        }
        
        print("Sending OCR request...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            timeout=120
        )
        
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"OCR result: {content}")
            print(f"Processing time: {processing_time:.1f} seconds")
            print("SUCCESS: vLLM OCR is working!")
        else:
            print(f"OCR request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"OCR test error: {e}")

if __name__ == "__main__":
    main()