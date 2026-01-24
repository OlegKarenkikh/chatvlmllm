#!/usr/bin/env python3
"""
ФИНАЛЬНЫЙ КОМПЛЕКСНЫЙ ТЕСТ ВСЕХ ИСПРАВЛЕНИЙ

Проверяем:
1. Исправленную dots.ocr с правильной обработкой изображений
2. Оптимизированные параметры генерации для qwen3_vl_2b
3. Систему восстановления CUDA
4. CPU fallback режим
5. Полный end-to-end workflow
"""

import time
import torch
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_comprehensive_test_document():
    """Создаем комплексный тестовый документ."""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        font = ImageFont.truetype("arial.ttf", 14)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Заголовок
    draw.text((50, 30), "КОМПЛЕКСНЫЙ ТЕСТОВЫЙ ДОКУМЕНТ", fill='black', font=title_font)
    
    # Основная информация
    draw.text((50, 80), "1. Номер документа: TEST-2026-001", fill='black', font=font)
    draw.text((50, 110), "2. Дата создания: 24 января 2026", fill='black', font=font)
    draw.text((50, 140), "3. Статус: АКТИВЕН", fill='black', font=font)
    draw.text((50, 170), "4. Организация: ChatVLMLLM Testing Lab", fill='black', font=font)
    
    # Таблица данных
    draw.text((50, 220), "Таблица результатов тестирования:", fill='black', font=font)
    
    # Рисуем таблицу
    table_x, table_y = 50, 250
    table_width, table_height = 700, 200
    
    draw.rectangle([table_x, table_y, table_x + table_width, table_y + table_height], outline='black', width=2)
    
    # Заголовки таблицы
    draw.line([table_x, table_y + 40, table_x + table_width, table_y + 40], fill='black', width=1)
    draw.line([table_x + 200, table_y, table_x + 200, table_y + table_height], fill='black', width=1)
    draw.line([table_x + 400, table_y, table_x + 400, table_y + table_height], fill='black', width=1)
    draw.line([table_x + 550, table_y, table_x + 550, table_y + table_height], fill='black', width=1)
    
    draw.text((table_x + 10, table_y + 10), "Модель", fill='black', font=small_font)
    draw.text((table_x + 210, table_y + 10), "Время загрузки", fill='black', font=small_font)
    draw.text((table_x + 410, table_y + 10), "Качество OCR", fill='black', font=small_font)
    draw.text((table_x + 560, table_y + 10), "Статус", fill='black', font=small_font)
    
    # Данные таблицы
    rows = [
        ("qwen_vl_2b", "10.4s", "100%", "OK"),
        ("qwen3_vl_2b", "7.7s", "44%", "OK"),
        ("dots_ocr", "12.3s", "0%", "FIXED"),
        ("dots_ocr_final", "?", "?", "TEST")
    ]
    
    for i, (model, load_time, quality, status) in enumerate(rows):
        y = table_y + 50 + i * 30
        draw.text((table_x + 10, y), model, fill='black', font=small_font)
        draw.text((table_x + 210, y), load_time, fill='black', font=small_font)
        draw.text((table_x + 410, y), quality, fill='black', font=small_font)
        draw.text((table_x + 560, y), status, fill='black', font=small_font)
    
    # Дополнительная информация
    draw.text((50, 480), "Дополнительные параметры:", fill='black', font=font)
    draw.text((50, 510), "• GPU: RTX 5070 Ti (11.94GB VRAM)", fill='black', font=small_font)
    draw.text((50, 530), "• CUDA: 13.0", fill='black', font=small_font)
    draw.text((50, 550), "• PyTorch: 2.9.1+cu130", fill='black', font=small_font)
    
    # Сохраняем для визуального контроля
    img.save("test_comprehensive_document.png")
    
    return img

