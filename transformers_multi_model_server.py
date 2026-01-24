#!/usr/bin/env python3
"""
Многомодельный сервер на базе Transformers с 8-bit квантизацией
Поддерживает загрузку и переключение между моделями
"""

import torch
import base64
import io
import json
import time
import threading
from pathlib import Path
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
from flask import Flask, request, jsonify
import gc

class MultiModelTransformersServer:
    def __init__(self):
        self.models = {}  # Загруженные модели
        self.processors = {}  # Процессоры для моделей
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        # Конфигурация поддерживаемых моделей
        self.supported_models = {
            "rednote-hilab/dots.ocr": {
                "name": "DotsOCR",
                "type": "ocr",
                "memory_8bit_gb": 3.5,
                "max_memory_gb": 6.0,
                "default_prompt": "Extract all text from this image"
            },
            "stepfun-ai/GOT-OCR-2.0-hf": {
                "name": "GOT-OCR 2.0",
                "type": "ocr", 
                "memory_8bit_gb": 0.8,
                "max_memory_gb": 2.0,
                "default_prompt": "OCR:"
            },
            "Qwen/Qwen2-VL-2B-Instruct": {
                "name": "Qwen2-VL 2B",
                "type": "vlm",
                "memory_8bit_gb": 2.5,
                "max_memory_gb": 4.0,
                "default_prompt": "Describe what you see in this image"
            },
            "microsoft/Phi-3.5-vision-instruct": {
                "name": "Phi-3.5 Vision",
                "type": "vlm",
                "memory_8bit_gb": 4.5,
                "max_memory_gb": 8.0,
                "default_prompt": "What is in this image?"
            }
        }
        
        self.loading_status = {}  # Статус загрузки моделей
        
    def get_gpu_memory_info(self):
        """Получение информации о GPU памяти"""
        if not torch.cuda.is_available():
            return {"available": False}
        
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        cached = torch.cuda.memory_reserved(0) / 1024**3
        free = total - cached
        
        return {
            "available": True,
            "total_gb": total,
            "allocated_gb": allocated,
            "cached_gb": cached,
            "free_gb": free
        }
    
    def can_load_model(self, model_name):
        """Проверка возможности загрузки модели"""
        if model_name not in self.supported_models:
            return False, "Модель не поддерживается"
        
        model_config = self.supported_models[model_name]
        gpu_info = self.get_gpu_memory_info()
        
        if not gpu_info["available"]:
            return True, "CPU режим"  # Можно загрузить на CPU
        
        required_memory = model_config["memory_8bit_gb"]
        available_memory = gpu_info["free_gb"]
        
        if available_memory < required_memory:
            return False, f"Недостаточно GPU памяти: нужно {required_memory:.1f} GB, доступно {available_memory:.1f} GB"
        
        return True, f"Достаточно памяти: {available_memory:.1f} GB доступно"
    
    def load_model(self, model_name):
        """Загрузка модели с оптимизациями"""
        if model_name in self.models:
            return True, "Модель уже загружена"
        
        can_load, reason = self.can_load_model(model_name)
        if not can_load:
            return False, reason
        
        print(f"🔄 Загрузка модели {model_name}...")
        self.loading_status[model_name] = "loading"
        
        try:
            model_config = self.supported_models[model_name]
            
            # Загрузка процессора
            print(f"📝 Загрузка процессора для {model_config['name']}...")
            processor = AutoProcessor.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir=self.cache_dir
            )
            
            # Определение параметров загрузки модели
            gpu_info = self.get_gpu_memory_info()
            load_params = {
                "trust_remote_code": True,
                "cache_dir": self.cache_dir,
                "low_cpu_mem_usage": True
            }
            
            if gpu_info["available"] and gpu_info["free_gb"] >= model_config["memory_8bit_gb"]:
                # GPU загрузка с 8-bit квантизацией
                print(f"🎮 Загрузка на GPU с 8-bit квантизацией...")
                load_params.update({
                    "torch_dtype": torch.bfloat16,
                    "device_map": "auto",
                    "load_in_8bit": True,
                    "max_memory": {0: f"{model_config['max_memory_gb']}GB"}
                })
            else:
                # CPU загрузка
                print(f"💻 Загрузка на CPU...")
                load_params.update({
                    "torch_dtype": torch.float32,
                    "device_map": "cpu"
                })
            
            # Загрузка модели
            print(f"🧠 Загрузка модели {model_config['name']}...")
            model = AutoModelForCausalLM.from_pretrained(model_name, **load_params)
            
            # Сохранение в кеше
            self.models[model_name] = model
            self.processors[model_name] = processor
            self.loading_status[model_name] = "loaded"
            
            # Информация о памяти после загрузки
            if gpu_info["available"]:
                new_gpu_info = self.get_gpu_memory_info()
                memory_used = new_gpu_info["allocated_gb"] - gpu_info["allocated_gb"]
                print(f"💾 Использовано GPU памяти: {memory_used:.2f} GB")
            
            print(f"✅ Модель {model_config['name']} загружена успешно")
            return True, f"Модель {model_config['name']} загружена"
            
        except Exception as e:
            self.loading_status[model_name] = "error"
            error_msg = f"Ошибка загрузки {model_name}: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def unload_model(self, model_name):
        """Выгрузка модели из памяти"""
        if model_name not in self.models:
            return False, "Модель не загружена"
        
        try:
            print(f"🗑️ Выгрузка модели {model_name}...")
            
            # Удаление из памяти
            del self.models[model_name]
            del self.processors[model_name]
            
            if model_name in self.loading_status:
                del self.loading_status[model_name]
            
            # Очистка GPU кеша
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Принудительная сборка мусора
            gc.collect()
            
            print(f"✅ Модель {model_name} выгружена")
            return True, f"Модель {model_name} выгружена"
            
        except Exception as e:
            error_msg = f"Ошибка выгрузки {model_name}: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def process_image(self, model_name, image_data, prompt=None):
        """Обработка изображения указанной моделью"""
        if model_name not in self.models:
            return {"error": f"Модель {model_name} не загружена"}
        
        if not prompt:
            prompt = self.supported_models[model_name]["default_prompt"]
        
        try:
            # Загрузка изображения
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            print(f"🖼️ Обработка изображения {image.size} моделью {model_name}")
            
            model = self.models[model_name]
            processor = self.processors[model_name]
            
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
            text = processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Обработка изображения и текста
            image_inputs, video_inputs = processor.process_vision_info(messages)
            inputs = processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            
            # Перенос на устройство
            inputs = inputs.to(self.device)
            
            print("🔄 Генерация ответа...")
            start_time = time.time()
            
            # Генерация
            with torch.no_grad():
                generated_ids = model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    do_sample=False,
                    temperature=0.1,
                    pad_token_id=processor.tokenizer.eos_token_id,
                    use_cache=True
                )
            
            generation_time = time.time() - start_time
            
            # Декодирование результата
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=False
            )[0]
            
            print(f"✅ Обработка завершена за {generation_time:.1f} сек")
            
            return {
                "success": True,
                "text": output_text.strip(),
                "model": model_name,
                "generation_time": generation_time,
                "method": "transformers_8bit"
            }
            
        except Exception as e:
            error_msg = f"Ошибка обработки: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def get_loaded_models(self):
        """Получение списка загруженных моделей"""
        return [
            {
                "id": model_name,
                "name": self.supported_models[model_name]["name"],
                "type": self.supported_models[model_name]["type"],
                "status": "loaded"
            }
            for model_name in self.models.keys()
        ]
    
    def get_available_models(self):
        """Получение списка доступных моделей"""
        models = []
        for model_name, config in self.supported_models.items():
            can_load, reason = self.can_load_model(model_name)
            status = "loaded" if model_name in self.models else ("available" if can_load else "unavailable")
            
            models.append({
                "id": model_name,
                "name": config["name"],
                "type": config["type"],
                "memory_8bit_gb": config["memory_8bit_gb"],
                "status": status,
                "reason": reason if not can_load else None
            })
        
        return models

