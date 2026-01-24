# РЕШЕНИЕ ИНТЕГРАЦИИ DOTS.OCR В CHATVLMLLM

## 🎯 ПРОБЛЕМА И РЕШЕНИЕ

### Основные проблемы:
1. **Flash Attention несовместимость** с RTX 5070 Ti Blackwell (sm_120)
2. **Версии зависимостей** - dots.ocr требует точные версии
3. **Неправильная обработка изображений** - проблемы с chat template
4. **CUDA 13.0 совместимость** - новая архитектура требует адаптации

### ✅ ГОТОВОЕ РЕШЕНИЕ:

## 1. ПРАВИЛЬНАЯ УСТАНОВКА ЗАВИСИМОСТЕЙ

```bash
# Шаг 1: Установка правильной версии PyTorch для Blackwell
pip uninstall torch torchvision torchaudio -y
pip install torch==2.7.0 torchvision==0.22.0 torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu126

# Шаг 2: НЕ устанавливаем flash-attn (несовместим с Blackwell)
# Используем eager attention вместо flash attention

# Шаг 3: Установка qwen_vl_utils (правильная версия)
pip install qwen-vl-utils==0.0.8

# Шаг 4: Установка dots.ocr
pip install git+https://github.com/ucaslcl/GOT-OCR2.0.git
```

## 2. ИНТЕГРАЦИЯ В CHATVLMLLM

### Вариант A: Добавление в существующую архитектуру

```python
# В models/dots_ocr_chatvlm_integration.py
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from qwen_vl_utils import process_vision_info
from PIL import Image
import logging

class DotsOCRChatVLM:
    """dots.ocr интеграция для chatvlmllm проекта"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_name = "rednote-hilab/dots.ocr"
        
    def load_model(self):
        """Загрузка с Blackwell оптимизациями"""
        try:
            # Blackwell оптимизации
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            torch.backends.cudnn.benchmark = True
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.bfloat16,  # Оптимально для Blackwell
                attn_implementation="eager",  # ОБЯЗАТЕЛЬНО для RTX 5070 Ti
                device_map="auto",
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Ошибка загрузки dots.ocr: {e}")
            return False
    
    def chat_completion(self, messages, max_tokens=2048):
        """Совместимость с OpenAI API для chatvlmllm"""
        try:
            # Извлечение изображения и текста из messages
            image_content = None
            text_content = "Extract all text from this image"
            
            for message in messages:
                if message.get("role") == "user":
                    content = message.get("content", [])
                    for item in content:
                        if item.get("type") == "image_url":
                            image_url = item.get("image_url", {}).get("url")
                            if image_url:
                                image_content = Image.open(image_url).convert('RGB')
                        elif item.get("type") == "text":
                            text_content = item.get("text", text_content)
            
            if not image_content:
                return {"error": "No image provided"}
            
            # Обработка через dots.ocr
            result = self.process_image(image_content, text_content)
            
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result or "No text detected"
                    }
                }]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def process_image(self, image, prompt):
        """Основная обработка изображения"""
        if not self.model or not self.processor:
            return None
            
        try:
            # Правильный формат для dots.ocr
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }]
            
            # Применение chat template
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Обработка vision info
            image_inputs, video_inputs = process_vision_info(messages)
            
            # Подготовка входных данных
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            ).to("cuda")
            
            # Генерация с оптимизированными параметрами
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=False,
                    temperature=0.0,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Декодирование
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            return output_text.strip()
            
        except Exception as e:
            logging.error(f"Ошибка обработки: {e}")
            return None
```

### Вариант B: Через vLLM сервер (РЕКОМЕНДУЕТСЯ)

