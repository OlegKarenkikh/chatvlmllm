#!/usr/bin/env python3
"""
Полный тест рабочего процесса всех моделей:
- qwen_vl_2b (Qwen2-VL)
- qwen3_vl_2b (Qwen3-VL) 
- dots_ocr
Включает: загрузку, определение типа документа, распознавание полей, измерение скорости
"""

import time
import torch
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import json
import yaml

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_drivers_license():
    """Создаем изображение водительского удостоверения"""
    img = Image.new('RGB', (600, 400), color='#E8F4FD')  # Голубоватый фон
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 18)
        main_font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Заголовок
    draw.text((20, 15), "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ", fill='black', font=title_font)
    draw.text((20, 40), "РОССИЙСКАЯ ФЕДЕРАЦИЯ", fill='black', font=main_font)
    
    # Основные поля
    draw.text((20, 80), "1. Фамилия: ИВАНОВ", fill='black', font=main_font)
    draw.text((20, 105), "2. Имя: ИВАН", fill='black', font=main_font)
    draw.text((20, 130), "3. Отчество: ИВАНОВИЧ", fill='black', font=main_font)
    
    draw.text((20, 165), "4a. Дата рождения: 15.03.1985", fill='black', font=main_font)
    draw.text((20, 190), "4b. Место рождения: г. Москва", fill='black', font=main_font)
    
    draw.text((20, 225), "5. Номер: 77 12 345678", fill='black', font=main_font)
    draw.text((20, 250), "4c. Дата выдачи: 20.05.2020", fill='black', font=main_font)
    draw.text((20, 275), "4d. Действительно до: 20.05.2030", fill='black', font=main_font)
    
    draw.text((20, 310), "7. Подпись владельца: И.Иванов", fill='black', font=small_font)
    
    # Категории
    draw.text((350, 80), "9. Категории:", fill='black', font=main_font)
    draw.text((350, 105), "B - легковые автомобили", fill='black', font=small_font)
    draw.text((350, 125), "Дата получения: 20.05.2020", fill='black', font=small_font)
    
    # Рамка
    draw.rectangle([10, 10, 590, 390], outline='black', width=2)
    
    return img

def create_passport():
    """Создаем изображение паспорта"""
    img = Image.new('RGB', (600, 400), color='#FFF8DC')  # Кремовый фон
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 16)
        main_font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
    
    # Заголовок
    draw.text((20, 15), "ПАСПОРТ ГРАЖДАНИНА", fill='black', font=title_font)
    draw.text((20, 35), "РОССИЙСКОЙ ФЕДЕРАЦИИ", fill='black', font=title_font)
    
    # Основные поля
    draw.text((20, 80), "Фамилия: ПЕТРОВ", fill='black', font=main_font)
    draw.text((20, 105), "Имя: ПЕТР", fill='black', font=main_font)
    draw.text((20, 130), "Отчество: ПЕТРОВИЧ", fill='black', font=main_font)
    
    draw.text((20, 165), "Пол: МУЖ.", fill='black', font=main_font)
    draw.text((150, 165), "Дата рождения: 10.07.1990", fill='black', font=main_font)
    
    draw.text((20, 195), "Место рождения: г. Санкт-Петербург", fill='black', font=main_font)
    
    draw.text((20, 230), "Серия и номер: 40 17 123456", fill='black', font=main_font)
    draw.text((20, 255), "Дата выдачи: 15.08.2010", fill='black', font=main_font)
    draw.text((20, 280), "Код подразделения: 780-001", fill='black', font=main_font)
    
    # Рамка
    draw.rectangle([10, 10, 590, 390], outline='black', width=2)
    
    return img

