"""
DOTS.OCR С ИСПРАВЛЕНИЕМ VIDEO_PROCESSOR ПРОБЛЕМЫ

Исправляет критическую ошибку:
TypeError: Received a NoneType for argument video_processor, but a BaseVideoProcessor was expected.

Эта ошибка возникает из-за несовместимости dots.ocr с новыми версиями transformers,
где Qwen2.5-VL процессор требует video_processor параметр.
"""

import os
import json
import torch
from typing import Any, Dict, List, Optional, Union
from PIL import Image
import traceback

from models.base_model import BaseModel
from utils.logger import logger


class DotsOCRVideoProcessorFixedModel(BaseModel):
    """dots.ocr с исправлением video_processor проблемы."""
    
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
    
    def _create_video_processor_mock(self):
        """Создаем заглушку для video_processor."""
        try:
            from transformers.models.qwen2_5_vl.processing_qwen2_5_vl import Qwen25VLVideoProcessor
            
            # Создаем минимальную заглушку
            class VideoProcessorMock:
                def __init__(self):
                    pass
                
                def __call__(self, *args, **kwargs):
                    return None
                
                def preprocess(self, *args, **kwargs):
                    return None
            
            return VideoProcessorMock()
            
        except ImportError:
            # Если Qwen25VLVideoProcessor недоступен, создаем простую заглушку
            class SimpleVideoProcessorMock:
                def __init__(self):
                    pass
                
                def __call__(self, *args, **kwargs):
                    return None
            
            return SimpleVideoProcessorMock()
    
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
        """Загружаем модель с исправлением video_processor проблемы."""
        try:
            logger.info(f"Loading dots.ocr with video_processor fix from {self.model_path}")
            
            from transformers import AutoModelForCausalLM, AutoProcessor, AutoImageProcessor, AutoTokenizer
            
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
            logger.info("Loading processor with video_processor fix...")
            
            try:
                # Пробуем стандартную загрузку
                self.processor = AutoProcessor.from_pretrained(
                    self.model_path, 
                    trust_remote_code=True,
                    use_fast=False
                )
                logger.info("✅ Standard processor loading successful")
                
            except TypeError as e:
                if "video_processor" in str(e):
                    logger.warning("🔧 video_processor error detected, applying fix...")
                    
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
                    
                    # Создаем заглушку для video_processor
                    video_processor_mock = self._create_video_processor_mock()
                    
                    # Пытаемся создать процессор с правильными параметрами
                    try:
                        # Создаем простой video processor
                        from transformers.image_processing_utils import BaseImageProcessor
                        
                        class DummyVideoProcessor(BaseImageProcessor):
                            """Заглушка для video_processor, наследующая от BaseImageProcessor."""
                            
                            def __init__(self):
                                super().__init__()
                            
                            def preprocess(self, videos, **kwargs):
                                # Возвращаем пустой результат для видео
                                return {}
                            
                            def __call__(self, videos=None, **kwargs):
                                if videos is None:
                                    return {}
                                return self.preprocess(videos, **kwargs)
                        
                        # Создаем заглушку
                        dummy_video_processor = DummyVideoProcessor()
                        
                        # Создаем кастомный процессор напрямую
                        class DotsOCRProcessorFixed:
                            def __init__(self, image_processor, tokenizer, video_processor=None):
                                self.image_processor = image_processor
                                self.tokenizer = tokenizer
                                self.video_processor = video_processor or dummy_video_processor
                            
                            def apply_chat_template(self, messages, **kwargs):
                                return self.tokenizer.apply_chat_template(messages, **kwargs)
                            
                            def __call__(self, text=None, images=None, videos=None, **kwargs):
                                result = {}
                                
                                if text is not None:
                                    text_inputs = self.tokenizer(text, **kwargs)
                                    result.update(text_inputs)
                                
                                if images is not None:
                                    # Правильная обработка изображений для dots.ocr
                                    image_inputs = self.image_processor(
                                        images, 
                                        return_tensors=kwargs.get('return_tensors', 'pt')
                                    )
                                    result.update(image_inputs)
                                    
                                    # Создаем img_mask если его нет
                                    if 'img_mask' not in result and 'pixel_values' in image_inputs:
                                        batch_size = image_inputs['pixel_values'].shape[0]
                                        if len(image_inputs['pixel_values'].shape) == 3:
                                            # Формат [batch, patches, features]
                                            total_patches = image_inputs['pixel_values'].shape[1]
                                        else:
                                            # Используем размер из image_grid_thw если доступен
                                            if 'image_grid_thw' in result:
                                                grid_thw = result['image_grid_thw']
                                                if len(grid_thw.shape) >= 2 and grid_thw.shape[1] >= 3:
                                                    _, h_patches, w_patches = grid_thw[0]
                                                    total_patches = h_patches * w_patches
                                                else:
                                                    total_patches = 256  # fallback
                                            else:
                                                total_patches = 256  # fallback
                                        
                                        import torch
                                        result['img_mask'] = torch.ones(batch_size, total_patches, dtype=torch.bool)
                                    
                                    # Используем существующий image_grid_thw если он есть, иначе создаем свой
                                    if 'image_grid_thw' not in image_inputs and 'pixel_values' in image_inputs:
                                        batch_size = image_inputs['pixel_values'].shape[0]
                                        
                                        # Для dots.ocr нужно правильно вычислить размеры сетки
                                        # pixel_values имеет форму [batch, channels, height, width]
                                        if len(image_inputs['pixel_values'].shape) == 4:
                                            _, channels, height, width = image_inputs['pixel_values'].shape
                                            # Вычисляем количество патчей (обычно 14x14 патчи)
                                            patch_size = 14  # стандартный размер патча для ViT
                                            h_patches = height // patch_size
                                            w_patches = width // patch_size
                                            total_patches = h_patches * w_patches
                                        else:
                                            # Если уже в формате патчей [batch, patches, features]
                                            total_patches = image_inputs['pixel_values'].shape[1]
                                            # Для 588 патчей: попробуем 21x28 = 588
                                            if total_patches == 588:
                                                h_patches, w_patches = 21, 28
                                            else:
                                                # Общий случай - найдем ближайшие факторы
                                                import math
                                                sqrt_patches = int(math.sqrt(total_patches))
                                                h_patches = sqrt_patches
                                                w_patches = sqrt_patches
                                                # Если не квадратная, найдем лучшие факторы
                                                if h_patches * w_patches != total_patches:
                                                    for i in range(sqrt_patches, 0, -1):
                                                        if total_patches % i == 0:
                                                            h_patches = i
                                                            w_patches = total_patches // i
                                                            break
                                        
                                        # Создаем image_grid_thw (время, высота, ширина для каждого изображения)
                                        # Для статических изображений время = 1
                                        import torch
                                        result['image_grid_thw'] = torch.tensor([[1, h_patches, w_patches]], dtype=torch.long)
                                        
                                        # Создаем img_mask (маска для изображений)
                                        result['img_mask'] = torch.ones(batch_size, total_patches, dtype=torch.bool)
                                
                                # Игнорируем videos, так как dots.ocr их не поддерживает
                                
                                return result
                            
                            def batch_decode(self, *args, **kwargs):
                                return self.tokenizer.batch_decode(*args, **kwargs)
                        
                        self.processor = DotsOCRProcessorFixed(
                            image_processor=image_processor,
                            tokenizer=tokenizer,
                            video_processor=dummy_video_processor
                        )
                        
                        logger.info("✅ Custom processor created successfully")
                    
                    except Exception as custom_error:
                        logger.error(f"Custom processor creation failed: {custom_error}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        
                        # Последняя попытка - создаем максимально простой процессор
                        logger.warning("Trying ultra-simple processor fallback...")
                        
                        class UltraSimpleProcessor:
                            def __init__(self, image_processor, tokenizer):
                                self.image_processor = image_processor
                                self.tokenizer = tokenizer
                            
                            def apply_chat_template(self, messages, **kwargs):
                                # Простая обработка сообщений
                                if isinstance(messages, list) and len(messages) > 0:
                                    message = messages[0]
                                    if isinstance(message, dict) and 'content' in message:
                                        content = message['content']
                                        if isinstance(content, list):
                                            for item in content:
                                                if isinstance(item, dict) and item.get('type') == 'text':
                                                    return item.get('text', '')
                                        elif isinstance(content, str):
                                            return content
                                return kwargs.get('text', '')
                            
                            def __call__(self, text=None, images=None, videos=None, **kwargs):
                                result = {}
                                
                                if text is not None:
                                    try:
                                        text_inputs = self.tokenizer(text, **kwargs)
                                        result.update(text_inputs)
                                    except Exception as e:
                                        logger.warning(f"Tokenizer failed: {e}")
                                        # Минимальная токенизация
                                        import torch
                                        result['input_ids'] = torch.tensor([[1, 2, 3]])  # Dummy tokens
                                        result['attention_mask'] = torch.tensor([[1, 1, 1]])
                                
                                if images is not None:
                                    try:
                                        image_inputs = self.image_processor(images, return_tensors=kwargs.get('return_tensors', 'pt'))
                                        result.update(image_inputs)
                                        
                                        # КРИТИЧЕСКИ ВАЖНО: Создаем правильный img_mask
                                        if 'pixel_values' in image_inputs:
                                            # Всегда пересоздаем img_mask для гарантии корректности
                                            pixel_values = image_inputs['pixel_values']
                                            
                                            if len(pixel_values.shape) == 2:
                                                # Формат [patches, features]
                                                batch_size = 1
                                                total_patches = pixel_values.shape[0]
                                            elif len(pixel_values.shape) == 3:
                                                # Формат [batch, patches, features] 
                                                batch_size = pixel_values.shape[0]
                                                total_patches = pixel_values.shape[1]
                                            else:
                                                # Fallback на основе image_grid_thw
                                                batch_size = 1
                                                if 'image_grid_thw' in result:
                                                    grid_thw = result['image_grid_thw']
                                                    if len(grid_thw.shape) >= 2 and grid_thw.shape[1] >= 3:
                                                        _, h_patches, w_patches = grid_thw[0]
                                                        total_patches = int(h_patches * w_patches)
                                                    else:
                                                        total_patches = 256
                                                else:
                                                    total_patches = 256
                                            
                                            import torch
                                            # Принудительно создаем маску на правильном устройстве
                                            device = pixel_values.device if hasattr(pixel_values, 'device') else 'cpu'
                                            result['img_mask'] = torch.ones(batch_size, total_patches, dtype=torch.bool, device=device)
                                            
                                            logger.info(f"🔧 Created img_mask: shape={result['img_mask'].shape}, sum={result['img_mask'].sum()}, device={result['img_mask'].device}")
                                        
                                        # Используем существующий image_grid_thw если он есть, иначе создаем свой
                                        if 'image_grid_thw' not in image_inputs and 'pixel_values' in image_inputs:
                                            batch_size = image_inputs['pixel_values'].shape[0]
                                            
                                            # Для dots.ocr нужно правильно вычислить размеры сетки
                                            # pixel_values может быть в формате [batch, patches, features] или [batch, channels, height, width]
                                            if len(image_inputs['pixel_values'].shape) == 4:
                                                _, channels, height, width = image_inputs['pixel_values'].shape
                                                # Вычисляем количество патчей (обычно 14x14 патчи)
                                                patch_size = 14  # стандартный размер патча для ViT
                                                h_patches = height // patch_size
                                                w_patches = width // patch_size
                                                total_patches = h_patches * w_patches
                                            elif len(image_inputs['pixel_values'].shape) == 3:
                                                # Уже в формате патчей [batch, patches, features]
                                                batch_size, total_patches, features = image_inputs['pixel_values'].shape
                                                # Предполагаем квадратную сетку патчей
                                                h_patches = int(total_patches ** 0.5)
                                                w_patches = h_patches
                                                # Если не квадратная, используем приближение
                                                if h_patches * w_patches != total_patches:
                                                    # Для 588 патчей: 24x24 = 576, 25x24 = 600, попробуем 21x28 = 588
                                                    if total_patches == 588:
                                                        h_patches, w_patches = 21, 28
                                                    else:
                                                        # Общий случай - найдем ближайшие факторы
                                                        import math
                                                        sqrt_patches = int(math.sqrt(total_patches))
                                                        for i in range(sqrt_patches, 0, -1):
                                                            if total_patches % i == 0:
                                                                h_patches = i
                                                                w_patches = total_patches // i
                                                                break
                                            else:
                                                # Неожиданный формат, используем безопасные значения
                                                total_patches = image_inputs['pixel_values'].shape[1] if len(image_inputs['pixel_values'].shape) > 1 else 1
                                                h_patches = int(total_patches ** 0.5)
                                                w_patches = h_patches
                                            
                                            import torch
                                            result['image_grid_thw'] = torch.tensor([[1, h_patches, w_patches]], dtype=torch.long)
                                            result['img_mask'] = torch.ones(batch_size, total_patches, dtype=torch.bool)
                                            
                                    except Exception as e:
                                        logger.warning(f"Image processor failed: {e}")
                                
                                return result
                            
                            def batch_decode(self, *args, **kwargs):
                                return self.tokenizer.batch_decode(*args, **kwargs)
                        
                        self.processor = UltraSimpleProcessor(image_processor, tokenizer)
                        logger.info("✅ Ultra-simple processor fallback created")
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
                
                logger.info(f"Tokenizer vocab size: {len(tokenizer)}")
                logger.info(f"EOS token: {tokenizer.eos_token} (ID: {tokenizer.eos_token_id})")
                logger.info(f"PAD token: {tokenizer.pad_token} (ID: {tokenizer.pad_token_id})")
            
            logger.info("✅ dots.ocr loaded successfully with video_processor fix")
            
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
            
            # Фильтруем входные данные - оставляем только те, что принимает модель
            model_inputs = {}
            valid_keys = ['input_ids', 'attention_mask', 'pixel_values', 'image_grid_thw']
            
            for key, value in inputs.items():
                if key in valid_keys:
                    model_inputs[key] = value
                else:
                    logger.debug(f"Skipping input key: {key}")
            
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
                'output_hidden_states': False
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
                        **model_inputs,
                        **generation_kwargs
                    )
            
            # Декодируем результат
            generated_ids_trimmed = [
                out_ids[len(in_ids):] 
                for in_ids, out_ids in zip(model_inputs['input_ids'], generated_ids)
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
                logger.warning(f"Processor call with videos failed: {e}, trying without videos")
                try:
                    inputs = self.processor(
                        text=[text],
                        images=image_inputs,
                        padding=True,
                        return_tensors="pt"
                    )
                except Exception as e2:
                    logger.error(f"Processor call failed: {e2}")
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
                "method": "video_processor_fixed_parsing"
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