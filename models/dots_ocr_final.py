"""
ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ РЕАЛИЗАЦИЯ dots.ocr

Основано на глубоком изучении официальной документации и примеров.
Ключевые исправления:
1. Правильная обработка изображений (14x14 patches)
2. Корректные промпты для разных задач
3. Правильная обработка результатов
4. Устранение проблем с генерацией
"""

import os
import json
import torch
from typing import Any, Dict, List, Optional, Union
from PIL import Image
import traceback

from models.base_model import BaseModel
from utils.logger import logger


class DotsOCRFinalModel(BaseModel):
    """Финальная исправленная реализация dots.ocr."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
        self.max_new_tokens = config.get('max_new_tokens', 2048)  # Уменьшено для стабильности
        
        # Отключаем параллелизм токенизатора
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Официальные промпты из документации dots.ocr
        self.prompts = {
            # Простое извлечение текста
            "text_extraction": "Extract all text from this image.",
            
            # OCR с сохранением порядка чтения
            "ocr_reading_order": "Please extract all text content from this image while maintaining the original reading order.",
            
            # Структурированное извлечение (упрощенная версия)
            "structured_simple": "Extract the text content from this document image. Focus on the main text elements.",
            
            # Для таблиц
            "table_extraction": "Extract the table content from this image and format it as plain text.",
            
            # Минимальный промпт
            "minimal": "What text do you see?"
        }
    
    def load_model(self) -> None:
        """Загружаем модель с оптимизированными настройками."""
        try:
            logger.info(f"Loading dots.ocr from {self.model_path}")
            
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Базовые параметры загрузки
            load_kwargs = self._get_load_kwargs()
            
            # Оптимизированные параметры для dots.ocr
            load_kwargs.update({
                'torch_dtype': torch.float16,  # Используем float16 вместо bfloat16
                'trust_remote_code': True,
                'attn_implementation': "eager",  # Безопасный режим
                'low_cpu_mem_usage': True,
                'use_safetensors': True
            })
            
            # Загружаем модель
            logger.info("Loading model weights...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **load_kwargs
            )
            
            # Загружаем процессор
            logger.info("Loading processor...")
            self.processor = AutoProcessor.from_pretrained(
                self.model_path, 
                trust_remote_code=True,
                use_fast=False  # Используем медленный процессор для стабильности
            )
            
            # Устанавливаем модель в режим eval
            self.model.eval()
            
            # Проверяем токенизатор
            if hasattr(self.processor, 'tokenizer'):
                if self.processor.tokenizer.pad_token is None:
                    self.processor.tokenizer.pad_token = self.processor.tokenizer.eos_token
                    logger.info("Set pad_token to eos_token")
            
            logger.info("dots.ocr loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load dots.ocr: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Предобработка изображения для dots.ocr."""
        try:
            # Конвертируем в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Оптимальный размер для dots.ocr (на основе документации)
            # dots.ocr работает с патчами 14x14, оптимальные размеры кратны 14
            max_size = 1400  # 100 * 14
            
            # Изменяем размер если изображение слишком большое
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                # Делаем размеры кратными 14
                new_size = (
                    ((new_size[0] + 13) // 14) * 14,
                    ((new_size[1] + 13) // 14) * 14
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {new_size}")
            
            return image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def _safe_generate(self, inputs: Dict, prompt_type: str = "simple") -> str:
        """Безопасная генерация с обработкой ошибок."""
        try:
            # Параметры генерации оптимизированные для dots.ocr
            generation_kwargs = {
                'max_new_tokens': min(self.max_new_tokens, 1024),  # Ограничиваем для стабильности
                'do_sample': False,  # Детерминированная генерация
                'temperature': 0.1,
                'pad_token_id': self.processor.tokenizer.eos_token_id,
                'eos_token_id': self.processor.tokenizer.eos_token_id,
                'use_cache': True,
                'output_attentions': False,
                'output_hidden_states': False
            }
            
            # Для простых промптов используем меньше токенов
            if prompt_type in ["minimal", "text_extraction"]:
                generation_kwargs['max_new_tokens'] = 256
            
            # Генерируем ответ
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    **generation_kwargs
                )
            
            # Декодируем результат
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, 
                skip_special_tokens=True, 
                clean_up_tokenization_spaces=True
            )[0]
            
            return output_text.strip()
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def _create_messages(self, image: Image.Image, prompt: str) -> List[Dict]:
        """Создаем сообщения в правильном формате для dots.ocr."""
        return [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    
    def _process_with_prompt(self, image: Image.Image, prompt: str, prompt_type: str = "simple") -> str:
        """Обрабатываем изображение с заданным промптом."""
        try:
            # Предобрабатываем изображение
            processed_image = self._preprocess_image(image)
            
            # Создаем сообщения
            messages = self._create_messages(processed_image, prompt)
            
            # Применяем шаблон чата
            text = self.processor.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
            
            # Обрабатываем визуальную информацию
            try:
                from qwen_vl_utils import process_vision_info
                image_inputs, video_inputs = process_vision_info(messages)
            except ImportError:
                logger.warning("qwen_vl_utils не найден, используем прямую обработку")
                image_inputs = [processed_image]
                video_inputs = None
            
            # Подготавливаем входные данные
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            
            # Перемещаем на устройство
            device = next(self.model.parameters()).device
            inputs = inputs.to(device)
            
            # Генерируем ответ
            output_text = self._safe_generate(inputs, prompt_type)
            
            return output_text
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"[Processing error: {e}]"
    
    def process_image(self, image: Image.Image, prompt: Optional[str] = None, 
                     mode: str = "text_extraction") -> str:
        """Основной метод обработки изображения."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Выбираем промпт
            if prompt is None:
                prompt = self.prompts.get(mode, self.prompts["text_extraction"])
            
            logger.info(f"Processing with mode: {mode}")
            
            # Валидируем изображение
            if image is None:
                raise ValueError("Image is None")
            
            # Обрабатываем изображение
            result = self._process_with_prompt(image, prompt, mode)
            
            # Проверяем результат
            if not result or result.strip() == "":
                logger.warning("Empty result, trying alternative prompt")
                # Пробуем минимальный промпт
                result = self._process_with_prompt(image, self.prompts["minimal"], "minimal")
            
            logger.info("Processing completed successfully")
            
            return result if result else "[dots.ocr: No text detected]"
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return f"[dots.ocr error: {e}]"
    
    def extract_text(self, image: Image.Image) -> str:
        """Извлекаем только текст."""
        return self.process_image(image, mode="text_extraction")
    
    def chat(self, image: Image.Image, prompt: str, **kwargs) -> str:
        """Чат с моделью."""
        return self.process_image(image, prompt=prompt, mode="custom")
    
    def extract_table(self, image: Image.Image) -> str:
        """Извлекаем содержимое таблицы."""
        return self.process_image(image, mode="table_extraction")
    
    def parse_document(self, image: Image.Image) -> Dict[str, Any]:
        """Парсим документ (упрощенная версия)."""
        try:
            # Используем структурированное извлечение
            result = self.process_image(image, mode="structured_simple")
            
            return {
                "success": True,
                "text": result,
                "method": "simplified_parsing"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": f"Error: {e}"
            }
    
    def unload(self) -> None:
        """Выгружаем модель."""
        try:
            if self.model is not None:
                del self.model
                self.model = None
            if self.processor is not None:
                del self.processor
                self.processor = None
            
            # Безопасная очистка CUDA кеша
            if torch.cuda.is_available():
                try:
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                except Exception as e:
                    logger.warning(f"Warning during CUDA cleanup: {e}")
            
            logger.info("dots.ocr unloaded successfully")
            
        except Exception as e:
            logger.warning(f"Warning during model unload: {e}")