def create_invoice():
    """Создаем изображение счета"""
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 16)
        main_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        main_font = ImageFont.load_default()
    
    # Заголовок
    draw.text((20, 15), "СЧЕТ № INV-2026-001", fill='black', font=title_font)
    draw.text((20, 40), "от 24.01.2026", fill='black', font=main_font)
    
    # Поставщик
    draw.text((20, 70), "Поставщик: ООО \"ТехКомпани\"", fill='black', font=main_font)
    draw.text((20, 90), "ИНН: 7701234567", fill='black', font=main_font)
    draw.text((20, 110), "Адрес: г. Москва, ул. Тверская, д. 1", fill='black', font=main_font)
    
    # Покупатель
    draw.text((20, 140), "Покупатель: ООО \"КлиентСервис\"", fill='black', font=main_font)
    draw.text((20, 160), "ИНН: 7702345678", fill='black', font=main_font)
    
    # Таблица товаров
    draw.text((20, 190), "Наименование товара", fill='black', font=main_font)
    draw.text((250, 190), "Кол-во", fill='black', font=main_font)
    draw.text((320, 190), "Цена", fill='black', font=main_font)
    draw.text((400, 190), "Сумма", fill='black', font=main_font)
    
    draw.line([20, 205, 480, 205], fill='black', width=1)
    
    draw.text((20, 215), "Компьютер Dell OptiPlex", fill='black', font=main_font)
    draw.text((250, 215), "2 шт", fill='black', font=main_font)
    draw.text((320, 215), "45 000", fill='black', font=main_font)
    draw.text((400, 215), "90 000", fill='black', font=main_font)
    
    draw.text((20, 235), "Монитор Samsung 24\"", fill='black', font=main_font)
    draw.text((250, 235), "2 шт", fill='black', font=main_font)
    draw.text((320, 235), "15 000", fill='black', font=main_font)
    draw.text((400, 235), "30 000", fill='black', font=main_font)
    
    draw.line([20, 255, 480, 255], fill='black', width=1)
    
    # Итого
    draw.text((300, 270), "Итого: 120 000 руб.", fill='black', font=title_font)
    draw.text((300, 295), "НДС 20%: 20 000 руб.", fill='black', font=main_font)
    draw.text((300, 315), "Всего к оплате: 140 000 руб.", fill='black', font=title_font)
    
    return img

def check_flash_attention_status(model_name):
    """Проверяет статус Flash Attention для модели"""
    try:
        config_path = 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        model_config = config.get('models', {}).get(model_name, {})
        use_flash = model_config.get('use_flash_attention', False)
        attn_impl = model_config.get('attn_implementation', 'eager')
        
        return {
            "use_flash_attention": use_flash,
            "attn_implementation": attn_impl,
            "configured_correctly": True
        }
    except Exception as e:
        return {
            "use_flash_attention": False,
            "attn_implementation": "unknown",
            "configured_correctly": False,
            "error": str(e)
        }

