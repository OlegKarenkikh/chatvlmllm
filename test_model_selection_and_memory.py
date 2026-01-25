#!/usr/bin/env python3
"""
Тест корректности выбора модели и управления памятью vLLM контейнеров
"""

import time
import json
from PIL import Image, ImageDraw, ImageFont
from vllm_memory_manager import VLLMMemoryManager
from vllm_streamlit_adapter import VLLMStreamlitAdapter

def create_test_image():
    """Создание тестового изображения"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Model Selection Test", fill='black', font=font)
    draw.text((50, 100), "dots.ocr vs Qwen3-VL", fill='blue', font=font)
    draw.text((50, 150), "Memory Management", fill='red', font=font)
    draw.text((50, 200), "GPU Optimization", fill='green', font=font)
    
    return img

def test_model_selection_and_memory():
    """Тестирование выбора модели и управления памятью"""
    
    print("🧪 Тестирование выбора модели и управления памятью")
    print("=" * 60)
    
    # Инициализация компонентов
    memory_manager = VLLMMemoryManager()
    adapter = VLLMStreamlitAdapter()
    
    # Создание тестового изображения
    test_image = create_test_image()
    test_image.save("test_model_selection.png")
    print("✅ Тестовое изображение создано")
    
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "model_selection_and_memory",
        "memory_tests": {},
        "model_tests": {},
        "recommendations": []
    }
    
    # 1. Тест статуса памяти
    print("\n1️⃣ Анализ использования памяти:")
    print("-" * 40)
    
    memory_status = memory_manager.get_memory_status()
    
    print(f"Активных контейнеров: {memory_status['running_containers']}")
    print(f"Использование GPU: {memory_status['current_memory_gb']:.1f}/{memory_status['max_memory_gb']} ГБ")
    print(f"Процент использования: {memory_status['memory_usage_percent']:.1f}%")
    print(f"Доступно памяти: {memory_status['available_memory_gb']:.1f} ГБ")
    
    results["memory_tests"]["initial_status"] = memory_status
    
    # Проверка лимитов памяти
    if memory_status['memory_usage_percent'] > 100:
        print("❌ КРИТИЧНО: Превышен лимит GPU памяти!")
        results["recommendations"].append("Критично: Превышен лимит GPU памяти - требуется оптимизация")
    elif memory_status['memory_usage_percent'] > 90:
        print("⚠️ ПРЕДУПРЕЖДЕНИЕ: Высокое использование GPU памяти")
        results["recommendations"].append("Предупреждение: Высокое использование GPU памяти")
    else:
        print("✅ Использование GPU памяти в норме")
    
    # 2. Тест доступных моделей
    print("\n2️⃣ Анализ доступных моделей:")
    print("-" * 40)
    
    available_models = adapter.get_recommended_models()
    
    for i, model in enumerate(available_models, 1):
        model_name = model.split('/')[-1]
        is_active = model in adapter.healthy_endpoints
        endpoint = adapter.model_endpoints.get(model, "unknown")
        
        status_icon = "✅" if is_active else "❌"
        print(f"{i}. {status_icon} {model_name} ({endpoint})")
        
        results["model_tests"][model] = {
            "available": is_active,
            "endpoint": endpoint,
            "priority": i
        }
    
    if not available_models:
        print("❌ Нет доступных моделей!")
        results["recommendations"].append("Критично: Нет доступных моделей")
        return results
    
    # 3. Тест переключения между моделями
    print("\n3️⃣ Тест переключения между моделями:")
    print("-" * 40)
    
    test_models = [
        "rednote-hilab/dots.ocr",
        "Qwen/Qwen3-VL-2B-Instruct"
    ]
    
    model_performance = {}
    
    for model in test_models:
        if model not in adapter.model_endpoints:
            continue
            
        print(f"\n🔄 Тестирование модели: {model.split('/')[-1]}")
        
        # Проверяем доступность модели
        start_time = time.time()
        is_available = adapter.ensure_model_available(model)
        switch_time = time.time() - start_time
        
        if not is_available:
            print(f"❌ Модель {model.split('/')[-1]} недоступна")
            model_performance[model] = {
                "available": False,
                "switch_time": switch_time,
                "error": "Model not available"
            }
            continue
        
        print(f"✅ Модель активна (время переключения: {switch_time:.1f}с)")
        
        # Тестируем OCR
        try:
            ocr_start = time.time()
            result = adapter.process_image(
                test_image, 
                "Extract all text from this image", 
                model,
                max_tokens=512
            )
            ocr_time = time.time() - ocr_start
            
            if result and result.get("success"):
                print(f"✅ OCR успешно: {len(result['text'])} символов за {ocr_time:.1f}с")
                print(f"   Результат: {result['text'][:50]}...")
                
                model_performance[model] = {
                    "available": True,
                    "switch_time": switch_time,
                    "ocr_time": ocr_time,
                    "text_length": len(result['text']),
                    "tokens_used": result.get('tokens_used', 0),
                    "success": True
                }
            else:
                print(f"❌ OCR неуспешно")
                model_performance[model] = {
                    "available": True,
                    "switch_time": switch_time,
                    "ocr_time": ocr_time,
                    "success": False,
                    "error": result.get('error', 'Unknown error') if result else 'No result'
                }
                
        except Exception as e:
            print(f"❌ Ошибка OCR: {e}")
            model_performance[model] = {
                "available": True,
                "switch_time": switch_time,
                "success": False,
                "error": str(e)
            }
        
        # Проверяем статус памяти после теста
        memory_after = memory_manager.get_memory_status()
        print(f"   Память после теста: {memory_after['current_memory_gb']:.1f} ГБ")
        
        time.sleep(2)  # Пауза между тестами
    
    results["model_tests"]["performance"] = model_performance
    
    # 4. Тест оптимизации памяти
    print("\n4️⃣ Тест оптимизации памяти:")
    print("-" * 40)
    
    memory_before = memory_manager.get_memory_status()
    print(f"Память до оптимизации: {memory_before['current_memory_gb']:.1f} ГБ")
    
    if memory_before['memory_usage_percent'] > 75:
        print("🔧 Запуск оптимизации памяти...")
        success, message = memory_manager.optimize_memory_usage()
        
        if success:
            print(f"✅ Оптимизация успешна: {message}")
            
            memory_after = memory_manager.get_memory_status()
            print(f"Память после оптимизации: {memory_after['current_memory_gb']:.1f} ГБ")
            
            results["memory_tests"]["optimization"] = {
                "performed": True,
                "success": True,
                "message": message,
                "memory_before": memory_before['current_memory_gb'],
                "memory_after": memory_after['current_memory_gb'],
                "memory_saved": memory_before['current_memory_gb'] - memory_after['current_memory_gb']
            }
        else:
            print(f"❌ Ошибка оптимизации: {message}")
            results["memory_tests"]["optimization"] = {
                "performed": True,
                "success": False,
                "message": message
            }
    else:
        print("✅ Оптимизация не требуется - память в норме")
        results["memory_tests"]["optimization"] = {
            "performed": False,
            "reason": "Memory usage below threshold"
        }
    
    # 5. Финальные рекомендации
    print("\n5️⃣ Рекомендации:")
    print("-" * 40)
    
    # Анализ производительности моделей
    successful_models = [model for model, perf in model_performance.items() if perf.get("success")]
    
    if successful_models:
        print("✅ Работающие модели:")
        for model in successful_models:
            perf = model_performance[model]
            model_name = model.split('/')[-1]
            print(f"   - {model_name}: OCR {perf['ocr_time']:.1f}с, переключение {perf['switch_time']:.1f}с")
        
        # Рекомендация лучшей модели
        best_model = min(successful_models, key=lambda x: model_performance[x]['ocr_time'])
        best_name = best_model.split('/')[-1]
        print(f"🏆 Рекомендуемая модель: {best_name} (самая быстрая)")
        results["recommendations"].append(f"Рекомендуемая модель: {best_name}")
    else:
        print("❌ Нет работающих моделей!")
        results["recommendations"].append("Критично: Нет работающих моделей")
    
    # Рекомендации по памяти
    final_memory = memory_manager.get_memory_status()
    
    if final_memory['memory_usage_percent'] <= 75:
        print("✅ Память оптимизирована - можно запускать несколько моделей")
        results["recommendations"].append("Память оптимизирована - можно запускать несколько моделей")
    elif final_memory['memory_usage_percent'] <= 90:
        print("⚠️ Рекомендуется использовать одну модель за раз")
        results["recommendations"].append("Рекомендуется использовать одну модель за раз")
    else:
        print("❌ Требуется оптимизация - высокое потребление памяти")
        results["recommendations"].append("Требуется оптимизация - высокое потребление памяти")
    
    # 6. Сохранение результатов
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = f"model_selection_memory_test_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены: {results_file}")
    
    # 7. Итоговый статус
    print(f"\n📊 ИТОГОВЫЙ СТАТУС:")
    print("=" * 60)
    
    working_models = len(successful_models)
    total_models = len(test_models)
    memory_ok = final_memory['memory_usage_percent'] <= 90
    
    if working_models > 0 and memory_ok:
        print("🎉 СИСТЕМА ГОТОВА К РАБОТЕ")
        print(f"   ✅ Работающих моделей: {working_models}/{total_models}")
        print(f"   ✅ Память в норме: {final_memory['current_memory_gb']:.1f}/{final_memory['max_memory_gb']} ГБ")
        print("   💡 Можно запускать приложение: streamlit run app.py")
    else:
        print("⚠️ ТРЕБУЕТСЯ НАСТРОЙКА")
        if working_models == 0:
            print("   ❌ Нет работающих моделей")
        if not memory_ok:
            print("   ❌ Проблемы с памятью")
        print("   💡 Проверьте контейнеры и настройки памяти")
    
    return results

if __name__ == "__main__":
    test_model_selection_and_memory()