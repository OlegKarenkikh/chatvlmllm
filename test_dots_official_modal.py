#!/usr/bin/env python3
"""
Тест dots.ocr точно по примеру из Modal Notebooks
"""

import sys
import time
import json
from pathlib import Path
from PIL import Image

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from models.model_loader import ModelLoader
from utils.logger import logger


def test_dots_ocr_modal_style():
    """Test dots.ocr exactly like in Modal Notebooks."""
    
    print("🔬 Тестирование dots.ocr по примеру Modal Notebooks")
    print("=" * 60)
    
    # Load model
    start_time = time.time()
    model = ModelLoader.load_model('dots_ocr')
    load_time = time.time() - start_time
    print(f"✅ Модель загружена за {load_time:.2f}с")
    
    # Test with realistic document
    test_image_path = "realistic_document.png"
    if not Path(test_image_path).exists():
        print("❌ Файл realistic_document.png не найден")
        return
    
    image = Image.open(test_image_path)
    print(f"📷 Изображение загружено: {image.size}, режим: {image.mode}")
    
    # Test 1: OCR mode (like Modal example)
    print("\n🔤 Тест 1: Простое OCR")
    try:
        from utils.dots_prompts import dict_promptmode_to_prompt
        prompt = dict_promptmode_to_prompt["ocr"]
    except ImportError:
        prompt = "Extract all text from this image."
    
    print(f"Промпт: {prompt}")
    
    start_time = time.time()
    result1 = model.inference(image, prompt)
    process_time1 = time.time() - start_time
    
    print(f"⏱️ Время обработки: {process_time1:.2f}с")
    print(f"📄 Результат ({len(result1)} символов):")
    print(result1[:300] + "..." if len(result1) > 300 else result1)
    
    # Test 2: Layout analysis (like Modal example)
    print("\n📋 Тест 2: Анализ layout")
    try:
        from utils.dots_prompts import dict_promptmode_to_prompt
        prompt = dict_promptmode_to_prompt["prompt_layout_all_en"]
    except ImportError:
        prompt = """Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

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
    
    print(f"Промпт: {prompt[:100]}...")
    
    start_time = time.time()
    result2 = model.inference(image, prompt)
    process_time2 = time.time() - start_time
    
    print(f"⏱️ Время обработки: {process_time2:.2f}с")
    print(f"📄 Результат ({len(result2)} символов):")
    
    # Try to parse as JSON
    try:
        parsed = json.loads(result2)
        print(f"✅ Валидный JSON с {len(parsed)} элементами")
        
        # Show first few elements
        for i, element in enumerate(parsed[:5]):
            bbox = element.get('bbox', [])
            category = element.get('category', 'Unknown')
            text = element.get('text', '')[:50]
            print(f"  {i+1}. {category:15} | {str(bbox):25} | {text}...")
            
        if len(parsed) > 5:
            print(f"  ... и еще {len(parsed) - 5} элементов")
            
    except json.JSONDecodeError:
        print("❌ Результат не является валидным JSON")
        print(result2[:500] + "..." if len(result2) > 500 else result2)
    
    # Unload model
    ModelLoader.unload_model('dots_ocr')
    print("\n✅ Модель выгружена")
    print("🎯 Тест завершен!")


if __name__ == "__main__":
    test_dots_ocr_modal_style()