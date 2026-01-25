#!/usr/bin/env python3
"""
Принудительная перезагрузка модулей HTML рендеринга
"""

import sys
import importlib
import os

def force_reload_modules():
    """Принудительная перезагрузка модулей"""
    
    modules_to_reload = [
        'utils.smart_content_renderer',
        'utils.html_table_renderer'
    ]
    
    print("🔄 Принудительная перезагрузка модулей HTML рендеринга...")
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            print(f"   Перезагружаю: {module_name}")
            importlib.reload(sys.modules[module_name])
        else:
            print(f"   Модуль не загружен: {module_name}")
    
    # Проверяем, что файлы существуют и обновлены
    files_to_check = [
        'utils/smart_content_renderer.py',
        'utils/html_table_renderer.py'
    ]
    
    print("\n📁 Проверка файлов:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            print(f"   ✅ {file_path} - обновлен: {mtime}")
        else:
            print(f"   ❌ {file_path} - не найден!")
    
    print("\n✅ Перезагрузка завершена")

def test_html_detection():
    """Тест определения HTML"""
    
    # Импортируем после перезагрузки
    from utils.smart_content_renderer import SmartContentRenderer
    
    test_content = """📋 Детальная информация
<table class="bbox-table">
    <thead>
        <tr>
            <th>#</th>
            <th>Категория</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>Тест</td>
        </tr>
    </tbody>
</table>"""
    
    print("\n🧪 Тест определения HTML:")
    has_html = SmartContentRenderer.has_html_content(test_content)
    print(f"   HTML обнаружен: {has_html}")
    
    if has_html:
        content_info = SmartContentRenderer.extract_html_and_text(test_content)
        print(f"   Найдено таблиц: {len(content_info['tables'])}")
        
        if content_info['tables']:
            print("   ✅ Таблица успешно извлечена")
        else:
            print("   ❌ Таблица не извлечена")
    else:
        print("   ❌ HTML не обнаружен")

if __name__ == "__main__":
    force_reload_modules()
    test_html_detection()