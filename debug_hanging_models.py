#!/usr/bin/env python3
"""
Диагностика зависания моделей
Проверяем каждый этап загрузки и обработки
"""

import time
import signal
import sys
import torch
from PIL import Image
from models.model_loader import ModelLoader
from utils.logger import logger

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Операция превысила таймаут")

def test_with_timeout(func, timeout_seconds=60):
    """Выполняет функцию с таймаутом"""
    # Устанавливаем обработчик сигнала
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = func()
        signal.alarm(0)  # Отменяем таймаут
        return result, None
    except TimeoutError as e:
        return None, f"ТАЙМАУТ ({timeout_seconds}s)"
    except Exception as e:
        signal.alarm(0)
        return None, f"ОШИБКА: {e}"

def diagnose_model_loading(model_key):
    """Диагностика загрузки модели по этапам"""
    print(f"\n🔍 ДИАГНОСТИКА МОДЕЛИ: {model_key}")
    print("-" * 50)
    
    # Этап 1: Проверка конфигурации
    print("1️⃣ Проверка конфигурации...")
    try:
        config = ModelLoader.load_config()
        if model_key in config["models"]:
            model_config = config["models"][model_key]
            print(f"   ✅ Конфигурация найдена: {model_config.get('model_path')}")
        else:
            print(f"   ❌ Модель не найдена в конфигурации")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка конфигурации: {e}")
        return False
    
    # Этап 2: Проверка кеша
    print("2️⃣ Проверка кеша...")
    try:
        is_cached, cache_msg = ModelLoader.check_model_cache(model_key)
        print(f"   {'✅' if is_cached else '⚠️'} {cache_msg}")
    except Exception as e:
        print(f"   ❌ Ошибка проверки кеша: {e}")
    
    # Этап 3: Инициализация модели (с таймаутом)
    print("3️⃣ Инициализация модели...")
    
    def init_model():
        return ModelLoader.load_model(model_key)
    
    model, error = test_with_timeout(init_model, timeout_seconds=120)
    
    if error:
        print(f"   ❌ {error}")
        return False
    elif model:
        print(f"   ✅ Модель инициализирована: {type(model).__name__}")
    else:
        print(f"   ❌ Неизвестная ошибка инициализации")
        return False
    
    # Этап 4: Создание тестового изображения
    print("4️⃣ Создание тестового изображения...")
    try:
        test_image = Image.new('RGB', (100, 100), color='white')
        print(f"   ✅ Изображение создано: {test_image.size}")
    except Exception as e:
        print(f"   ❌ Ошибка создания изображения: {e}")
        model.unload()
        return False
    
    # Этап 5: Обработка изображения (с таймаутом)
    print("5️⃣ Обработка изображения...")
    
    def process_image():
        if hasattr(model, 'process_image'):
            return model.process_image(test_image)
        elif hasattr(model, 'chat'):
            return model.chat(test_image, "Что на изображении?")
        else:
            return "Метод обработки не найден"
    
    result, error = test_with_timeout(process_image, timeout_seconds=60)
    
    if error:
        print(f"   ❌ {error}")
    elif result:
        print(f"   ✅ Обработка завершена: {len(str(result))} символов")
        print(f"   📄 Результат: {str(result)[:50]}...")
    else:
        print(f"   ❌ Пустой результат")
    
    # Этап 6: Выгрузка модели
    print("6️⃣ Выгрузка модели...")
    try:
        model.unload()
        print(f"   ✅ Модель выгружена")
    except Exception as e:
        print(f"   ⚠️ Ошибка выгрузки: {e}")
    
    return result is not None and error is None

def main():
    """Основная функция диагностики"""
    print("🔧 ДИАГНОСТИКА ЗАВИСАНИЯ МОДЕЛЕЙ")
    print("=" * 60)
    
    # Проверяем GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"🖥️ GPU: {gpu_name}")
        print(f"💾 VRAM: {vram_gb:.2f}GB")
    else:
        print("❌ CUDA недоступна!")
    
    # Список моделей для тестирования (от простых к сложным)
    models_to_test = [
        "qwen_vl_2b",      # Простая и быстрая
        "got_ocr_hf",      # OCR модель
        "qwen3_vl_2b",     # Более сложная
    ]
    
    print(f"\n📋 Тестируем {len(models_to_test)} моделей:")
    for model in models_to_test:
        print(f"  • {model}")
    
    successful = []
    failed = []
    
    for model_key in models_to_test:
        try:
            success = diagnose_model_loading(model_key)
            if success:
                successful.append(model_key)
            else:
                failed.append(model_key)
        except KeyboardInterrupt:
            print(f"\n⚠️ Прервано пользователем на модели {model_key}")
            break
        except Exception as e:
            print(f"\n❌ Критическая ошибка на модели {model_key}: {e}")
            failed.append(model_key)
        
        # Очистка GPU памяти между тестами
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print(f"🧹 GPU память очищена")
    
    # Итоговые результаты
    print(f"\n📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
    print("=" * 60)
    print(f"✅ Успешно: {len(successful)}")
    print(f"❌ Неудачно: {len(failed)}")
    
    if successful:
        print(f"\n✅ РАБОЧИЕ МОДЕЛИ:")
        for model in successful:
            print(f"   • {model}")
    
    if failed:
        print(f"\n❌ ПРОБЛЕМНЫЕ МОДЕЛИ:")
        for model in failed:
            print(f"   • {model}")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    if len(failed) > len(successful):
        print("   🔧 Большинство моделей не работает - проверьте:")
        print("      - Версии transformers и torch")
        print("      - Доступность GPU")
        print("      - Свободную VRAM")
    elif failed:
        print("   ⚠️ Некоторые модели не работают - возможные причины:")
        print("      - Недостаток VRAM для тяжелых моделей")
        print("      - Проблемы с конкретными реализациями")
    else:
        print("   🎉 Все модели работают корректно!")
    
    return len(successful) > 0

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Диагностика прервана пользователем")
        exit(1)