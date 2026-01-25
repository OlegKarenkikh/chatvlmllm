#!/usr/bin/env python3
"""
Тест для выявления ошибок в приложении
"""

import sys
import traceback
import time

def test_app_imports():
    """Тестирование импортов приложения"""
    print("🧪 Тестирование импортов...")
    
    try:
        # Основные импорты
        import streamlit as st
        import yaml
        from pathlib import Path
        from PIL import Image
        import io
        import re
        import sys
        import importlib
        import html
        import time
        print("✅ Основные импорты успешны")
        
        # Специфичные импорты
        from single_container_manager import SingleContainerManager
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        print("✅ Специфичные импорты успешны")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        traceback.print_exc()
        return False

def test_config_loading():
    """Тестирование загрузки конфигурации"""
    print("\n🧪 Тестирование загрузки конфигурации...")
    
    try:
        import yaml
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        print("✅ Конфигурация загружена")
        print(f"  • Моделей в конфигурации: {len(config.get('models', {}))}")
        print(f"  • Поддерживаемые форматы: {config.get('ocr', {}).get('supported_formats', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        traceback.print_exc()
        return False

def test_single_container_manager():
    """Тестирование SingleContainerManager"""
    print("\n🧪 Тестирование SingleContainerManager...")
    
    try:
        from single_container_manager import SingleContainerManager
        
        manager = SingleContainerManager()
        print("✅ SingleContainerManager инициализирован")
        
        # Проверяем конфигурацию моделей
        models_count = len(manager.models_config)
        print(f"  • Доступно моделей: {models_count}")
        
        # Проверяем статус системы
        status = manager.get_system_status()
        print(f"  • Активная модель: {status.get('active_model_name', 'Нет')}")
        print(f"  • Принцип: {status.get('principle', 'Неизвестно')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка SingleContainerManager: {e}")
        traceback.print_exc()
        return False

def test_vllm_adapter():
    """Тестирование VLLMStreamlitAdapter"""
    print("\n🧪 Тестирование VLLMStreamlitAdapter...")
    
    try:
        from vllm_streamlit_adapter import VLLMStreamlitAdapter
        
        adapter = VLLMStreamlitAdapter()
        print("✅ VLLMStreamlitAdapter инициализирован")
        
        # Проверяем наличие менеджера контейнеров
        has_container_manager = hasattr(adapter, 'container_manager')
        print(f"  • Менеджер контейнеров: {'✅' if has_container_manager else '❌'}")
        
        # Проверяем доступные модели
        models_count = len(adapter.available_models)
        print(f"  • Доступно моделей: {models_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка VLLMStreamlitAdapter: {e}")
        traceback.print_exc()
        return False

def test_ui_components():
    """Тестирование UI компонентов"""
    print("\n🧪 Тестирование UI компонентов...")
    
    try:
        from ui.styles import get_custom_css
        print("✅ UI стили загружены")
        
        # Проверяем функции рендеринга
        from app import render_message_with_json_and_html_tables
        from app import is_dots_ocr_json_response
        from app import convert_dots_ocr_json_to_text_table
        from app import convert_html_table_to_text
        from app import clean_ocr_result
        
        print("✅ Функции рендеринга доступны")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка UI компонентов: {e}")
        traceback.print_exc()
        return False

def test_app_structure():
    """Тестирование структуры приложения"""
    print("\n🧪 Тестирование структуры приложения...")
    
    try:
        # Читаем app.py и проверяем ключевые компоненты
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()
        
        checks = [
            ("SingleContainerManager импорт", "from single_container_manager import SingleContainerManager" in app_content),
            ("VLLMStreamlitAdapter импорт", "from vllm_streamlit_adapter import VLLMStreamlitAdapter" in app_content),
            ("Инициализация менеджера", "single_container_manager" in app_content),
            ("Статус системы", "get_system_status" in app_content),
            ("Переключение модели", "start_single_container" in app_content),
            ("Режим OCR", 'elif "📄 Режим OCR" in page:' in app_content),
            ("Режим чата", 'elif "💬 Режим чата" in page:' in app_content),
            ("Главная страница", 'if "🏠 Главная" in page:' in app_content)
        ]
        
        passed = 0
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if result:
                passed += 1
        
        print(f"  📊 Проверок пройдено: {passed}/{len(checks)}")
        
        return passed == len(checks)
        
    except Exception as e:
        print(f"❌ Ошибка проверки структуры: {e}")
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ДИАГНОСТИКА ОШИБОК ПРИЛОЖЕНИЯ")
    print("=" * 50)
    
    tests = [
        ("Импорты", test_app_imports),
        ("Конфигурация", test_config_loading),
        ("SingleContainerManager", test_single_container_manager),
        ("VLLMStreamlitAdapter", test_vllm_adapter),
        ("UI компоненты", test_ui_components),
        ("Структура приложения", test_app_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print(f"\n🎯 ИТОГОВЫЙ ОТЧЕТ:")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Результат: {passed}/{total} тестов пройдено ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎊 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Приложение должно работать корректно.")
        print("💡 Если есть ошибки, они могут возникать при взаимодействии с пользователем.")
    else:
        print("⚠️ Обнаружены проблемы. Проверьте детали выше.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)