def test_model_workflow(model_name, test_images):
    """Тестирует полный рабочий процесс модели"""
    print(f"\n🚀 ТЕСТ МОДЕЛИ: {model_name}")
    print("=" * 60)
    
    # Проверяем Flash Attention
    flash_status = check_flash_attention_status(model_name)
    print(f"⚡ Flash Attention статус:")
    print(f"   use_flash_attention: {flash_status['use_flash_attention']}")
    print(f"   attn_implementation: {flash_status['attn_implementation']}")
    
    try:
        from models.model_loader import ModelLoader
        
        # 1. ЗАГРУЗКА МОДЕЛИ
        print(f"\n📥 1. ЗАГРУЗКА МОДЕЛИ...")
        start_load = time.time()
        
        model = ModelLoader.load_model(model_name)
        load_time = time.time() - start_load
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Проверяем VRAM
        if torch.cuda.is_available():
            vram_used = torch.cuda.memory_allocated(0) / 1024**3
            print(f"💾 VRAM использовано: {vram_used:.2f}GB")
        
        results = []
        
        # 2. ТЕСТИРОВАНИЕ НА РАЗНЫХ ТИПАХ ДОКУМЕНТОВ
        for doc_type, image in test_images.items():
            print(f"\n📄 2. ТЕСТ ДОКУМЕНТА: {doc_type.upper()}")
            
            # Определение типа документа
            start_detect = time.time()
            
            # Простое определение типа по содержимому
            if hasattr(model, 'chat'):
                type_prompt = "Определи тип документа на изображении. Ответь одним словом: паспорт, водительское_удостоверение, счет или другое."
                detected_type = model.chat(image, type_prompt)
            else:
                detected_type = "Не поддерживается"
            
            detect_time = time.time() - start_detect
            
            print(f"🔍 Определение типа: {detected_type} ({detect_time:.2f}s)")
            
            # OCR распознавание
            start_ocr = time.time()
            
            if doc_type == "drivers_license":
                ocr_prompt = "Извлеки все поля из водительского удостоверения: фамилию, имя, отчество, дату рождения, номер, дату выдачи, категории."
            elif doc_type == "passport":
                ocr_prompt = "Извлеки все поля из паспорта: фамилию, имя, отчество, дату рождения, серию и номер, дату выдачи."
            elif doc_type == "invoice":
                ocr_prompt = "Извлеки все поля из счета: номер счета, дату, поставщика, покупателя, товары, итоговую сумму."
            else:
                ocr_prompt = "Извлеки весь текст с изображения."
            
            if hasattr(model, 'process_image'):
                ocr_result = model.process_image(image, ocr_prompt)
            elif hasattr(model, 'chat'):
                ocr_result = model.chat(image, ocr_prompt)
            else:
                ocr_result = "Метод не поддерживается"
            
            ocr_time = time.time() - start_ocr
            
            print(f"📝 OCR результат ({len(ocr_result)} символов):")
            print(f"   {ocr_result[:200]}{'...' if len(ocr_result) > 200 else ''}")
            print(f"⏱️ Время OCR: {ocr_time:.2f}s")
            
            # Анализ качества распознавания
            quality_score = analyze_ocr_quality(doc_type, ocr_result)
            print(f"🎯 Качество распознавания: {quality_score:.0f}%")
            
            results.append({
                "document_type": doc_type,
                "detected_type": detected_type,
                "detect_time": detect_time,
                "ocr_time": ocr_time,
                "total_time": detect_time + ocr_time,
                "quality_score": quality_score,
                "result_length": len(ocr_result)
            })
        
        # 3. ИТОГОВАЯ СТАТИСТИКА
        print(f"\n📊 3. ИТОГОВАЯ СТАТИСТИКА МОДЕЛИ {model_name}")
        print("-" * 50)
        
        total_docs = len(results)
        avg_detect_time = sum(r["detect_time"] for r in results) / total_docs
        avg_ocr_time = sum(r["ocr_time"] for r in results) / total_docs
        avg_total_time = sum(r["total_time"] for r in results) / total_docs
        avg_quality = sum(r["quality_score"] for r in results) / total_docs
        
        print(f"📈 Среднее время определения типа: {avg_detect_time:.2f}s")
        print(f"📈 Среднее время OCR: {avg_ocr_time:.2f}s")
        print(f"📈 Среднее общее время: {avg_total_time:.2f}s")
        print(f"📈 Среднее качество: {avg_quality:.0f}%")
        
        # Проверяем VRAM после обработки
        if torch.cuda.is_available():
            vram_after = torch.cuda.memory_allocated(0) / 1024**3
            print(f"💾 VRAM после обработки: {vram_after:.2f}GB")
        
        # НЕ ВЫГРУЖАЕМ МОДЕЛЬ (как требуется)
        print(f"🔄 Модель остается в памяти для следующих запросов")
        
        return {
            "model_name": model_name,
            "load_time": load_time,
            "flash_attention": flash_status,
            "results": results,
            "averages": {
                "detect_time": avg_detect_time,
                "ocr_time": avg_ocr_time,
                "total_time": avg_total_time,
                "quality": avg_quality
            },
            "vram_usage": vram_after if torch.cuda.is_available() else 0
        }
        
    except Exception as e:
        print(f"❌ Ошибка тестирования модели {model_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "model_name": model_name,
            "error": str(e),
            "success": False
        }