```python
# В api.py или app.py
from openai import OpenAI
import subprocess
import time

class DotsOCRvLLMIntegration:
    """Интеграция dots.ocr через vLLM сервер"""
    
    def __init__(self, port=8000):
        self.port = port
        self.client = None
        self.server_process = None
        
    def start_vllm_server(self):
        """Запуск vLLM сервера для dots.ocr"""
        try:
            cmd = [
                "vllm", "serve", "rednote-hilab/dots.ocr",
                "--trust-remote-code",
                "--gpu-memory-utilization", "0.9",
                "--port", str(self.port),
                "--dtype", "bfloat16",
                "--disable-log-requests"
            ]
            
            self.server_process = subprocess.Popen(cmd)
            
            # Ждем запуска сервера
            time.sleep(30)
            
            # Создаем клиента
            self.client = OpenAI(
                base_url=f"http://localhost:{self.port}/v1",
                api_key="token-abc123"
            )
            
            return True
            
        except Exception as e:
            print(f"Ошибка запуска vLLM: {e}")
            return False
    
    def chat_completion(self, messages, max_tokens=2048):
        """OpenAI совместимый API"""
        if not self.client:
            return {"error": "vLLM server not started"}
            
        try:
            response = self.client.chat.completions.create(
                model="rednote-hilab/dots.ocr",
                messages=messages,
                max_tokens=max_tokens
            )
            
            return response.model_dump()
            
        except Exception as e:
            return {"error": str(e)}
    
    def stop_server(self):
        """Остановка vLLM сервера"""
        if self.server_process:
            self.server_process.terminate()
```

## 3. ДОБАВЛЕНИЕ В КОНФИГУРАЦИЮ CHATVLMLLM

```yaml
# В config.yaml или config_final.yaml
models:
  dots_ocr_vllm:
    name: "dots.ocr via vLLM"
    type: "vllm_server"
    model_path: "rednote-hilab/dots.ocr"
    port: 8000
    status: "production"
    
  dots_ocr_direct:
    name: "dots.ocr Direct"
    type: "transformers"
    model_path: "rednote-hilab/dots.ocr"
    precision: "bf16"
    attn_implementation: "eager"
    status: "experimental"
```

## 4. ИСПОЛЬЗОВАНИЕ В CHATVLMLLM

```python
# В app.py или main файле
from models.dots_ocr_chatvlm_integration import DotsOCRChatVLM

# Инициализация
dots_ocr = DotsOCRChatVLM()
if dots_ocr.load_model():
    print("✅ dots.ocr готова к использованию")

# Использование в API endpoint
@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    messages = request.json.get('messages', [])
    result = dots_ocr.chat_completion(messages)
    return jsonify(result)
```

## 5. ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ

```python
# test_dots_ocr_integration.py
def test_chatvlm_integration():
    """Тест интеграции с chatvlmllm"""
    
    # Тестовые данные в формате chatvlmllm
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "test_document.png"}
                },
                {
                    "type": "text", 
                    "text": "Extract all text from this document"
                }
            ]
        }
    ]
    
    # Тест через прямую интеграцию
    dots_ocr = DotsOCRChatVLM()
    if dots_ocr.load_model():
        result = dots_ocr.chat_completion(messages)
        print(f"Результат: {result}")
    
    # Тест через vLLM
    vllm_integration = DotsOCRvLLMIntegration()
    if vllm_integration.start_vllm_server():
        result = vllm_integration.chat_completion(messages)
        print(f"vLLM результат: {result}")
```

## 6. РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ

### Для продакшена:
1. **Используйте vLLM вариант** - более стабильный и быстрый
2. **Fallback на qwen_vl_2b** - если dots.ocr недоступен
3. **Мониторинг памяти** - dots.ocr требует ~19GB VRAM

### Для разработки:
1. **Прямая интеграция** - для отладки и экспериментов
2. **Логирование** - подробные логи для диагностики
3. **Graceful degradation** - обработка ошибок

## 7. АЛЬТЕРНАТИВНЫЕ РЕШЕНИЯ

Если dots.ocr продолжает вызывать проблемы:

```python
# Используйте проверенные модели из вашего проекта
FALLBACK_MODELS = {
    "primary": "qwen_vl_2b",      # Быстро и качественно
    "advanced": "qwen3_vl_2b",    # Продвинутые возможности  
    "specialized": "got_ocr_hf"   # Специализированная OCR
}
```

## 🎉 ЗАКЛЮЧЕНИЕ

Теперь у вас есть три варианта интеграции dots.ocr:

1. **vLLM сервер** (рекомендуется) - стабильно и быстро
2. **Прямая интеграция** - полный контроль
3. **Fallback система** - надежность через альтернативы

Выберите подходящий вариант в зависимости от ваших потребностей!