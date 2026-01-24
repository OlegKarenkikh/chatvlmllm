#!/usr/bin/env python3
"""
Проверка работы исправления HTML рендеринга
"""

import requests
import time

def check_streamlit_app():
    """Проверка доступности Streamlit приложения"""
    
    print("🔍 Проверка доступности приложения...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Приложение доступно на http://localhost:8501")
            return True
        else:
            print(f"❌ Приложение недоступно. Код ответа: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def verify_smart_renderer():
    """Проверка работы умного рендерера"""
    
    print("\n🧪 Проверка умного рендерера...")
    
    try:
        from utils.smart_content_renderer import SmartContentRenderer
        
        # Тестовый HTML контент
        test_html = """
        Результат анализа:
        
        <table>
            <tr><th>Товар</th><th>Цена</th></tr>
            <tr><td>Хлеб</td><td>50</td></tr>
        </table>
        
        Итого: 50 руб.
        """
        
        renderer = SmartContentRenderer()
        
        # Проверка определения HTML
        has_html = renderer.has_html_content(test_html)
        print(f"   HTML обнаружен: {has_html}")
        
        # Проверка извлечения таблиц
        content_info = renderer.extract_html_and_text(test_html)
        print(f"   Найдено таблиц: {len(content_info['tables'])}")
        
        if has_html and len(content_info['tables']) > 0:
            print("✅ Умный рендерер работает корректно")
            return True
        else:
            print("❌ Проблема с умным рендерером")
            return False
            
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Главная функция проверки"""
    
    print("🔧 ПРОВЕРКА ИСПРАВЛЕНИЯ HTML РЕНДЕРИНГА")
    print("=" * 50)
    
    # Проверка доступности приложения
    app_ok = check_streamlit_app()
    
    # Проверка умного рендерера
    renderer_ok = verify_smart_renderer()
    
    print("\n📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print("=" * 30)
    print(f"Приложение доступно: {'✅' if app_ok else '❌'}")
    print(f"Умный рендерер работает: {'✅' if renderer_ok else '❌'}")
    
    if app_ok and renderer_ok:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        print("Исправление HTML рендеринга работает корректно.")
        print("\n📱 Откройте http://localhost:8501 для тестирования")
        print("💡 Загрузите документ с таблицей и проверьте отображение")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        if not app_ok:
            print("- Приложение недоступно. Проверьте запуск Streamlit")
        if not renderer_ok:
            print("- Проблема с умным рендерером. Проверьте файлы")

if __name__ == "__main__":
    main()