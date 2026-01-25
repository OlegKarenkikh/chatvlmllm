#!/usr/bin/env python3
"""
Прямое исправление HTML рендеринга в чате
Заменяем SmartContentRenderer на простую функцию
"""

import re
import html
import streamlit as st

def render_html_tables_simple(content: str) -> str:
    """Простая замена HTML таблиц на markdown"""
    
    # Поиск HTML таблиц
    table_pattern = r'<table[^>]*>.*?</table>'
    tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not tables:
        return content
    
    result_content = content
    
    for table_html in tables:
        try:
            # Конвертируем HTML таблицу в markdown
            markdown_table = html_table_to_markdown(table_html)
            
            # Заменяем HTML таблицу на markdown
            result_content = result_content.replace(table_html, f"\n\n**📊 Таблица:**\n\n{markdown_table}\n\n")
            
        except Exception as e:
            print(f"Ошибка конвертации таблицы: {e}")
            # Fallback - просто убираем HTML теги
            clean_table = re.sub(r'<[^>]+>', '', table_html)
            result_content = result_content.replace(table_html, f"\n\n**📊 Таблица:**\n{clean_table}\n\n")
    
    return result_content

def html_table_to_markdown(table_html: str) -> str:
    """Конвертация HTML таблицы в Markdown"""
    
    try:
        # Извлечение строк таблицы
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
        
        if not rows:
            return "Не удалось извлечь строки таблицы"
        
        markdown_rows = []
        is_header = True
        
        for row in rows:
            # Извлечение ячеек
            cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL | re.IGNORECASE)
            
            if not cells:
                continue
            
            # Очистка содержимого ячеек от HTML тегов
            clean_cells = []
            for cell in cells:
                clean_cell = re.sub(r'<[^>]+>', '', cell)
                clean_cell = html.unescape(clean_cell).strip()
                # Ограничиваем длину ячейки
                if len(clean_cell) > 50:
                    clean_cell = clean_cell[:47] + "..."
                clean_cells.append(clean_cell)
            
            # Формирование строки Markdown
            markdown_row = "| " + " | ".join(clean_cells) + " |"
            markdown_rows.append(markdown_row)
            
            # Добавление разделителя после заголовка
            if is_header and len(clean_cells) > 0:
                separator = "| " + " | ".join(["---"] * len(clean_cells)) + " |"
                markdown_rows.append(separator)
                is_header = False
        
        return "\n".join(markdown_rows)
        
    except Exception as e:
        return f"Ошибка конвертации таблицы: {str(e)}"

def test_html_conversion():
    """Тест конвертации HTML в markdown"""
    
    test_html = """📋 Детальная информация<table class="bbox-table">
    <thead>
        <tr>
            <th style="width: 50px;">#</th>
            <th style="width: 150px;">Категория</th>
            <th style="width: 200px;">BBOX координаты</th>
            <th>Текст</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>Заголовок документа</td>
            <td>[45, 123, 567, 189]</td>
            <td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>
        </tr>
        <tr>
            <td>2</td>
            <td>Персональные данные</td>
            <td>[78, 234, 456, 298]</td>
            <td>ИВАНОВ ИВАН ИВАНОВИЧ</td>
        </tr>
    </tbody>
</table>

Анализ завершен."""
    
    print("🧪 ТЕСТ КОНВЕРТАЦИИ HTML В MARKDOWN")
    print("=" * 50)
    
    result = render_html_tables_simple(test_html)
    
    print("РЕЗУЛЬТАТ:")
    print(result)
    print("\n✅ Тест завершен")

if __name__ == "__main__":
    test_html_conversion()