#!/usr/bin/env python3
"""
Консольный тест HTML рендеринга
"""

import sys
import importlib

# Принудительная перезагрузка модулей
if 'utils.smart_content_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.smart_content_renderer'])
if 'utils.html_table_renderer' in sys.modules:
    importlib.reload(sys.modules['utils.html_table_renderer'])

from utils.smart_content_renderer import SmartContentRenderer

def test_html_rendering():
    """Тест HTML рендеринга в консоли"""
    
    test_content = """📋 Детальная информация<table class="bbox-table">         <thead>             <tr>                 <th style="width: 50px;">#</th>                 <th style="width: 150px;">Категория</th>                 <th style="width: 200px;">BBOX координаты</th>                 <th>Текст</th>             </tr>         </thead>         <tbody>             <tr>                 <td>1</td>                 <td>Заголовок документа</td>                 <td>[45, 123, 567, 189]</td>                 <td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>             </tr>         </tbody>     </table>

Анализ завершен."""
    
    print("🧪 КОНСОЛЬНЫЙ ТЕСТ HTML РЕНДЕРИНГА")
    print("=" * 50)
    
    # Тест 1: Определение HTML
    print("\n1. Тест определения HTML:")
    has_html = SmartContentRenderer.has_html_content(test_content)
    print(f"   HTML обнаружен: {has_html}")
    
    # Тест 2: Извлечение таблиц
    print("\n2. Тест извлечения таблиц:")
    content_info = SmartContentRenderer.extract_html_and_text(test_content)
    print(f"   Найдено таблиц: {len(content_info['tables'])}")
    print(f"   has_html: {content_info['has_html']}")
    
    if content_info['tables']:
        print(f"   Длина первой таблицы: {len(content_info['tables'][0])} символов")
        print(f"   Первые 100 символов таблицы: {content_info['tables'][0][:100]}...")
    
    # Тест 3: Очистка HTML таблицы
    print("\n3. Тест очистки HTML таблицы:")
    if content_info['tables']:
        from utils.html_table_renderer import HTMLTableRenderer
        renderer = HTMLTableRenderer()
        clean_table = renderer.clean_html_table(content_info['tables'][0])
        print(f"   Длина очищенной таблицы: {len(clean_table)} символов")
        print(f"   Первые 200 символов: {clean_table[:200]}...")
    
    print("\n✅ Консольный тест завершен")

if __name__ == "__main__":
    test_html_rendering()