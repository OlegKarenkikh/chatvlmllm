#!/usr/bin/env python3
"""
Пример использования dots.ocr в API chatvlmllm проекта
"""

from flask import Flask, request, jsonify
import logging
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.dots_ocr_chatvlm_integration import get_dots_ocr_instance, initialize_dots_ocr

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Глобальная переменная для отслеживания состояния модели
dots_ocr_ready = False

@app.before_first_request
def initialize_model():
    """Инициализация модели при первом запросе"""
    global dots_ocr_ready
    
    logger.info("🚀 Инициализация dots.ocr для chatvlmllm API...")
    
    if initialize_dots_ocr():
        dots_ocr_ready = True
        logger.info("✅ dots.ocr готова к использованию")
    else:
        logger.error("❌ Не удалось инициализировать dots.ocr")

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния API"""
    return jsonify({
        "status": "healthy" if dots_ocr_ready else "initializing",
        "dots_ocr_ready": dots_ocr_ready,
        "message": "dots.ocr API for chatvlmllm"
    })

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """
    OpenAI совместимый endpoint для OCR
    Совместим с chatvlmllm архитектурой
    """
    if not dots_ocr_ready:
        return jsonify({
            "error": "dots.ocr not ready",
            "message": "Model is still initializing"
        }), 503
    
    try:
        # Получение данных запроса
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        # Извлечение параметров
        messages = data.get('messages', [])
        max_tokens = data.get('max_tokens', 2048)
        model = data.get('model', 'dots.ocr')
        
        if not messages:
            return jsonify({
                "error": "No messages provided"
            }), 400
        
        # Получение экземпляра модели
        dots_ocr = get_dots_ocr_instance()
        
        # Обработка через dots.ocr
        result = dots_ocr.chat_completion(messages, max_tokens)
        
        # Добавление метаданных
        result['model'] = model
        result['object'] = 'chat.completion'
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Ошибка в chat_completions: {e}")
        return jsonify({
            "error": str(e),
            "message": "Internal server error"
        }), 500

@app.route('/v1/ocr', methods=['POST'])
def ocr_endpoint():
    """
    Специализированный OCR endpoint
    Упрощенный интерфейс для быстрого OCR
    """
    if not dots_ocr_ready:
        return jsonify({
            "error": "dots.ocr not ready"
        }), 503
    
    try:
        data = request.get_json()
        
        # Поддержка разных форматов входных данных
        if 'image_url' in data:
            # Простой формат
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": data['image_url']}
                    },
                    {
                        "type": "text",
                        "text": data.get('prompt', 'Extract all text from this image')
                    }
                ]
            }]
        elif 'messages' in data:
            # Полный формат
            messages = data['messages']
        else:
            return jsonify({
                "error": "No image_url or messages provided"
            }), 400
        
        # Обработка
        dots_ocr = get_dots_ocr_instance()
        result = dots_ocr.chat_completion(messages, data.get('max_tokens', 1024))
        
        # Упрощенный ответ для OCR
        if 'error' not in result:
            extracted_text = result['choices'][0]['message']['content']
            return jsonify({
                "success": True,
                "extracted_text": extracted_text,
                "processing_info": result.get('usage', {})
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"Ошибка в OCR endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/v1/models', methods=['GET'])
def list_models():
    """Список доступных моделей"""
    return jsonify({
        "object": "list",
        "data": [
            {
                "id": "dots.ocr",
                "object": "model",
                "created": 1640995200,
                "owned_by": "rednote-hilab",
                "ready": dots_ocr_ready
            }
        ]
    })

# Пример клиента для тестирования
def test_api_client():
    """Тестовый клиент для проверки API"""
    import requests
    import json
    
    base_url = "http://localhost:5000"
    
    # Тест 1: Проверка здоровья
    print("🧪 Тест 1: Health Check")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Тест 2: OCR endpoint
    print("🧪 Тест 2: OCR Endpoint")
    ocr_data = {
        "image_url": "test_chatvlm_document.png",
        "prompt": "Extract all text from this document"
    }
    
    response = requests.post(
        f"{base_url}/v1/ocr",
        json=ocr_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Text: {result['extracted_text'][:100]}...")
    else:
        print(f"Error: {response.text}")
    print()
    
    # Тест 3: Chat Completions (OpenAI формат)
    print("🧪 Тест 3: Chat Completions")
    chat_data = {
        "model": "dots.ocr",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": "test_chatvlm_document.png"}
                    },
                    {
                        "type": "text",
                        "text": "Please extract all visible text"
                    }
                ]
            }
        ],
        "max_tokens": 1024
    }
    
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=chat_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            content = result['choices'][0]['message']['content']
            print(f"Content: {content[:100]}...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='dots.ocr API для chatvlmllm')
    parser.add_argument('--test', action='store_true', help='Запустить тестовый клиент')
    parser.add_argument('--port', type=int, default=5000, help='Порт для API')
    parser.add_argument('--host', default='localhost', help='Хост для API')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Запуск тестового клиента...")
        test_api_client()
    else:
        print("🚀 Запуск dots.ocr API для chatvlmllm...")
        print(f"📡 API будет доступно на: http://{args.host}:{args.port}")
        print("📋 Endpoints:")
        print("   GET  /health - проверка состояния")
        print("   GET  /v1/models - список моделей")
        print("   POST /v1/ocr - простой OCR")
        print("   POST /v1/chat/completions - OpenAI совместимый")
        
        app.run(host=args.host, port=args.port, debug=False)