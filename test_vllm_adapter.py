#!/usr/bin/env python3
"""
Тест vLLM адаптера для диагностики проблемы с Qwen3-VL
"""

from vllm_streamlit_adapter import VLLMStreamlitAdapter
from PIL import Image
import io
import base64

def test_adapter():
    print("🧪 ТЕСТ vLLM АДАПТЕРА")
    print("=" * 30)
    
    # Создаем адаптер
    adapter = VLLMStreamlitAdapter()
    
    # Проверяем подключение
    print(f"\n📊 СТАТУС ПОДКЛЮЧЕНИЯ:")
    status = adapter.get_server_status()
    print(f"Статус: {status['status']}")
    print(f"Доступных моделей: {len(status['available_models'])}")
    print(f"Активных endpoints: {len(status.get('endpoints', {}))}")
    
    for model in status['available_models']:
        print(f"  • {model}")
    
    # Проверяем endpoints
    print(f"\n🌐 ENDPOINTS:")
    for model, endpoint in status.get('endpoints', {}).items():
        print(f"  {model} → {endpoint}")
    
    # Тестируем обработку изображения
    if status['available_models']:
        print(f"\n🖼️ ТЕСТ ОБРАБОТКИ ИЗОБРАЖЕНИЯ:")
        
        # Создаем простое тестовое изображение
        test_image = Image.new('RGB', (100, 50), color='white')
        
        model = status['available_models'][0]
        print(f"Используем модель: {model}")
        
        result = adapter.process_image(
            image=test_image,
            prompt="What do you see in this image?",
            model=model,
            max_tokens=100
        )
        
        print(f"Результат: {result}")
        
        if result and result.get('success'):
            print("✅ ТЕСТ ПРОЙДЕН")
            print(f"Ответ: {result['text'][:100]}...")
            print(f"Время: {result['processing_time']:.2f} сек")
        else:
            print("❌ ТЕСТ НЕ ПРОЙДЕН")
            print(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    
    else:
        print("❌ Нет доступных моделей для тестирования")

if __name__ == "__main__":
    test_adapter()