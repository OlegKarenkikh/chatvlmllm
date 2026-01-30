"""
ИСПРАВЛЕННАЯ РЕАЛИЗАЦИЯ dots.ocr НА ОСНОВЕ ОФИЦИАЛЬНОЙ ДОКУМЕНТАЦИИ

Основано на:
- Официальный репозиторий: https://github.com/rednote-hilab/dots.ocr
- Hugging Face: https://huggingface.co/rednote-hilab/dots.ocr
- Официальная документация и примеры использования

Ключевые исправления:
1. Правильная обработка JSON результатов
2. Корректные промпты из официального репозитория
3. Правильная обработка изображений
4. Устранение CUDA ошибок
5. Улучшенная обработка ошибок
"""

import os
import json
import torch
from typing import Any, Dict, List, Optional, Union
from PIL import Image
import traceback

from models.base_model import BaseModel
from utils.logger import logger


class DotsOCRCorrectedModel(BaseModel):
    """Исправленная реализация dots.ocr с правильной обработкой результатов."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
        self.processor = None
        self.max_new_tokens = config.get('max_new_tokens', 24000)
        
        # Отключаем параллелизм токенизатора для стабильности
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Официальные промпты из документации
        self.official_prompts = {
            "layout_all": """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

1. Bbox format: [x1, y1, x2, y2]

2. Layout Categories: The possible categories are ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title'].

3. Text Extraction & Formatting Rules:
    - Picture: For the 'Picture' category, the text field should be omitted.
    - Formula: Format its text as LaTeX.
    - Table: Format its text as HTML.
    - All Others (Text, Title, etc.): Format their text as Markdown.

4. Constraints:
    - The output text must be the original text from the image, with no translation.
    - All layout elements must be sorted according to human reading order.

