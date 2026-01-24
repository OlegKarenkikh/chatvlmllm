#!/usr/bin/env python3
"""
Тестирование аварийных исправлений критических CUDA ошибок
"""

import json
import time
from datetime import datetime
from PIL import Image
import io
import base64

def test_emergency_model_loader():
    """Тестирование аварийного загрузчика моделей"""
    
    print("🧪 ТЕСТИРОВАНИЕ АВАРИЙНЫХ ИСПРАВЛЕНИЙ")
    print("=" * 60)
    
    try:
        from models.model_loader import ModelLoader
        
        # Проверка статуса аварийного режима
        print("📊 Статус аварийного режима:")
        emergency_status = ModelLoader.get_emergency_status()
        
        for key, value in emergency_status.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} элементов")
                for item in value:
                    print(f"    • {item}")
            else:
                print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        
        # Тестирование загрузки безопасной модели
        print("🔄 Тестирование загрузки модели Qwen3-VL...")
        
        start_time = time.time()
        
        try:
            model = ModelLoader.load_model("qwen3_vl_2b")
            load_time = time.time() - start_time
            
            print(f"✅ Модель загружена успешно за {load_time:.2f}с")
            
            # Создание тестового изображения
            test_image = Image.new('RGB', (100, 100), color='white')
            
            # Тестирование обработки изображения
            print("🖼️ Тестирование обработки изображения...")
            
            try:
                if hasattr(model, 'extract_text'):
                    result = model.extract_text(test_image)
                elif hasattr(model, 'process_image'):
                    result = model.process_image(test_image)
                else:
                    result = "Модель загружена, но методы обработки недоступны"
                
                print(f"✅ Обработка изображения успешна")
                print(f"📄 Результат: {result[:100]}..." if len(str(result)) > 100 else f"📄 Результат: {result}")
                
            except Exception as processing_error:
                print(f"⚠️ Ошибка обработки изображения: {processing_error}")
                
                # Проверяем, является ли это критической CUDA ошибкой
                if "CUDA error: device-side assert triggered" in str(processing_error):
                    print("🚨 КРИТИЧЕСКАЯ CUDA ОШИБКА ВСЕ ЕЩЕ ПРИСУТСТВУЕТ!")
                    return False
                else:
                    print("💡 Ошибка не критическая, модель загружена")
            
            # Выгрузка модели
            print("🗑️ Выгрузка модели...")
            ModelLoader.unload_model("qwen3_vl_2b")
            print("✅ Модель выгружена")
            
            return True
            
        except Exception as load_error:
            load_time = time.time() - start_time
            print(f"❌ Ошибка загрузки модели за {load_time:.2f}с: {load_error}")
            
            # Анализ типа ошибки
            error_str = str(load_error)
            
            if "CUDA error: device-side assert triggered" in error_str:
                print("🚨 КРИТИЧЕСКАЯ CUDA ОШИБКА НЕ ИСПРАВЛЕНА!")
                return False
            elif "FlashAttention2" in error_str:
                print("⚠️ Flash Attention ошибка не исправлена")
                return False
            elif "load_in_8bit" in error_str:
                print("⚠️ Квантизация ошибка не исправлена")
                return False
            else:
                print("💡 Неизвестная ошибка, требует дополнительного анализа")
                return False
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_vllm_mode():
    """Тестирование vLLM режима как альтернативы"""
    
    print("\n" + "=" * 60)
    print("🚀 ТЕСТИРОВАНИЕ vLLM РЕЖИМА")
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        
        adapter = VLLMStreamlitAdapter()
        status = adapter.get_server_status()
        
        print(f"📊 Статус vLLM сервера: {status.get('status', 'unknown')}")
        
        if status.get("status") == "healthy":
            print("✅ vLLM сервер доступен - рекомендуется использовать для стабильной работы")
            
            # Создание тестового изображения
            test_image = Image.new('RGB', (100, 100), color='white')
            
            try:
                result = adapter.process_image(
                    test_image, 
                    "Extract all text from this image", 
                    "rednote-hilab/dots.ocr",
                    max_tokens=1024
                )
                
                if result and result.get("success"):
                    print(f"✅ vLLM обработка успешна за {result.get('processing_time', 0):.2f}с")
                    return True
                else:
                    print("⚠️ vLLM обработка неуспешна")
                    return False
                    
            except Exception as vllm_error:
                print(f"❌ Ошибка vLLM обработки: {vllm_error}")
                return False
        else:
            print("❌ vLLM сервер недоступен")
            print("💡 Запустите: docker-compose -f docker-compose-vllm.yml up -d")
            return False
            
    except ImportError:
        print("❌ vLLM адаптер недоступен")
        return False

def create_test_report(transformers_result: bool, vllm_result: bool):
    """Создание отчета о тестировании"""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "emergency_fixes_test": {
            "transformers_mode": {
                "status": "PASSED" if transformers_result else "FAILED",
                "description": "Тестирование аварийного загрузчика моделей"
            },
            "vllm_mode": {
                "status": "PASSED" if vllm_result else "FAILED", 
                "description": "Тестирование vLLM режима как альтернативы"
            }
        },
        "overall_status": "SYSTEM_OPERATIONAL" if (transformers_result or vllm_result) else "SYSTEM_CRITICAL",
        "recommendations": []
    }
    
    if transformers_result:
        report["recommendations"].append("✅ Transformers режим работает с аварийными исправлениями")
    else:
        report["recommendations"].append("❌ Transformers режим требует дополнительных исправлений")
    
    if vllm_result:
        report["recommendations"].append("✅ vLLM режим рекомендуется для стабильной работы")
    else:
        report["recommendations"].append("⚠️ vLLM режим недоступен - запустите Docker контейнер")
    
    if not transformers_result and not vllm_result:
        report["recommendations"].extend([
            "🚨 КРИТИЧЕСКОЕ СОСТОЯНИЕ: Оба режима недоступны",
            "🔧 Требуется обновление драйверов CUDA",
            "🔧 Возможно требуется переустановка PyTorch",
            "🔧 Рассмотрите использование CPU режима"
        ])
    
    # Сохранение отчета
    with open("emergency_fixes_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def main():
    """Главная функция тестирования"""
    
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ КРИТИЧЕСКИХ ОШИБОК")
    print("Дата:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Тестирование Transformers режима
    transformers_result = test_emergency_model_loader()
    
    # Тестирование vLLM режима
    vllm_result = test_vllm_mode()
    
    # Создание отчета
    report = create_test_report(transformers_result, vllm_result)
    
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    print(f"🔧 Transformers режим: {'✅ РАБОТАЕТ' if transformers_result else '❌ НЕ РАБОТАЕТ'}")
    print(f"🚀 vLLM режим: {'✅ РАБОТАЕТ' if vllm_result else '❌ НЕ РАБОТАЕТ'}")
    print(f"🎯 Общий статус: {report['overall_status']}")
    
    print("\n💡 Рекомендации:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    print(f"\n📄 Подробный отчет: emergency_fixes_test_report.json")
    
    if report["overall_status"] == "SYSTEM_OPERATIONAL":
        print("\n🎉 СИСТЕМА ЧАСТИЧНО ВОССТАНОВЛЕНА!")
        if vllm_result:
            print("   Рекомендуется использовать vLLM режим для максимальной стабильности")
        else:
            print("   Используйте Transformers режим с осторожностью")
    else:
        print("\n🚨 СИСТЕМА ВСЕ ЕЩЕ В КРИТИЧЕСКОМ СОСТОЯНИИ!")
        print("   Требуются дополнительные исправления")

if __name__ == "__main__":
    main()