def analyze_ocr_quality(doc_type, ocr_result):
    """Анализирует качество OCR для конкретного типа документа"""
    ocr_upper = ocr_result.upper()
    
    if doc_type == "drivers_license":
        keywords = ["ИВАНОВ", "ИВАН", "ИВАНОВИЧ", "15.03.1985", "77 12 345678", "20.05.2020", "КАТЕГОРИИ"]
        found = sum(1 for kw in keywords if kw in ocr_upper)
        return (found / len(keywords)) * 100
    
    elif doc_type == "passport":
        keywords = ["ПЕТРОВ", "ПЕТР", "ПЕТРОВИЧ", "10.07.1990", "40 17 123456", "15.08.2010", "780-001"]
        found = sum(1 for kw in keywords if kw in ocr_upper)
        return (found / len(keywords)) * 100
    
    elif doc_type == "invoice":
        keywords = ["INV-2026-001", "24.01.2026", "ТЕХКОМПАНИ", "7701234567", "DELL", "140 000"]
        found = sum(1 for kw in keywords if kw in ocr_upper)
        return (found / len(keywords)) * 100
    
    else:
        # Общая оценка по длине результата
        return min(100, len(ocr_result) / 10)

def main():
    """Основная функция тестирования"""
    print("🔬 ПОЛНЫЙ ТЕСТ РАБОЧЕГО ПРОЦЕССА МОДЕЛЕЙ")
    print("=" * 70)
    
    # Проверяем GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ VRAM: {vram_total:.2f}GB")
    else:
        print("❌ GPU недоступна")
        return False
    
    # Создаем тестовые изображения
    print(f"\n📸 СОЗДАНИЕ ТЕСТОВЫХ ДОКУМЕНТОВ...")
    test_images = {
        "drivers_license": create_drivers_license(),
        "passport": create_passport(),
        "invoice": create_invoice()
    }
    print(f"✅ Создано {len(test_images)} тестовых документов")
    
    # Список моделей для тестирования
    models_to_test = ["qwen_vl_2b", "qwen3_vl_2b", "dots_ocr"]
    
    all_results = []
    
    # Тестируем каждую модель
    for model_name in models_to_test:
        try:
            result = test_model_workflow(model_name, test_images)
            all_results.append(result)
            
            # Пауза между моделями
            time.sleep(2)
            
        except Exception as e:
            print(f"\n❌ Критическая ошибка при тестировании {model_name}: {e}")
            all_results.append({
                "model_name": model_name,
                "error": str(e),
                "success": False
            })
    
    # Финальный отчет
    print(f"\n" + "=" * 70)
    print("📊 ФИНАЛЬНЫЙ СРАВНИТЕЛЬНЫЙ ОТЧЕТ")
    print("=" * 70)
    
    successful_models = [r for r in all_results if r.get("success", True) and "error" not in r]
    
    if successful_models:
        print(f"\n🏆 СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ:")
        print(f"{'Модель':<15} | {'Загрузка':<8} | {'OCR':<8} | {'Качество':<8} | {'VRAM':<8} | Flash Attention")
        print("-" * 80)
        
        for result in successful_models:
            model_name = result["model_name"]
            load_time = result.get("load_time", 0)
            avg_ocr = result.get("averages", {}).get("ocr_time", 0)
            avg_quality = result.get("averages", {}).get("quality", 0)
            vram = result.get("vram_usage", 0)
            flash_status = result.get("flash_attention", {})
            flash_enabled = "✅" if flash_status.get("use_flash_attention", False) else "❌"
            
            print(f"{model_name:<15} | {load_time:>6.1f}s | {avg_ocr:>6.1f}s | {avg_quality:>6.0f}% | {vram:>6.1f}GB | {flash_enabled}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    if successful_models:
        # Найдем лучшую модель по общей производительности
        best_model = min(successful_models, 
                        key=lambda x: x.get("averages", {}).get("total_time", float('inf')))
        print(f"🥇 Самая быстрая: {best_model['model_name']}")
        
        # Найдем модель с лучшим качеством
        best_quality = max(successful_models,
                          key=lambda x: x.get("averages", {}).get("quality", 0))
        print(f"🎯 Лучшее качество: {best_quality['model_name']}")
        
        # Проверим Flash Attention
        flash_models = [r for r in successful_models 
                       if r.get("flash_attention", {}).get("use_flash_attention", False)]
        if flash_models:
            print(f"⚡ Flash Attention активен: {', '.join(r['model_name'] for r in flash_models)}")
        else:
            print(f"⚠️ Flash Attention не активен ни в одной модели")
    
    print(f"\n✅ Тестирование завершено!")
    return len(successful_models) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)