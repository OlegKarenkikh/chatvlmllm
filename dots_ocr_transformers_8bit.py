#!/usr/bin/env python3
"""
Альтернативное решение: dots.ocr через transformers с 8-bit квантизацией
Для GPU с ограниченной памятью (< 8GB свободно)
"""

import torch
import base64
import io
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
import requests
from flask import Flask, request, jsonify
import threading
import time

class DotsOCRTransformers:
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
        
    def load_model(self):
        """Загрузка модели с 8-bit квантизацией"""
        print("🔄 Загрузка dots.ocr с 8-bit квантизацией...")
        
        try:
            # Проверка доступной GPU памяти
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                free_memory = (torch.cuda.get_device_properties(0).total_memory - 
                             torch.cuda.memory_allocated(0)) / 1024**3
                print(f"📊 GPU: {gpu_memory:.1f}GB всего, {free_memory:.1f}GB свободно")
            
            # Загрузка процессора
            print("📝 Загрузка процессора...")
            self.processor = AutoProcessor.from_pretrained(
                "rednote-hilab/dots.ocr",
                trust_remote_code=True
            )
            
            # Загрузка модели с оптимизациями
            print("🧠 Загрузка модели с 8-bit квантизацией...")
            self.model = AutoModelForCausalLM.from_pretrained(
                "rednote-hilab/dots.ocr",
                torch_dtype=torch.bfloat16,
                device_map="auto",
                load_in_8bit=True,  # 8-bit квантизация для экономии памяти
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                max_memory={0: "6GB"}  # Ограничение памяти GPU
            )
            
            print("✅ Модель загружена успешно!")
            self.model_loaded = True
            
            # Проверка использования памяти
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated(0) / 1024**3
                print(f"💾 Использовано GPU памяти: {allocated:.2f}GB")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            return False
    
    def process_image(self, image_path_or_base64, prompt="Extract all text from this image"):
        """Обработка изображения"""
        if not self.model_loaded:
            return {"error": "Модель не загружена"}
        
        try:
            # Загрузка изображения
            if image_path_or_base64.startswith('data:image'):
                # Base64 изображение
                image_data = image_path_or_base64.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                # Путь к файлу
                image = Image.open(image_path_or_base64)
            
            # Конвертация в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            print(f"🖼️ Обработка изображения {image.size}")
            
            # Подготовка входных данных
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": image}
                    ]
                }
            ]
            
            # Применение шаблона чата
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Обработка изображения и текста
            image_inputs, video_inputs = self.processor.process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            
            # Перенос на устройство
            inputs = inputs.to(self.device)
            
            print("🔄 Генерация ответа...")
            
            # Генерация с оптимизированными параметрами
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,  # Ограничение для экономии памяти
                    do_sample=False,
                    temperature=0.1,
                    pad_token_id=self.processor.tokenizer.eos_token_id,
                    use_cache=True
                )
            
            # Декодирование результата
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            print("✅ Обработка завершена")
            
            return {
                "success": True,
                "text": output_text.strip(),
                "model": "rednote-hilab/dots.ocr",
                "method": "transformers_8bit"
            }
            
        except Exception as e:
            print(f"❌ Ошибка обработки: {e}")
            return {"error": str(e)}

# Flask API сервер
app = Flask(__name__)
ocr_model = DotsOCRTransformers()

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy" if ocr_model.model_loaded else "loading",
        "model_loaded": ocr_model.model_loaded
    })

@app.route('/v1/models')
def models():
    return jsonify({
        "data": [{
            "id": "rednote-hilab/dots.ocr",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "transformers_8bit"
        }]
    })

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        # Извлечение изображения и текста из сообщения
        user_message = messages[-1]
        content = user_message.get('content', [])
        
        text_prompt = "Extract all text from this image"
        image_data = None
        
        for item in content:
            if item.get('type') == 'text':
                text_prompt = item.get('text', text_prompt)
            elif item.get('type') == 'image_url':
                image_data = item.get('image_url', {}).get('url')
        
        if not image_data:
            return jsonify({"error": "No image provided"}), 400
        
        # Обработка изображения
        result = ocr_model.process_image(image_data, text_prompt)
        
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
        
        # Формат ответа OpenAI API
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "rednote-hilab/dots.ocr",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["text"]
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 100,  # Примерное значение
                "completion_tokens": len(result["text"].split()),
                "total_tokens": 100 + len(result["text"].split())
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def load_model_background():
    """Загрузка модели в фоновом режиме"""
    ocr_model.load_model()

def main():
    """Основная функция"""
    print("🚀 ЗАПУСК DOTS.OCR ЧЕРЕЗ TRANSFORMERS (8-BIT)")
    print("=" * 55)
    
    # Проверка CUDA
    if torch.cuda.is_available():
        print(f"✅ CUDA доступна: {torch.cuda.get_device_name(0)}")
        print(f"📊 GPU память: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    else:
        print("⚠️ CUDA недоступна, будет использоваться CPU (медленно)")
    
    # Запуск загрузки модели в фоне
    print("🔄 Запуск загрузки модели в фоновом режиме...")
    model_thread = threading.Thread(target=load_model_background)
    model_thread.daemon = True
    model_thread.start()
    
    # Запуск Flask сервера
    print("🌐 Запуск API сервера на порту 8000...")
    print("📡 API будет доступно на: http://localhost:8000")
    print("📋 Endpoints:")
    print("   • Health: http://localhost:8000/health")
    print("   • Models: http://localhost:8000/v1/models")
    print("   • Chat: http://localhost:8000/v1/chat/completions")
    
    app.run(host='0.0.0.0', port=8000, debug=False)

if __name__ == "__main__":
    main()