# Flask приложение
app = Flask(__name__)
server = MultiModelTransformersServer()

@app.route('/health')
def health():
    gpu_info = server.get_gpu_memory_info()
    return jsonify({
        "status": "healthy",
        "loaded_models": len(server.models),
        "gpu_available": gpu_info["available"],
        "gpu_memory": gpu_info if gpu_info["available"] else None
    })

@app.route('/v1/models')
def models():
    loaded_models = server.get_loaded_models()
    return jsonify({
        "data": [
            {
                "id": model["id"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "transformers_multi"
            }
            for model in loaded_models
        ]
    })

@app.route('/models/available')
def available_models():
    return jsonify({
        "models": server.get_available_models()
    })

@app.route('/models/load', methods=['POST'])
def load_model():
    data = request.json
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({"error": "Model name required"}), 400
    
    success, message = server.load_model(model_name)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"error": message}), 400

@app.route('/models/unload', methods=['POST'])
def unload_model():
    data = request.json
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({"error": "Model name required"}), 400
    
    success, message = server.unload_model(model_name)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"error": message}), 400

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        data = request.json
        model_name = data.get('model')
        messages = data.get('messages', [])
        
        if not model_name:
            return jsonify({"error": "Model name required"}), 400
        
        if not messages:
            return jsonify({"error": "Messages required"}), 400
        
        # Извлечение изображения и текста
        user_message = messages[-1]
        content = user_message.get('content', [])
        
        text_prompt = None
        image_data = None
        
        for item in content:
            if item.get('type') == 'text':
                text_prompt = item.get('text')
            elif item.get('type') == 'image_url':
                image_data = item.get('image_url', {}).get('url')
        
        if not image_data:
            return jsonify({"error": "Image required"}), 400
        
        # Обработка изображения
        result = server.process_image(model_name, image_data, text_prompt)
        
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
        
        # Формат ответа OpenAI API
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_name,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["text"]
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": len(result["text"].split()),
                "total_tokens": 100 + len(result["text"].split())
            },
            "generation_time": result.get("generation_time", 0)
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def main():
    """Основная функция"""
    print("🚀 МНОГОМОДЕЛЬНЫЙ TRANSFORMERS СЕРВЕР")
    print("=" * 45)
    
    # Информация о системе
    gpu_info = server.get_gpu_memory_info()
    if gpu_info["available"]:
        print(f"✅ GPU доступна: {gpu_info['total_gb']:.1f} GB")
        print(f"💾 Свободно: {gpu_info['free_gb']:.1f} GB")
    else:
        print("⚠️ GPU недоступна, будет использоваться CPU")
    
    print(f"📁 Кеш моделей: {server.cache_dir}")
    print(f"🤖 Поддерживаемых моделей: {len(server.supported_models)}")
    
    # Автозагрузка модели по умолчанию
    default_model = "rednote-hilab/dots.ocr"
    print(f"\n🔄 Автозагрузка модели по умолчанию: {default_model}")
    
    def load_default_model():
        success, message = server.load_model(default_model)
        if success:
            print(f"✅ {message}")
        else:
            print(f"⚠️ {message}")
    
    # Загрузка в фоновом режиме
    load_thread = threading.Thread(target=load_default_model)
    load_thread.daemon = True
    load_thread.start()
    
    # Запуск сервера
    print("\n🌐 Запуск API сервера...")
    print("📡 Endpoints:")
    print("   • Health: http://localhost:8000/health")
    print("   • Models: http://localhost:8000/v1/models")
    print("   • Available: http://localhost:8000/models/available")
    print("   • Load: POST http://localhost:8000/models/load")
    print("   • Unload: POST http://localhost:8000/models/unload")
    print("   • Chat: http://localhost:8000/v1/chat/completions")
    
    app.run(host='0.0.0.0', port=8000, debug=False)

if __name__ == "__main__":
    main()