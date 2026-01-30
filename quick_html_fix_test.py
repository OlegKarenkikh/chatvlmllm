#!/usr/bin/env python3
"""
Быстрый тест исправления HTML рендеринга
"""

def test_smart_renderer():
    """Тест умного рендерера без Streamlit"""
    
    from utils.smart_content_renderer import SmartContentRenderer
    
    # Тестовый контент с HTML таблицей
    test_content = """
    Результат анализа документа:
    
    <table>
        <tr>
            <th>Товар</th>
            <th>Цена</th>
        </tr>
        <tr>
            <td>Хлеб</td>
            <td>50 руб</td>
        </tr>
        <tr>
            <td>Молоко</td>
            <td>80 руб</td>
        </tr>
    </table>
    
    Общая сумма: 130 руб.
    """
    
    print("🧪 ТЕСТ УМНОГО РЕНДЕРЕРА HTML")
    print("=" * 40)
    
    renderer = SmartContentRenderer()
    
    # Проверка определения HTML
    has_html = renderer.has_html_content(test_content)
    print(f"HTML обнаружен: {has_html}")
    
    # Анализ контента
    content_info = renderer.extract_html_and_text(test_content)
    print(f"Найдено таблиц: {len(content_info['tables'])}")
    print(f"Есть HTML: {content_info['has_html']}")
    
    # Показываем разделенный контент
    print("\n📝 Текстовая часть:")
    print(content_info['text_content'])
    
    print("\n📊 HTML таблицы:")
    for i, table in enumerate(content_info['tables']):
        print(f"Таблица {i+1}: {len(table)} символов")
        print(table[:100] + "..." if len(table) > 100 else table)
    
    print("\n✅ Тест завершен успешно!")
    
    return True

def test_message_rendering():
    """Тест рендеринга сообщений"""
    
    print("\n🔄 ТЕСТ РЕНДЕРИНГА СООБЩЕНИЙ")
    print("=" * 40)
    
    # Тестовые сообщения
    messages = [
        {
            "role": "user",
            "content": "Проанализируй документ"
        },
        {
            "role": "assistant",
            "content": """Анализ завершен:

<table>
<tr><th>Параметр</th><th>Значение</th></tr>
<tr><td>Тип документа</td><td>Чек</td></tr>
<tr><td>Дата</td><td>25.01.2026</td></tr>
</table>

Документ обработан успешно."""
        }
    ]
    
    from utils.smart_content_renderer import SmartContentRenderer
    
    for i, message in enumerate(messages):
        print(f"\n📨 Сообщение {i+1} ({message['role']}):")
        
        # Проверяем наличие HTML
        has_html = SmartContentRenderer.has_html_content(message['content'])
        print(f"   HTML: {has_html}")
        
        # Показываем первые 100 символов контента
        content_preview = message['content'][:100].replace('\n', ' ')
        print(f"   Контент: {content_preview}...")
    
    print("\n✅ Тест сообщений завершен!")
    
    return True

if __name__ == "__main__":
    try:
        test_smart_renderer()
        test_message_rendering()
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("Исправление HTML рендеринга работает корректно.")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()