#!/usr/bin/env python3
"""Отладка проблем с OCR моделями."""

import sys
from pathlib import Path
from PIL import Image
import time

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

from models.model_loader import ModelLoader


def test_got_ocr_hf_detailed():
    """Детальный тест GOT-OCR HF для понимания проблем."""
    print("🔍 ДЕТАЛЬНЫЙ ТЕСТ GOT-OCR HF")
    print("=" * 50)
    
    # Загрузка изображения
    try:
        image = Image.open("test_interface_image.png")
        print(f"✅ Изображение загружено: {image.size}, режим: {image.mode}")
    except:
        print("❌ Не найдено test_interface_image.png")
        return
    
    try:
        # Загрузка модели
        model = ModelLoader.load_model("got_ocr_hf")
        print("✅ Модель GOT-OCR HF загружена")
        
        # Тест разных режимов
        modes = [
            ("ocr", "Чистый текст"),
            ("format", "Форматированный текст"),
        ]
        
        for mode, description in modes:
            print(f"\n🧪 Тест режима '{mode}' - {description}")
            print("-" * 30)
            
            try:
                # Обновляем режим модели
                model.ocr_type = mode
                
                # Обработка
                start_time = time.time()
                result = model.process_image(image)
                process_time = time.time() - start_time
                
                print(f"✅ Обработка за {process_time:.2f}с")
                print(f"📊 Длина результата: {len(result)} символов")
                print(f"📄 Результат:")
                print(f"   Raw: {repr(result)}")
                print(f"   Text: {result}")
                
                # Анализ качества
                if len(result) < 10:
                    print("⚠️ Слишком короткий результат")
                elif any(char in result for char in "ÀÁÂÃÄÅÆÇÈÉÊË"):
                    print("⚠️ Обнаружены искаженные символы")
                elif "RUS BO ANTE" in result:
                    print("⚠️ Обнаружен типичный искаженный текст")
                else:
                    print("✅ Результат выглядит нормально")
                
            except Exception as e:
                print(f"❌ Ошибка в режиме {mode}: {e}")
        
        # Выгрузка
        ModelLoader.unload_model("got_ocr_hf")
        print("\n🔄 Модель выгружена")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")


def test_dots_ocr_fix():
    """Тест исправления dots.ocr."""
    print("\n🔧 ТЕСТ ИСПРАВЛЕНИЯ DOTS.OCR")
    print("=" * 50)
    
    # Загрузка изображения
    try:
        image = Image.open("test_interface_image.png")
        print(f"✅ Изображение загружено: {image.size}, режим: {image.mode}")
    except:
        print("❌ Не найдено test_interface_image.png")
        return
    
    try:
        # Загрузка модели
        model = ModelLoader.load_model("dots_ocr")
        print("✅ Модель dots.ocr загружена")
        
        # Проверка компонентов модели
        print(f"\n🔍 Анализ компонентов модели:")
        print(f"   Тип процессора: {type(model.processor)}")
        print(f"   Модель: {type(model.model)}")
        
        # Простой тест OCR
        print(f"\n🧪 Простой тест OCR...")
        try:
            # Используем самый простой промпт
            simple_prompt = "Extract all text from this image."
            result = model.process_image(image, prompt=simple_prompt, mode="ocr_only")
            
            print(f"✅ Успешная обработка!")
            print(f"📊 Длина результата: {len(result)} символов")
            print(f"📄 Результат: {result[:200]}...")
            
        except Exception as e:
            print(f"❌ Ошибка обработки: {e}")
            
            # Попробуем альтернативный подход
            print(f"\n🔄 Попытка альтернативного подхода...")
            try:
                # Прямой вызов модели без сложной обработки
                from transformers import AutoTokenizer
                
                # Простой текстовый промпт
                prompt = "What text do you see in this image?"
                
                # Если процессор - словарь, используем компоненты
                if isinstance(model.processor, dict):
                    tokenizer = model.processor['tokenizer']
                    
                    # Простая токенизация
                    inputs = tokenizer(prompt, return_tensors="pt")
                    
                    # Преобразование изображения в тензор
                    import torchvision.transforms as transforms
                    
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    transform = transforms.Compose([
                        transforms.Resize((224, 224)),
                        transforms.ToTensor(),
                    ])
                    
                    pixel_values = transform(image).unsqueeze(0)
                    
                    # Объединение входов
                    device = next(model.model.parameters()).device
                    inputs = {
                        'input_ids': inputs['input_ids'].to(device),
                        'attention_mask': inputs['attention_mask'].to(device),
                        'pixel_values': pixel_values.to(device)
                    }
                    
                    # Генерация
                    with torch.no_grad():
                        outputs = model.model.generate(
                            **inputs,
                            max_new_tokens=1000,
                            do_sample=False
                        )
                    
                    # Декодирование
                    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    
                    print(f"✅ Альтернативный подход успешен!")
                    print(f"📄 Результат: {result}")
                    
                else:
                    print("❌ Альтернативный подход не применим")
                    
            except Exception as e2:
                print(f"❌ Альтернативный подход тоже не сработал: {e2}")
        
        # Выгрузка
        ModelLoader.unload_model("dots_ocr")
        print("\n🔄 Модель выгружена")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")


def test_qwen_models():
    """Тест моделей Qwen для сравнения."""
    print("\n🧪 ТЕСТ МОДЕЛЕЙ QWEN ДЛЯ СРАВНЕНИЯ")
    print("=" * 50)
    
    # Загрузка изображения
    try:
        image = Image.open("test_interface_image.png")
        print(f"✅ Изображение загружено: {image.size}, режим: {image.mode}")
    except:
        print("❌ Не найдено test_interface_image.png")
        return
    
    models_to_test = ["qwen_vl_2b", "qwen3_vl_2b"]
    
    for model_key in models_to_test:
        print(f"\n🚀 Тест модели {model_key}")
        print("-" * 30)
        
        try:
            # Загрузка модели
            model = ModelLoader.load_model(model_key)
            print("✅ Модель загружена")
            
            # OCR тест
            start_time = time.time()
            
            if hasattr(model, 'extract_text'):
                result = model.extract_text(image)
            else:
                result = model.chat(image, "Извлеките весь текст из этого документа, сохраняя структуру.")
            
            process_time = time.time() - start_time
            
            print(f"✅ Обработка за {process_time:.2f}с")
            print(f"📊 Длина результата: {len(result)} символов")
            print(f"📄 Первые 100 символов: {result[:100]}")
            
            # Выгрузка
            ModelLoader.unload_model(model_key)
            print("🔄 Модель выгружена")
            
        except Exception as e:
            print(f"❌ Ошибка с моделью {model_key}: {e}")


def main():
    """Главная функция отладки."""
    print("🔬 ОТЛАДКА ПРОБЛЕМ С OCR МОДЕЛЯМИ")
    print("=" * 60)
    
    # Тест GOT-OCR HF (основная проблема)
    test_got_ocr_hf_detailed()
    
    # Тест dots.ocr (дополнительная проблема)
    test_dots_ocr_fix()
    
    # Тест Qwen моделей (для сравнения)
    test_qwen_models()
    
    print(f"\n🏁 ОТЛАДКА ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    main()