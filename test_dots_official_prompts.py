#!/usr/bin/env python3
"""
Тест dots.ocr с официальными промптами
"""

import os
import sys
import time
import torch
from pathlib import Path
from PIL import Image

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Set environment variable
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from models.model_loader import ModelLoader
from utils.logger import logger


def test_with_official_prompts():
    """Тест с официальными промптами dots.ocr."""
    
    print("📋 ТЕСТ С ОФИЦИАЛЬНЫМИ ПРОМПТАМИ DOTS.OCR")
    print("=" * 50)
    
    try:
        # Load model
        print("📥 Загрузка модели...")
        model_wrapper = ModelLoader.load_model('dots_ocr')
        
        # Get the actual model and processor
        model = model_wrapper.model
        processor = model_wrapper.processor
        
        print("✅ Модель загружена")
        
        # Try to get official prompts
        try:
            from dots_ocr.utils import dict_promptmode_to_prompt
            print("✅ Официальные промпты импортированы")
            
            ocr_prompt = dict_promptmode_to_prompt["ocr"]
            layout_prompt = dict_promptmode_to_prompt["prompt_layout_all_en"]
            
            print(f"📝 OCR промпт: {ocr_prompt[:100]}...")
            print(f"📋 Layout промпт: {layout_prompt[:100]}...")
            
        except ImportError:
            print("❌ Не удалось импортировать официальные промпты")
            print("💡 Используем fallback промпты")
            
            ocr_prompt = "Extract all text from this image."
            layout_prompt = """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

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
5. Final Output: The entire output must be a single JSON object."""
        
        # Test with different images
        test_images = ["test_document.png", "complex_document.png", "realistic_document.png"]
        
        for image_path in test_images:
            if not Path(image_path).exists():
                print(f"⏭️ Пропускаем {image_path} - файл не найден")
                continue
                
            print(f"\n🖼️ Тестируем с {image_path}")
            
            image = Image.open(image_path)
            print(f"📷 Размер: {image.size}, режим: {image.mode}")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Test OCR prompt
            print("\n🔤 Тест OCR промпта...")
            result = test_prompt(model, processor, image, ocr_prompt, "OCR")
            
            if result and result.strip():
                print("✅ OCR работает!")
                break
            
            # Test Layout prompt
            print("\n📋 Тест Layout промпта...")
            result = test_prompt(model, processor, image, layout_prompt, "Layout")
            
            if result and result.strip():
                print("✅ Layout работает!")
                break
        
        # Unload model
        ModelLoader.unload_model('dots_ocr')
        print("\n✅ Тест завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")


def test_prompt(model, processor, image, prompt, prompt_type):
    """Тест конкретного промпта."""
    
    try:
        # Manual inference
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        # Preparation for inference
        text = processor.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Process vision info
        from qwen_vl_utils import process_vision_info
        image_inputs, video_inputs = process_vision_info(messages)
        
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        
        inputs = inputs.to("cuda")
        
        # Generate with more tokens
        print(f"🚀 Генерация для {prompt_type}...")
        
        with torch.no_grad():
            generated_ids = model.generate(
                **inputs, 
                max_new_tokens=2000,  # Больше токенов
                do_sample=False,
                pad_token_id=processor.tokenizer.eos_token_id,
                eos_token_id=processor.tokenizer.eos_token_id
            )
        
        # Decode output
        generated_ids_trimmed = [
            out_ids[len(in_ids):] 
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        (output_text,) = processor.batch_decode(
            generated_ids_trimmed, 
            skip_special_tokens=True, 
            clean_up_tokenization_spaces=False
        )
        
        print(f"📤 {prompt_type} результат:")
        print(f"Длина: {len(output_text)}")
        
        if output_text.strip():
            print(f"Содержимое: {output_text[:200]}...")
            
            # Try JSON parsing for layout
            if prompt_type == "Layout":
                try:
                    import json
                    parsed = json.loads(output_text)
                    print(f"✅ Валидный JSON: {type(parsed)}")
                except json.JSONDecodeError:
                    print("⚠️ Не JSON, но есть текст")
        else:
            print("❌ Пустой результат")
        
        return output_text
        
    except Exception as e:
        print(f"❌ Ошибка в {prompt_type}: {e}")
        return None


if __name__ == "__main__":
    test_with_official_prompts()