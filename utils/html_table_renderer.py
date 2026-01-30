#!/usr/bin/env python3
"""
Утилита для рендеринга HTML таблиц из ответов dots.ocr
"""

import re
import html
from typing import List, Dict, Any, Optional
import streamlit as st

class HTMLTableRenderer:
    """Класс для обработки и рендеринга HTML таблиц"""
    
    def __init__(self):
        self.table_counter = 0
    
    def extract_html_tables(self, text: str) -> List[str]:
        """Извлечение HTML таблиц из текста"""
        
        # Паттерны для поиска HTML таблиц
        table_patterns = [
            r'<table[^>]*>.*?</table>',
            r'<table>.*?</table>',
        ]
        
        tables = []
        
        for pattern in table_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            tables.extend(matches)
        
        # Удаление дубликатов
        unique_tables = []
        for table in tables:
            if table not in unique_tables:
                unique_tables.append(table)
        
        return unique_tables
    
    def clean_html_table(self, table_html: str) -> str:
        """Очистка и форматирование HTML таблицы"""
        
        # Удаление лишних пробелов и переносов строк
        table_html = re.sub(r'\s+', ' ', table_html)
        table_html = table_html.strip()
        
        # Добавление базовых стилей если их нет
        if 'style=' not in table_html.lower():
            # Добавляем стили к таблице
            table_html = table_html.replace('<table', '<table style="border-collapse: collapse; width: 100%; margin: 10px 0; background-color: white;"', 1)
        
        # Добавление стилей к ячейкам если их нет
        if 'border:' not in table_html.lower():
            table_html = re.sub(r'<td([^>]*)>', r'<td\1 style="border: 1px solid #ddd; padding: 8px; text-align: left; color: #333; background-color: white;">', table_html)
            table_html = re.sub(r'<th([^>]*)>', r'<th\1 style="border: 1px solid #ddd; padding: 8px; text-align: left; background-color: #f8f9fa; font-weight: bold; color: #333;">', table_html)
        
        return table_html
    
    def table_to_markdown(self, table_html: str) -> str:
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
    
    def extract_table_data(self, table_html: str) -> Dict[str, Any]:
        """Извлечение структурированных данных из HTML таблицы"""
        
        try:
            # Извлечение строк
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
            
            if not rows:
                return {"error": "Не найдено строк в таблице"}
            
            table_data = {
                "headers": [],
                "rows": [],
                "total_rows": len(rows),
                "total_columns": 0
            }
            
            for i, row in enumerate(rows):
                # Извлечение ячеек
                cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL | re.IGNORECASE)
                
                if not cells:
                    continue
                
                # Очистка содержимого ячеек
                clean_cells = []
                for cell in cells:
                    clean_cell = re.sub(r'<[^>]+>', '', cell)
                    clean_cell = html.unescape(clean_cell).strip()
                    clean_cells.append(clean_cell)
                
                # Первая строка как заголовки
                if i == 0:
                    table_data["headers"] = clean_cells
                    table_data["total_columns"] = len(clean_cells)
                else:
                    table_data["rows"].append(clean_cells)
            
            return table_data
            
        except Exception as e:
            return {"error": f"Ошибка извлечения данных: {str(e)}"}
    
    def render_table_in_streamlit(self, table_html: str, title: Optional[str] = None) -> None:
        """Рендеринг HTML таблицы в Streamlit"""
        
        self.table_counter += 1
        table_id = f"{id(self)}_{self.table_counter}"  # Уникальный ID для каждого экземпляра
        
        if title:
            st.subheader(title)
        else:
            st.subheader(f"📊 Таблица {self.table_counter}")
        
        # Очистка и стилизация таблицы
        clean_table = self.clean_html_table(table_html)
        
        # Отображение HTML таблицы
        st.markdown(clean_table, unsafe_allow_html=True)
        
        # Дополнительные опции
        with st.expander(f"🔧 Опции таблицы {self.table_counter}"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Показать как Markdown
                if st.button(f"📝 Показать Markdown", key=f"md_{table_id}"):
                    markdown_table = self.table_to_markdown(table_html)
                    st.code(markdown_table, language="markdown")
            
            with col2:
                # Показать структурированные данные
                if st.button(f"📊 Показать данные", key=f"data_{table_id}"):
                    table_data = self.extract_table_data(table_html)
                    st.json(table_data)
            
            # Исходный HTML
            st.text_area(f"HTML код таблицы {self.table_counter}:", clean_table, height=100, key=f"html_{table_id}")
    
    def process_dots_ocr_response(self, response_text: str) -> Dict[str, Any]:
        """Обработка ответа dots.ocr для поиска и рендеринга таблиц"""
        
        # Извлечение HTML таблиц
        html_tables = self.extract_html_tables(response_text)
        
        result = {
            "found_tables": len(html_tables),
            "tables": [],
            "has_tables": len(html_tables) > 0
        }
        
        for i, table_html in enumerate(html_tables):
            table_info = {
                "index": i + 1,
                "html": table_html,
                "clean_html": self.clean_html_table(table_html),
                "markdown": self.table_to_markdown(table_html),
                "data": self.extract_table_data(table_html)
            }
            result["tables"].append(table_info)
        
        return result
    
    def render_all_tables_in_streamlit(self, response_text: str) -> None:
        """Рендеринг всех найденных таблиц в Streamlit"""
        
        result = self.process_dots_ocr_response(response_text)
        
        if not result["has_tables"]:
            st.info("📋 В ответе не найдено HTML таблиц")
            return
        
        st.success(f"📊 Найдено {result['found_tables']} таблиц в ответе")
        
        for table_info in result["tables"]:
            self.render_table_in_streamlit(
                table_info["html"], 
                f"Таблица {table_info['index']}"
            )
            
            # Разделитель между таблицами
            if table_info["index"] < len(result["tables"]):
                st.divider()

def test_html_table_renderer():
    """Тестирование HTMLTableRenderer"""
    
    # Пример ответа dots.ocr с HTML таблицей
    sample_response = '''
    Вот результат анализа документа:
    
    <table>
        <thead>
            <tr>
                <td>Товар</td>
                <td>Количество</td>
                <td>Цена</td>
                <td>Сумма</td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Хлеб</td>
                <td>2</td>
                <td>50</td>
                <td>100</td>
            </tr>
            <tr>
                <td>Молоко</td>
                <td>1</td>
                <td>80</td>
                <td>80</td>
            </tr>
        </tbody>
    </table>
    
    Дополнительная информация о документе.
    
    <table>
        <tr>
            <th>Параметр</th>
            <th>Значение</th>
        </tr>
        <tr>
            <td>Дата</td>
            <td>24.01.2026</td>
        </tr>
        <tr>
            <td>Итого</td>
            <td>180 руб.</td>
        </tr>
    </table>
    '''
    
    # Тестирование рендерера
    renderer = HTMLTableRenderer()
    
    # Обработка ответа
    result = renderer.process_dots_ocr_response(sample_response)
    
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ HTML TABLE RENDERER")
    print("=" * 50)
    print(f"Найдено таблиц: {result['found_tables']}")
    
    for i, table_info in enumerate(result["tables"]):
        print(f"\n📋 Таблица {i + 1}:")
        print(f"   HTML длина: {len(table_info['html'])} символов")
        print(f"   Данные: {table_info['data']['total_rows']} строк, {table_info['data']['total_columns']} столбцов")
        print(f"   Заголовки: {table_info['data']['headers']}")
        
        print(f"\n   Markdown представление:")
        print(table_info['markdown'])
    
    print("\n✅ Тестирование завершено")

if __name__ == "__main__":
    test_html_table_renderer()