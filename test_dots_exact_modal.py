#!/usr/bin/env python3
"""
Точная копия примера из Modal Notebooks для dots.ocr
"""

import os
import sys
import json
import torch
from pathlib import Path
from PIL import Image

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Set environment variable
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from models.model_loader import ModelLoader
from utils.logger import logger


def inference(image_path_or_pil, prompt: str, model, processor):
    """Точная копия функции inference из Modal Notebooks."""
    
    # Handle both file path and PIL Image
    if isinstance(image_path_or_pil, str):
        image_path = image_path_or_pil
    else:
        # For PIL Image, we need to save it temporarily or handle differently
        image_path = image_path_or_pil
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
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
    
    # Inference: Generation of the output
    generated_ids = model.generate(**inputs, max_new_tokens=24000)
    
    generated_ids_trimmed = [
        out_ids[len(in_ids):] 
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    
    (output_text,) = processor.batch_decode(
        generated_ids_trimmed, 
        skip_special_tokens=True, 
        clean_up_tokenization_spaces=False
    )
    
    return json.loads(output_text)


def test_exact_modal_implementation():
    """Тест точной реализации Modal Notebooks."""
    
    print("🔬 Тестирование ТОЧНОЙ копии Modal Notebooks")
    print("=" * 60)
    
    # Load model using our model loader
    model_wrapper = ModelLoader.load_model('dots_ocr')
    
    # Get the actual model and processor
    model = model_wrapper.model
    processor = model_wrapper.processor
    
    print("✅ Модель и процессор загружены")
    
    # Import prompts (exact Modal way)
    try:
        from dots_ocr.utils import dict_promptmode_to_prompt
        print("✅ Промпты импортированы из dots_ocr.utils")
    except ImportError:
        print("❌ Не удалось импортировать dots_ocr.utils")
        return
    
    # Test with our complex document
    image_path = "complex_document.png"
    if not Path(image_path).exists():
        print("❌ Файл complex_document.png не найден")
        return
    
    image = Image.open(image_path)
    print(f"📷 Изображение загружено: {image.size}")
    
    # Test 1: OCR mode (exact Modal)
    print("\n🔤 Тест 1: OCR (точно как в Modal)")
    prompt = dict_promptmode_to_prompt["ocr"]
    print(f"Промпт: {prompt}")
    
    try:
        result1 = inference(image, prompt, model, processor)
        print(f"✅ Результат OCR: {type(result1)}")
        if isinstance(result1, list):
            print(f"   Найдено элементов: {len(result1)}")
        else:
            print(f"   Результат: {result1}")
    except Exception as e:
        print(f"❌ Ошибка OCR: {e}")
    
    # Test 2: Layout analysis (exact Modal)
    print("\n📋 Тест 2: Layout анализ (точно как в Modal)")
    prompt = dict_promptmode_to_prompt["prompt_layout_all_en"]
    print(f"Промпт: {prompt[:100]}...")
    
    try:
        result2 = inference(image, prompt, model, processor)
        print(f"✅ Результат Layout: {type(result2)}")
        
        if isinstance(result2, list):
            print(f"   Найдено элементов: {len(result2)}")
            
            # Show categories
            categories = {}
            for element in result2:
                cat = element.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            print("   Категории:")
            for cat, count in categories.items():
                print(f"     {cat}: {count}")
                
            # Show first few elements
            print("   Первые элементы:")
            for i, element in enumerate(result2[:3]):
                bbox = element.get('bbox', [])
                category = element.get('category', 'Unknown')
                text = element.get('text', '')[:50]
                print(f"     {i+1}. {category} | {bbox} | {text}...")
                
        else:
            print(f"   Результат: {result2}")
            
    except Exception as e:
        print(f"❌ Ошибка Layout: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
    
    # Unload model
    ModelLoader.unload_model('dots_ocr')
    print("\n✅ Тест завершен!")


if __name__ == "__main__":
    test_exact_modal_implementation()