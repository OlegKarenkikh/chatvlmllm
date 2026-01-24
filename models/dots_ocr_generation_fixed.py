"""
ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ DOTS.OCR С УЛУЧШЕННОЙ ГЕНЕРАЦИЕЙ

Проблемы исправлены:
1. Dtype mismatch (BFloat16/Half)
2. Генерация повторяющихся символов
3. Неправильные параметры генерации
"""

import os
import json
import torch
from typing import Any, Dict, List, Optional, Union
from PIL import Image
import traceback

from models.base_model import BaseModel
from utils.logger import logger


class DotsOCRGenerationFixedModel(BaseModel):
    """Полностью исправленная dots.ocr с правильной генерацией."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
        self.max_new_tokens = config.get('max_new_tokens', 512)
        
        # Отключаем параллелизм токенизатора
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Оптимизированные промпты для dots.ocr
        self.prompts = {
            "text_extraction": "Extract all text from this image. Provide only the text content without any formatting or repetition.",
            "minimal": "What text is in this image?",
            "simple": "Read the text.",
            "ocr": "Perform OCR on this image."
        }
    
    def _fix_model_dtypes(self, model):
        """Исправляем dtype несоответствия в модели."""
        try:
            logger.info("🔧 Исправляем dtype несоответствия...")
            
            # Приводим все параметры к float16
            target_dtype = torch.float16
            converted_count = 0
            
            for name, param in model.named_parameters():
                if param.dtype != target_dtype:
                    logger.debug(f"Converting {name} from {param.dtype} to {target_dtype}")
                    param.data = param.data.to(target_dtype)
                    converted_count += 1
            
            # Исправляем буферы
            for name, buffer in model.named_buffers():
                if buffer.dtype not in [torch.int64, torch.int32, torch.bool] and buffer.dtype != target_dtype:
                    logger.debug(f"Converting buffer {name} from {buffer.dtype} to {target_dtype}")
                    buffer.data = buffer.data.to(target_dtype)
                    converted_count += 1
            
            logger.info(f"✅ Dtype исправления применены ({converted_count} конверсий)")
            return model
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось исправить dtype: {e}")
            return model
    
    def load_model(self) -> None:
        """Загружаем модель с исправлением всех проблем."""
        try:
            logger.info(f"Loading dots.ocr with full fixes from {self.model_path}")
            
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Базовые параметры загрузки
            load_kwargs = self._get_load_kwargs()
            
            # Принудительно используем float16 для всего
            load_kwargs.update({
                'torch_dtype': torch.float16,
                'trust_remote_code': True,
                'attn_implementation': "eager",
                'low_cpu_mem_usage': True,
                'use_safetensors': True
            })
            
            # Загружаем модель
            logger.info("Loading model weights...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **load_kwargs
            )
            
            # КРИТИЧЕСКИ ВАЖНО: Исправляем dtype несоответствия
            self.model = self._fix_model_dtypes(self.model)
            
            # Загружаем процессор с исправлением video_processor проблемы
            logger.info("Loading processor...")
            try:
                # Сначала пробуем стандартную загрузку
                self.processor = AutoProcessor.from_pretrained(
                    self.model_path, 
                    trust_remote_code=True,
                    use_fast=False
                )
            except TypeError as e:
                if "video_processor" in str(e):
                    logger.warning("video_processor error detected, using manual processor loading...")
                    # Загружаем компоненты процессора вручную
                    from transformers import AutoImageProcessor, AutoTokenizer
                    
                    # Загружаем компоненты отдельно
                    image_processor = AutoImageProcessor.from_pretrained(
                        self.model_path, 
                        trust_remote_code=True
                    )
                    tokenizer = AutoTokenizer.from_pretrained(
                        self.model_path, 
                        trust_remote_code=True,
                        use_fast=False
                    )
                    
                    # Создаем процессор вручную с пустым video_processor
                    try:
                        # Импортируем класс процессора dots.ocr
                        from transformers.models.auto.processing_auto import AutoProcessor
                        processor_class = AutoProcessor._get_processor_class_from_config(
                            self.model_path, trust_remote_code=True
                        )
                        
                        # Создаем процессор с video_processor=None (будет заменен на пустой)
                        from transformers.models.qwen2_5_vl.processing_qwen2_5_vl import Qwen25VLProcessor
                        
                        # Создаем пустой video_processor
                        class DummyVideoProcessor:
                            def __init__(self):
                                pass
                        
                        dummy_video_processor = DummyVideoProcessor()
                        
                        # Создаем процессор с правильными параметрами
                        self.processor = processor_class(
                            image_processor=image_processor,
                            tokenizer=tokenizer,
                            video_processor=dummy_video_processor
                        )
                        
                        logger.info("✅ Processor loaded with manual video_processor fix")
                        
                    except Exception as manual_error:
                        logger.error(f"Manual processor creation failed: {manual_error}")
                        # Последняя попытка - создаем простой процессор
                        class SimpleProcessor:
                            def __init__(self, image_processor, tokenizer):
                                self.image_processor = image_processor
                                self.tokenizer = tokenizer
                            
                            def apply_chat_template(self, messages, **kwargs):
                                return self.tokenizer.apply_chat_template(messages, **kwargs)
                            
                            def __call__(self, text=None, images=None, videos=None, **kwargs):
                                # Простая обработка без видео
                                if text and images:
                                    image_inputs = self.image_processor(images, **kwargs)
                                    text_inputs = self.tokenizer(text, **kwargs)
                                    # Объединяем входы
                                    return {**image_inputs, **text_inputs}
                                elif text:
                                    return self.tokenizer(text, **kwargs)
                                elif images:
                                    return self.image_processor(images, **kwargs)
                                return {}
                        
                        self.processor = SimpleProcessor(image_processor, tokenizer)
                        logger.info("✅ Using simple processor fallback")
                else:
                    raise e
            
            # Устанавливаем модель в режим eval
            self.model.eval()
            
            # Настраиваем токенизатор для правильной генерации
            if hasattr(self.processor, 'tokenizer'):
                tokenizer = self.processor.tokenizer
                
                # Устанавливаем pad_token если его нет
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                    logger.info("Set pad_token to eos_token")
                
                # Настраиваем специальные токены для предотвращения повторений
                if hasattr(tokenizer, 'repetition_penalty'):
                    tokenizer.repetition_penalty = 1.2
                
                logger.info(f"Tokenizer vocab size: {len(tokenizer)}")
                logger.info(f"EOS token: {tokenizer.eos_token} (ID: {tokenizer.eos_token_id})")
                logger.info(f"PAD token: {tokenizer.pad_token} (ID: {tokenizer.pad_token_id})")
            
            logger.info("dots.ocr loaded successfully with full fixes")
            
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
            
            # Оптимальный размер для dots.ocr (кратный 14)
            max_size = 1120  # 80 * 14 - уменьшено для стабильности
            
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
    
    def _safe_generate_improved(self, inputs: Dict, prompt_type: str = "simple") -> str:
        """Улучшенная генерация с предотвращением повторений."""
        try:
            # Убеждаемся что все входные данные в float16
            device = next(self.model.parameters()).device
            target_dtype = torch.float16
            
            # Исправляем dtype входных данных
            for key, value in inputs.items():
                if isinstance(value, torch.Tensor) and value.dtype not in [torch.int64, torch.int32, torch.bool]:
                    if value.dtype != target_dtype:
                        logger.debug(f"Converting input {key} from {value.dtype} to {target_dtype}")
                        inputs[key] = value.to(target_dtype)
                
                # Перемещаем на устройство
                if isinstance(value, torch.Tensor):
                    inputs[key] = value.to(device)
            
            # Оптимизированные параметры генерации для предотвращения повторений
            generation_kwargs = {
                'max_new_tokens': 256,  # Уменьшено для стабильности
                'min_new_tokens': 1,    # Минимум 1 токен
                'do_sample': True,      # Включаем sampling для разнообразия
                'temperature': 0.7,     # Умеренная температура
                'top_p': 0.9,          # Nucleus sampling
                'top_k': 50,           # Top-k sampling
                'repetition_penalty': 1.3,  # Штраф за повторения
                'no_repeat_ngram_size': 3,   # Запрет повторения 3-грамм
                'pad_token_id': self.processor.tokenizer.pad_token_id,
                'eos_token_id': self.processor.tokenizer.eos_token_id,
                'use_cache': True,
                'output_attentions': False,
                'output_hidden_states': False,
                'early_stopping': True  # Ранняя остановка
            }
            
            # Для простых промптов используем более консервативные параметры
            if prompt_type in ["minimal", "simple"]:
                generation_kwargs.update({
                    'max_new_tokens': 128,
                    'temperature': 0.3,
                    'repetition_penalty': 1.5
                })
            
            # Генерируем ответ
            with torch.no_grad():
                # Принудительно устанавливаем autocast для консистентности
                with torch.autocast(device_type='cuda', dtype=target_dtype, enabled=True):
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
            
            # Постобработка для удаления артефактов
            output_text = output_text.strip()
            
            # Удаляем повторяющиеся символы (например, !!!!!!)
            import re
            output_text = re.sub(r'(.)\1{5,}', r'\1', output_text)  # Удаляем 6+ повторений
            output_text = re.sub(r'\s+', ' ', output_text)  # Нормализуем пробелы
            
            return output_text
            
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
            try:
                text = self.processor.apply_chat_template(
                    messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
            except Exception as e:
                logger.warning(f"Chat template failed: {e}, using simple text")
                text = prompt
            
            # Обрабатываем визуальную информацию
            try:
                from qwen_vl_utils import process_vision_info
                image_inputs, video_inputs = process_vision_info(messages)
            except ImportError:
                logger.warning("qwen_vl_utils не найден, используем прямую обработку")
                image_inputs = [processed_image]
                video_inputs = None
            except Exception as e:
                logger.warning(f"process_vision_info failed: {e}, using direct processing")
                image_inputs = [processed_image]
                video_inputs = None
            
            # Подготавливаем входные данные
            try:
                inputs = self.processor(
                    text=[text],
                    images=image_inputs,
                    videos=video_inputs,
                    padding=True,
                    return_tensors="pt"
                )
            except Exception as e:
                logger.warning(f"Processor call failed: {e}, trying simplified approach")
                # Упрощенный подход для простого процессора
                try:
                    inputs = self.processor(
                        text=[text],
                        images=image_inputs,
                        padding=True,
                        return_tensors="pt"
                    )
                except Exception as e2:
                    logger.error(f"Simplified processor call also failed: {e2}")
                    # Последняя попытка - ручная обработка
                    if hasattr(self.processor, 'tokenizer') and hasattr(self.processor, 'image_processor'):
                        text_inputs = self.processor.tokenizer(
                            [text], 
                            padding=True, 
                            return_tensors="pt"
                        )
                        image_inputs_processed = self.processor.image_processor(
                            image_inputs, 
                            return_tensors="pt"
                        )
                        inputs = {**text_inputs, **image_inputs_processed}
                    else:
                        raise e2
            
            # Генерируем ответ с улучшенными параметрами
            output_text = self._safe_generate_improved(inputs, prompt_type)
            
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
            if not result or result.strip() == "" or len(result.strip()) < 3:
                logger.warning("Poor result, trying alternative prompt")
                result = self._process_with_prompt(image, self.prompts["minimal"], "minimal")
            
            # Финальная проверка на артефакты
            if result and len(set(result.replace(' ', ''))) < 3:  # Если слишком мало уникальных символов
                logger.warning("Detected repetitive output, trying OCR prompt")
                result = self._process_with_prompt(image, self.prompts["ocr"], "simple")
            
            logger.info("Processing completed successfully")
            
            return result if result and len(result.strip()) > 2 else "[dots.ocr: No meaningful text detected]"
            
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
        return self.process_image(image, prompt="Extract table content from this image", mode="simple")
    
    def parse_document(self, image: Image.Image) -> Dict[str, Any]:
        """Парсим документ."""
        try:
            result = self.process_image(image, mode="text_extraction")
            
            return {
                "success": True,
                "text": result,
                "method": "generation_fixed_parsing"
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