5. Final Output: The entire output must be a single JSON object.""",
            
            "ocr_only": "Extract all text from this image, maintaining the original reading order.",
            
            "text_only": "Please extract all text content from this image without any layout information or formatting.",
            
            "simple_ocr": "What text do you see in this image?"
        }
    
    def load_model(self) -> None:
        """Загружаем модель с улучшенной обработкой ошибок."""
        try:
            logger.info(f"Loading dots.ocr from {self.model_path}")
            
            from transformers import AutoModelForCausalLM, AutoProcessor
            
            device = self._get_device()
            logger.info(f"Using device: {device}")
            
            # Базовые параметры загрузки
            load_kwargs = self._get_load_kwargs()
            
            # Официальные параметры из документации
            load_kwargs.update({
                'torch_dtype': torch.bfloat16,
                'trust_remote_code': True,
                'attn_implementation': "eager"  # Безопасный fallback
            })
            
            # Пробуем использовать оптимизированное внимание
            try:
                # Проверяем доступность Flash Attention
                import flash_attn
                load_kwargs['attn_implementation'] = "flash_attention_2"
                logger.info("✅ Используем flash_attention_2 для оптимальной производительности")
            except ImportError:
                # Пробуем PyTorch SDPA
                try:
                    if torch.cuda.is_available():
                        # Тестируем SDPA
                        test_tensor = torch.randn(1, 1, 10, 64, device='cuda', dtype=torch.bfloat16)
                        torch.nn.functional.scaled_dot_product_attention(test_tensor, test_tensor, test_tensor)
                        load_kwargs['attn_implementation'] = "sdpa"
                        logger.info("✅ Используем PyTorch SDPA")
                    else:
                        logger.info("💡 Используем eager attention (CPU режим)")
                except Exception as e:
                    logger.warning(f"⚠️ SDPA недоступен: {e}")
                    logger.info("💡 Используем eager attention (безопасный режим)")
            
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
                trust_remote_code=True
            )
            
            self.model.eval()
            logger.info("dots.ocr loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load dots.ocr: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _safe_inference(self, image: Image.Image, prompt: str) -> str:
        """Безопасный инференс с обработкой ошибок."""
        try:
            # Подготавливаем сообщения в формате чата
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
            
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
                logger.warning("qwen_vl_utils не найден, используем альтернативный метод")
                image_inputs = [image]
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
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs, 
                    max_new_tokens=self.max_new_tokens,
                    do_sample=False,  # Детерминированная генерация
                    temperature=0.1,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Декодируем результат
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
            logger.error(f"Inference failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _parse_json_result(self, raw_output: str) -> Union[Dict, str]:
        """Парсим JSON результат с улучшенной обработкой."""
        if not raw_output or raw_output.strip() == "":
            return "Empty result"
        
        # Пробуем парсить как JSON
        try:
            # Очищаем результат от возможных артефактов
            cleaned_output = raw_output.strip()
            
            # Ищем JSON объект в тексте
            start_idx = cleaned_output.find('{')
            end_idx = cleaned_output.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned_output[start_idx:end_idx+1]
                parsed_json = json.loads(json_str)
                
                # Если это список элементов макета, извлекаем текст
                if isinstance(parsed_json, list):
                    return self._extract_text_from_layout(parsed_json)
                elif isinstance(parsed_json, dict):
                    return self._extract_text_from_layout_dict(parsed_json)
                else:
                    return str(parsed_json)
            else:
                # JSON не найден, возвращаем как есть
                return cleaned_output
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e}")
            # Возвращаем сырой текст если JSON не парсится
            return raw_output
        except Exception as e:
            logger.error(f"Error parsing result: {e}")
            return raw_output
    
    def _extract_text_from_layout(self, layout_list: List[Dict]) -> str:
        """Извлекаем текст из списка элементов макета."""
        try:
            text_parts = []
            
            for element in layout_list:
                if isinstance(element, dict):
                    # Ищем текстовое содержимое в разных полях
                    text_content = None
                    
                    # Возможные поля с текстом
                    text_fields = ['text', 'content', 'value', 'ocr_text', 'extracted_text']
                    
                    for field in text_fields:
                        if field in element and element[field]:
                            text_content = element[field]
                            break
                    
                    if text_content:
                        # Очищаем и добавляем текст
                        cleaned_text = str(text_content).strip()
                        if cleaned_text and cleaned_text not in text_parts:
                            text_parts.append(cleaned_text)
            
            # Объединяем текст
            if text_parts:
                return '\n'.join(text_parts)
            else:
                return "No text content found in layout"
                
        except Exception as e:
            logger.error(f"Error extracting text from layout: {e}")
            return str(layout_list)
    
    def _extract_text_from_layout_dict(self, layout_dict: Dict) -> str:
        """Извлекаем текст из словаря макета."""
        try:
            # Если это словарь с элементами
            if 'elements' in layout_dict:
                return self._extract_text_from_layout(layout_dict['elements'])
            elif 'layout' in layout_dict:
                return self._extract_text_from_layout(layout_dict['layout'])
            elif 'text' in layout_dict:
                return str(layout_dict['text'])
            elif 'content' in layout_dict:
                return str(layout_dict['content'])
            else:
                # Ищем любые текстовые поля
                text_parts = []
                for key, value in layout_dict.items():
                    if isinstance(value, str) and len(value.strip()) > 0:
                        text_parts.append(value.strip())
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and 'text' in item:
                                text_parts.append(str(item['text']).strip())
                
                return '\n'.join(text_parts) if text_parts else str(layout_dict)
                
        except Exception as e:
            logger.error(f"Error extracting text from layout dict: {e}")
            return str(layout_dict)
    
    def process_image(self, image: Image.Image, prompt: Optional[str] = None, 
                     mode: str = "ocr_only") -> str:
        """Обрабатываем изображение с улучшенной логикой."""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Выбираем промпт
            if prompt is None:
                prompt = self.official_prompts.get(mode, self.official_prompts["ocr_only"])
            
            logger.info(f"Processing with mode: {mode}")
            
            # Валидируем изображение
            if image is None:
                raise ValueError("Image is None")
            
            # Конвертируем в RGB если нужно
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Выполняем инференс
            raw_result = self._safe_inference(image, prompt)
            
            # Обрабатываем результат
            if mode == "layout_all":
                # Для режима layout_all ожидаем JSON
                processed_result = self._parse_json_result(raw_result)
            else:
                # Для OCR режимов возвращаем текст как есть
                processed_result = raw_result
            
            logger.info("Processing completed successfully")
            
            # Возвращаем результат
            if isinstance(processed_result, str):
                return processed_result if processed_result else "[dots.ocr: Empty result]"
            else:
                return str(processed_result)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"[dots.ocr error: {e}]"
    
    def chat(self, image: Image.Image, prompt: str, **kwargs) -> str:
        """Чат с моделью."""
        return self.process_image(image, prompt=prompt, mode="custom")
    
    def extract_text(self, image: Image.Image) -> str:
        """Извлекаем только текст без макета."""
        return self.process_image(image, mode="text_only")
    
    def parse_document(self, image: Image.Image) -> Dict[str, Any]:
        """Парсим документ с информацией о макете."""
        try:
            result = self.process_image(image, mode="layout_all")
            
            # Пробуем парсить как JSON
            try:
                parsed = json.loads(result)
                return {
                    "success": True,
                    "layout": parsed,
                    "text": self._extract_text_from_layout(parsed) if isinstance(parsed, list) else str(parsed)
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "raw_result": result,
                    "text": result
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
            
            # Очищаем CUDA кеш безопасно
            if torch.cuda.is_available():
                try:
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                except Exception as e:
                    logger.warning(f"Warning during CUDA cleanup: {e}")
            
            logger.info("dots.ocr unloaded successfully")
            
        except Exception as e:
            logger.warning(f"Warning during model unload: {e}")