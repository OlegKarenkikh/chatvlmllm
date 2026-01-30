#!/usr/bin/env python3
"""
Тест исправления vLLM чата - проверяем, что модель правильно определяется
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vllm_streamlit_adapter import VLLMStreamlitAdapter
from single_container_manager import SingleContainerManager
from PIL import Image
import io
import base64

def test_vllm_chat_fix():
    print("🧪 Тестирование исправления vLLM чата...")
    
    # Инициализация компонентов
    adapter = VLLMStreamlitAdapter()
    container_manager = SingleContainerManager()
    
    print("\n📋 Статус системы:")
    print(f"Активная модель: {container_manager.get_active_model()}")
    print(f"Доступные модели: {adapter.available_models}")
    
    # Проверяем активную модель
    active_model_key = container_manager.get_active_model()
    if not active_model_key:
        print("❌ Нет активной модели")
        return False
    
    active_config = container_manager.models_config[active_model_key]
    vllm_model = active_config["model_path"]
    
    print(f"\n🔍 Активная модель:")
    print(f"  Ключ: {active_model_key}")
    print(f"  Путь модели: {vllm_model}")
    print(f"  Порт: {active_config['port']}")
    print(f"  Отображаемое имя: {active_config['display_name']}")
    
    # Тестируем получение лимита токенов
    model_max_tokens = adapter.get_model_max_tokens(vllm_model)
    print(f"  Лимит токенов: {model_max_tokens}")
    
    # Создаем тестовое изображение
    test_image = Image.new('RGB', (100, 100), color='white')
    
    print(f"\n🚀 Тестирование обработки изображения...")
    print(f"Используемая модель: {vllm_model}")
    
    # Тестируем обработку
    result = adapter.process_image(
        test_image, 
        "Extract text from this image", 
        vllm_model, 
        512
    )
    
    if result:
        print(f"\n📊 Результат:")
        print(f"  Успех: {result.get('success', False)}")
        print(f"  Время обработки: {result.get('processing_time', 0):.2f}с")
        if result.get('success'):
            print(f"  Текст: {result.get('text', '')[:100]}...")
        else:
            print(f"  Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    else:
        print("❌ Нет результата")
        return False
    
    return result.get('success', False)

if __name__ == "__main__":
    success = test_vllm_chat_fix()
    if success:
        print("\n✅ Тест пройден! vLLM чат должен работать корректно.")
    else:
        print("\n❌ Тест не пройден. Требуется дополнительная диагностика.")