#!/usr/bin/env python3
"""
Утилита для умного рендеринга контента в Streamlit
Автоматически определяет наличие HTML и выбирает подходящий способ отображения
"""

import re
import streamlit as st
from typing import Optional

class SmartContentRenderer:
    """Класс для умного рендеринга контента с HTML"""
    
    @staticmethod
    def has_html_content(text: str) -> bool:
        """Проверка наличия HTML тегов в тексте"""
        
        # Основные HTML теги, которые могут встречаться в ответах
        html_patterns = [
            r'<table[^>]*>.*?</table>',
            r'<div[^>]*>.*?</div>',
            r'<p[^>]*>.*?</p>',
            r'<span[^>]*>.*?</span>',
            r'<ul[^>]*>.*?</ul>',
            r'<ol[^>]*>.*?</ol>',
            r'<li[^>]*>.*?</li>',
            r'<h[1-6][^>]*>.*?</h[1-6]>',
            r'<strong[^>]*>.*?</strong>',
            r'<em[^>]*>.*?</em>',
            r'<b[^>]*>.*?</b>',
            r'<i[^>]*>.*?</i>',
            r'<br\s*/?>'
        ]
        
        for pattern in html_patterns:
            if re.search(pattern, text, re.DOTALL | re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def extract_html_and_text(content: str) -> dict:
        """Разделение контента на HTML и обычный текст"""
        
        # Поиск HTML таблиц
        table_pattern = r'<table[^>]*>.*?</table>'
        tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
        
        # Удаление HTML таблиц из основного текста
        text_without_tables = content
        for table in tables:
            text_without_tables = text_without_tables.replace(table, '[TABLE_PLACEHOLDER]')
        
        return {
            'has_html': len(tables) > 0,
            'tables': tables,
            'text_content': text_without_tables,
            'original_content': content
        }
    
    @staticmethod
    def render_content_smart(content: str, container=None) -> None:
        """Умное отображение контента с автоматическим определением HTML"""
        
        if container is None:
            container = st
        
        # Анализ контента
        content_info = SmartContentRenderer.extract_html_and_text(content)
        
        if content_info['has_html']:
            # Есть HTML контент - используем специальную обработку
            SmartContentRenderer._render_mixed_content(content_info, container)
        else:
            # Обычный текст - стандартное отображение
            container.markdown(content)
    
    @staticmethod
    def _render_mixed_content(content_info: dict, container) -> None:
        """Рендеринг смешанного контента (текст + HTML)"""
        
        text_content = content_info['text_content']
        tables = content_info['tables']
        
        # Разбиваем текст по плейсхолдерам таблиц
        text_parts = text_content.split('[TABLE_PLACEHOLDER]')
        
        # Отображаем части текста и таблицы поочередно
        for i, text_part in enumerate(text_parts):
            # Отображаем текстовую часть
            if text_part.strip():
                container.markdown(text_part.strip())
            
            # Отображаем таблицу если она есть
            if i < len(tables):
                try:
                    # Импортируем рендерер таблиц
                    from utils.html_table_renderer import HTMLTableRenderer
                    
                    renderer = HTMLTableRenderer()
                    
                    # Простое отображение таблицы без дополнительных опций для чата
                    clean_table = renderer.clean_html_table(tables[i])
                    container.markdown("**📊 Таблица:**")
                    container.markdown(clean_table, unsafe_allow_html=True)
                        
                except Exception as e:
                    # Fallback - отображаем как HTML с unsafe_allow_html
                    container.markdown(f"**📊 Таблица:**")
                    container.markdown(tables[i], unsafe_allow_html=True)
    
    @staticmethod
    def render_message_content(message: dict, container=None) -> None:
        """Рендеринг содержимого сообщения чата"""
        
        if container is None:
            container = st
        
        content = message.get("content", "")
        role = message.get("role", "")
        
        # Добавляем индикатор роли если нужно
        if role == "assistant":
            # Для ответов ассистента используем умный рендеринг
            SmartContentRenderer.render_content_smart(content, container)
        else:
            # Для пользовательских сообщений - обычное отображение
            container.markdown(content)
    
    @staticmethod
    def clean_html_for_display(html_content: str) -> str:
        """Очистка HTML для безопасного отображения"""
        
        # Удаляем потенциально опасные теги
        dangerous_tags = ['script', 'style', 'iframe', 'object', 'embed']
        
        for tag in dangerous_tags:
            pattern = f'<{tag}[^>]*>.*?</{tag}>'
            html_content = re.sub(pattern, '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        return html_content

def test_smart_content_renderer():
    """Тестирование SmartContentRenderer"""
    
    # Тестовые данные
    test_cases = [
        {
            "name": "Обычный текст",
            "content": "Это обычный текст без HTML тегов."
        },
        {
            "name": "Текст с HTML таблицей",
            "content": """
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
            </table>
            
            Дополнительная информация.
            """
        },
        {
            "name": "Множественные таблицы",
            "content": """
            Первая таблица:
            
            <table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>
            
            Текст между таблицами.
            
            <table><tr><th>C</th><th>D</th></tr><tr><td>3</td><td>4</td></tr></table>
            
            Заключение.
            """
        }
    ]
    
    print("🧪 ТЕСТИРОВАНИЕ SMART CONTENT RENDERER")
    print("=" * 50)
    
    renderer = SmartContentRenderer()
    
    for test_case in test_cases:
        print(f"\n📝 Тест: {test_case['name']}")
        
        # Проверка наличия HTML
        has_html = renderer.has_html_content(test_case['content'])
        print(f"   HTML обнаружен: {has_html}")
        
        # Анализ контента
        content_info = renderer.extract_html_and_text(test_case['content'])
        print(f"   Найдено таблиц: {len(content_info['tables'])}")
        
        if content_info['tables']:
            for i, table in enumerate(content_info['tables']):
                print(f"   Таблица {i+1}: {len(table)} символов")
    
    print("\n✅ Тестирование завершено")

if __name__ == "__main__":
    test_smart_content_renderer()