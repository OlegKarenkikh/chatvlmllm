#!/usr/bin/env python3
"""
Быстрый тест системы после исправления критических ошибок
"""

import time
from PIL import Image

def quick_test():
    """Быстрый тест основных функций"""
    
    print("🚀 БЫСТРЫЙ ТЕСТ СИСТЕМЫ")
    print("=" * 40)
    
    try:
        # Тест 1: Импорт загрузчика
        print("1️⃣ Тестирование импорта...")
        from models.model_loader import ModelLoader
        print("   ✅ Загрузчик импортирован")
        
        # Тест 2: Проверка аварийного режима
        print("2️⃣ Проверка аварийного режима...")
        status = ModelLoader.get_emergency_status()
        print(f"   ✅ Аварийный режим: {status['emergency_mode']}")
        print(f"   ✅ CUDA доступен: {status['cuda_available']}")
        print(f"   ✅ VRAM доступно: {status['available_vram_gb']:.1f}GB")
        
        # Тест 3: Быстрая загрузка модели
        print("3️⃣ Быстрая загрузка модели...")
        start_time = time.time()
        
        model = ModelLoader.load_model("qwen3_vl_2b")
        load_time = time.time() - start_time
        
        print(f"   ✅ Модель загружена за {load_time:.1f}с")
        
        # Тест 4: Быстрая обработка
        print("4️⃣ Тестирование обработки...")
        test_image = Image.new('RGB', (50, 50), color='red')
        
        start_time = time.time()
        result = model.extract_text(test_image)
        process_time = time.time() - start_time
        
        print(f"   ✅ Обработка за {process_time:.1f}с")
        print(f"   📄 Результат: {str(result)[:50]}...")
        
        # Тест 5: Выгрузка
        print("5️⃣ Выгрузка модели...")
        ModelLoader.unload_model("qwen3_vl_2b")
        print("   ✅ Модель выгружена")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Система работает корректно")
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТЕ: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n💡 Система готова к использованию!")
        print("   Запустите: streamlit run app.py")
    else:
        print("\n⚠️ Требуются дополнительные исправления")