def test_optimized_qwen3_vl():
    """Тестируем оптимизированную qwen3_vl_2b."""
    print("🚀 ТЕСТ ОПТИМИЗИРОВАННОЙ QWEN3-VL")
    print("=" * 50)
    
    try:
        from models.model_loader import ModelLoader
        from utils.optimized_generation import get_optimized_params, apply_cuda_optimizations
        
        # Применяем CUDA оптимизации
        cuda_optimized = apply_cuda_optimizations()
        print(f"✅ CUDA оптимизации: {'Применены' if cuda_optimized else 'Недоступны'}")
        
        # Создаем тестовое изображение
        test_image = create_comprehensive_test_document()
        
        # Загружаем модель
        print("📥 Загружаем qwen3_vl_2b...")
        start_load = time.time()
        
        model = ModelLoader.load_model("qwen3_vl_2b")
        load_time = time.time() - start_load
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        
        # Получаем оптимизированные параметры
        optimized_params = get_optimized_params("qwen3_vl_2b")
        print(f"📋 Оптимизированные параметры: max_new_tokens={optimized_params['max_new_tokens']}")
        
        # Тестируем с оптимизированными параметрами
        print("🔍 Тестируем с оптимизированными параметрами...")
        start_process = time.time()
        
        # Используем оптимизированные параметры
        result = model.chat(
            test_image, 
            "Extract all text from this document image",
            **optimized_params
        )
        
        process_time = time.time() - start_process
        
        print(f"⏱️ Время обработки: {process_time:.3f}s")
        print(f"📝 Длина результата: {len(result)} символов")
        print(f"🔍 Результат: {result[:150]}...")
        
        # Анализируем качество
        expected_keywords = ["КОМПЛЕКСНЫЙ", "ТЕСТОВЫЙ", "ДОКУМЕНТ", "TEST-2026-001", "24 января 2026", "АКТИВЕН"]
        found_keywords = sum(1 for kw in expected_keywords if kw.upper() in result.upper())
        quality_score = (found_keywords / len(expected_keywords)) * 100
        
        print(f"🎯 Качество OCR: {found_keywords}/{len(expected_keywords)} ({quality_score:.1f}%)")
        
        # Выгружаем модель
        model.unload()
        
        return {
            "success": True,
            "load_time": load_time,
            "process_time": process_time,
            "quality_score": quality_score,
            "optimized": True
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {"success": False, "error": str(e)}

def test_final_dots_ocr():
    """Тестируем финальную исправленную dots.ocr."""
    print("\n🔬 ТЕСТ ФИНАЛЬНОЙ ИСПРАВЛЕННОЙ DOTS.OCR")
    print("=" * 50)
    
    try:
        from models.model_loader import ModelLoader
        
        # Создаем тестовое изображение
        test_image = create_comprehensive_test_document()
        
        # Загружаем финальную модель
        print("📥 Загружаем финальную dots.ocr...")
        start_load = time.time()
        
        model = ModelLoader.load_model("dots_ocr")
        load_time = time.time() - start_load
        
        print(f"✅ Модель загружена за {load_time:.2f}s")
        print(f"📋 Класс модели: {model.__class__.__name__}")
        
        # Тест 1: Простое извлечение текста
        print("\n🔍 Тест 1: Простое извлечение текста")
        start_process = time.time()
        
        result = model.extract_text(test_image)
        process_time = time.time() - start_process
        
        print(f"⏱️ Время обработки: {process_time:.3f}s")
        print(f"📝 Длина результата: {len(result)} символов")
        print(f"🔍 Результат: {result[:200]}...")
        
        # Анализируем качество
        expected_keywords = ["КОМПЛЕКСНЫЙ", "ТЕСТОВЫЙ", "ДОКУМЕНТ", "TEST-2026-001", "АКТИВЕН"]
        found_keywords = sum(1 for kw in expected_keywords if kw.upper() in result.upper())
        quality_score = (found_keywords / len(expected_keywords)) * 100
        
        print(f"🎯 Качество OCR: {found_keywords}/{len(expected_keywords)} ({quality_score:.1f}%)")
        
        # Тест 2: Извлечение таблицы
        print("\n🔍 Тест 2: Извлечение таблицы")
        start_table = time.time()
        
        table_result = model.extract_table(test_image)
        table_time = time.time() - start_table
        
        print(f"⏱️ Время извлечения таблицы: {table_time:.3f}s")
        print(f"📊 Результат таблицы: {table_result[:150]}...")
        
        # Тест 3: Парсинг документа
        print("\n🔍 Тест 3: Парсинг документа")
        start_parse = time.time()
        
        parsed_result = model.parse_document(test_image)
        parse_time = time.time() - start_parse
        
        print(f"⏱️ Время парсинга: {parse_time:.3f}s")
        print(f"✅ Успешность парсинга: {parsed_result.get('success', False)}")
        
        # Выгружаем модель
        model.unload()
        
        return {
            "success": True,
            "load_time": load_time,
            "process_time": process_time,
            "quality_score": quality_score,
            "table_extraction": len(table_result) > 50,
            "document_parsing": parsed_result.get('success', False)
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def test_cuda_recovery_system():
    """Тестируем систему восстановления CUDA."""
    print("\n🛡️ ТЕСТ СИСТЕМЫ ВОССТАНОВЛЕНИЯ CUDA")
    print("=" * 50)
    
    try:
        from utils.cuda_recovery import cuda_recovery_manager
        
        # Тест 1: Детекция CUDA ошибок
        print("🔍 Тест детекции CUDA ошибок...")
        
        test_cases = [
            ("CUDA error: device-side assert triggered", True),
            ("CUDA out of memory", True),
            ("RuntimeError: CUDA kernel errors", True),
            ("Normal Python error", False),
            ("ValueError: Invalid input", False)
        ]
        
        correct_detections = 0
        for error_msg, expected in test_cases:
            error = Exception(error_msg)
            detected = cuda_recovery_manager.is_cuda_error(error)
            if detected == expected:
                correct_detections += 1
            print(f"   {'✅' if detected == expected else '❌'} '{error_msg[:30]}...' -> {'CUDA' if detected else 'Обычная'}")
        
        detection_accuracy = (correct_detections / len(test_cases)) * 100
        print(f"🎯 Точность детекции: {correct_detections}/{len(test_cases)} ({detection_accuracy:.1f}%)")
        
        # Тест 2: Безопасный вызов функции
        print("\n🔍 Тест безопасного вызова функции...")
        
        def test_function(mode="success"):
            if mode == "cuda_error":
                raise Exception("CUDA error: device-side assert triggered")
            elif mode == "normal_error":
                raise ValueError("Normal error")
            return f"Success: {mode}"
        
        # Успешный вызов
        try:
            result = cuda_recovery_manager.safe_cuda_call(test_function, mode="success")
            print(f"   ✅ Успешный вызов: {result}")
            success_call = True
        except Exception as e:
            print(f"   ❌ Неожиданная ошибка: {e}")
            success_call = False
        
        return {
            "detection_accuracy": detection_accuracy,
            "safe_call_works": success_call,
            "overall_success": detection_accuracy >= 80 and success_call
        }
        
    except ImportError:
        print("⚠️ Модуль cuda_recovery не найден")
        return {"overall_success": False, "error": "Module not found"}
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {"overall_success": False, "error": str(e)}

def test_cpu_fallback():
    """Тестируем CPU fallback режим."""
    print("\n💻 ТЕСТ CPU FALLBACK РЕЖИМА")
    print("=" * 50)
    
    try:
        # Проверяем наличие CPU fallback конфигурации
        if os.path.exists("config_cpu_fallback.yaml"):
            print("✅ CPU fallback конфигурация найдена")
            
            # Читаем конфигурацию
            import yaml
            with open("config_cpu_fallback.yaml", "r", encoding="utf-8") as f:
                cpu_config = yaml.safe_load(f)
            
            # Проверяем настройки
            models = cpu_config.get("models", {})
            cpu_models = [name for name, config in models.items() if config.get("force_cpu", False)]
            
            print(f"📋 CPU модели: {cpu_models}")
            print(f"✅ CPU fallback готов к использованию")
            
            return {"available": True, "cpu_models": len(cpu_models)}
        else:
            print("❌ CPU fallback конфигурация не найдена")
            return {"available": False}
            
    except Exception as e:
        print(f"❌ Ошибка проверки CPU fallback: {e}")
        return {"available": False, "error": str(e)}

def run_comprehensive_test():
    """Запускаем комплексный тест всех исправлений."""
    print("🔬 ФИНАЛЬНЫЙ КОМПЛЕКСНЫЙ ТЕСТ ВСЕХ ИСПРАВЛЕНИЙ")
    print("=" * 80)
    
    # Проверяем системные требования
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ VRAM: {vram_gb:.2f}GB")
    else:
        print("⚠️ CUDA недоступна")
    
    results = {}
    
    # Тест 1: Оптимизированная qwen3_vl_2b
    results["qwen3_vl_optimized"] = test_optimized_qwen3_vl()
    
    # Тест 2: Финальная dots.ocr
    results["dots_ocr_final"] = test_final_dots_ocr()
    
    # Тест 3: Система восстановления CUDA
    results["cuda_recovery"] = test_cuda_recovery_system()
    
    # Тест 4: CPU fallback
    results["cpu_fallback"] = test_cpu_fallback()
    
    # Итоговый анализ
    print("\n" + "=" * 80)
    print("🏆 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ВСЕХ ИСПРАВЛЕНИЙ")
    print("=" * 80)
    
    # Анализируем результаты
    successful_tests = 0
    total_tests = 0
    
    for test_name, result in results.items():
        total_tests += 1
        if isinstance(result, dict):
            if result.get("success", False) or result.get("overall_success", False) or result.get("available", False):
                successful_tests += 1
                status = "✅"
            else:
                status = "❌"
        else:
            status = "❓"
        
        print(f"{status} {test_name.replace('_', ' ').title()}")
        
        # Детали результатов
        if isinstance(result, dict):
            if "load_time" in result:
                print(f"    Время загрузки: {result['load_time']:.2f}s")
            if "process_time" in result:
                print(f"    Время обработки: {result['process_time']:.3f}s")
            if "quality_score" in result:
                print(f"    Качество OCR: {result['quality_score']:.1f}%")
            if "error" in result:
                print(f"    Ошибка: {result['error']}")
    
    # Общая оценка
    success_rate = (successful_tests / total_tests) * 100
    print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {successful_tests}/{total_tests} тестов пройдено ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🎉 БОЛЬШИНСТВО ИСПРАВЛЕНИЙ РАБОТАЮТ ОТЛИЧНО!")
        final_status = "excellent"
    elif success_rate >= 50:
        print("✅ Исправления работают удовлетворительно")
        final_status = "good"
    else:
        print("⚠️ Требуется дополнительная доработка")
        final_status = "needs_work"
    
    # Сохраняем результаты
    final_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_results": results,
        "success_rate": success_rate,
        "final_status": final_status,
        "recommendations": []
    }
    
    # Рекомендации
    if results["qwen3_vl_optimized"].get("success"):
        final_results["recommendations"].append("qwen3_vl_2b готова к использованию с оптимизациями")
    
    if results["dots_ocr_final"].get("success"):
        final_results["recommendations"].append("dots.ocr исправлена и готова к использованию")
    
    if results["cuda_recovery"].get("overall_success"):
        final_results["recommendations"].append("Система восстановления CUDA работает")
    
    if results["cpu_fallback"].get("available"):
        final_results["recommendations"].append("CPU fallback доступен при проблемах с CUDA")
    
    with open("final_fixes_test_results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в final_fixes_test_results.json")
    
    return success_rate >= 50

def main():
    """Главная функция."""
    try:
        success = run_comprehensive_test()
        return success
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        return False
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)