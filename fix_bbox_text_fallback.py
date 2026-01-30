#!/usr/bin/env python3
"""
Радикальное исправление - замена HTML на текстовое отображение
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_text_fallback_solution():
    """Создание текстового fallback решения"""
    
    print("🔧 Создание текстового fallback решения...")
    
    try:
        # Читаем app.py
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        print("✅ Файл app.py прочитан")
        
        # Заменяем HTML отображение на текстовое
        old_html_code = '''        # HTML таблица с результатами - ИСПРАВЛЕНО
        try:
            from utils.bbox_table_renderer import BBoxTableRenderer
            
            table_renderer = BBoxTableRenderer()
            
            # Статистика - ПРИНУДИТЕЛЬНОЕ HTML отображение
            stats_html = table_renderer.render_statistics(elements)
            st.markdown("**📊 Статистика:**")
            st.markdown(stats_html, unsafe_allow_html=True)
            
            # Легенда - ПРИНУДИТЕЛЬНОЕ HTML отображение  
            legend_html = table_renderer.render_legend(elements)
            st.markdown("**🎨 Легенда категорий:**")
            st.markdown(legend_html, unsafe_allow_html=True)
            
        except Exception as e:
            st.warning(f"⚠️ Не удалось отобразить HTML таблицу: {e}")
            
            # Fallback - простое текстовое отображение
            categories = {}
            for element in elements:
                category = element.get('category', 'Unknown')
                categories[category] = categories.get(category, 0) + 1
            
            st.markdown("**📊 Статистика (текстовый формат):**")
            st.write(f"Всего элементов: {len(elements)}")
            st.write(f"Категорий: {len(categories)}")
            
            st.markdown("**🎨 Категории:**")
            for category, count in categories.items():
                st.write(f"• {category}: {count}")'''
        
        new_text_code = '''        # ТЕКСТОВОЕ отображение результатов (без HTML)
        st.markdown("**📊 Статистика:**")
        
        # Статистика в виде метрик
        col1, col2, col3 = st.columns(3)
        
        # Подсчет статистики
        categories = {}
        total_area = 0
        
        for element in elements:
            category = element.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            bbox = element.get('bbox', [0, 0, 0, 0])
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            total_area += area
        
        with col1:
            st.metric("Всего элементов", len(elements))
        
        with col2:
            st.metric("Категорий", len(categories))
        
        with col3:
            st.metric("Общая площадь", f"{total_area:,}")
        
        # Легенда в виде цветных индикаторов
        st.markdown("**🎨 Легенда категорий:**")
        
        # Цвета для категорий (эмодзи)
        category_emojis = {
            'Picture': '🖼️',
            'Section-header': '📋',
            'Text': '📝',
            'List-item': '📌',
            'Table': '📊',
            'Title': '🏷️',
            'Formula': '🧮',
            'Caption': '💬',
            'Footnote': '📄',
            'Page-header': '📑',
            'Page-footer': '📄',
            'Signature': '✍️',
            'Stamp': '🔖',
            'Logo': '🏢',
            'Barcode': '📊',
            'QR-code': '📱'
        }
        
        # Отображаем категории в колонках
        legend_cols = st.columns(min(len(categories), 4))
        
        for i, (category, count) in enumerate(sorted(categories.items())):
            col_idx = i % len(legend_cols)
            emoji = category_emojis.get(category, '📄')
            
            with legend_cols[col_idx]:
                st.markdown(f"{emoji} **{category}**")
                st.caption(f"Элементов: {count}")'''
        
        if old_html_code in content:
            content = content.replace(old_html_code, new_text_code)
            print("✅ Заменено HTML отображение на текстовое")
        else:
            print("⚠️ Точное совпадение не найдено, ищем альтернативы...")
            
            # Ищем более общий паттерн
            if "HTML таблица с результатами" in content:
                print("✅ Найден блок HTML таблицы")
                # Заменяем весь блок
                import re
                pattern = r'# HTML таблица с результатами.*?for category, count in categories\.items\(\):\s*st\.write\(f"• {category}: {count}"\)'
                
                if re.search(pattern, content, re.DOTALL):
                    content = re.sub(pattern, new_text_code.strip(), content, flags=re.DOTALL)
                    print("✅ Заменено через регулярное выражение")
                else:
                    print("❌ Не удалось найти блок для замены")
        
        # Также заменяем детальную таблицу
        old_detail_code = '''        # HTML таблица с детальной информацией - ИСПРАВЛЕНО
        st.markdown("### 📋 Детальная информация")
        try:
            # Генерируем HTML таблицу
            table_html = table_renderer.render_elements_table(elements)
            
            # ПРИНУДИТЕЛЬНОЕ HTML отображение с отладкой
            st.markdown("**Отображение HTML таблицы:**")
            st.markdown(table_html, unsafe_allow_html=True)
            st.success("✅ HTML таблица отображена")
            
        except Exception as e:
            st.warning(f"⚠️ HTML таблица не работает: {e}")
            st.error(f"Ошибка: {str(e)}")'''
        
        new_detail_code = '''        # ТЕКСТОВАЯ детальная информация (без HTML)
        st.markdown("### 📋 Детальная информация")
        
        # Отображаем элементы в виде карточек
        for i, element in enumerate(elements, 1):
            bbox = element.get('bbox', [0, 0, 0, 0])
            category = element.get('category', 'Unknown')
            text = element.get('text', '')
            
            # Эмодзи для категории
            emoji = category_emojis.get(category, '📄')
            
            # Форматирование BBOX
            bbox_str = f"[{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]"
            
            # Ограничение длины текста
            display_text = text[:100] + "..." if len(text) > 100 else text
            
            # Отображение элемента в контейнере
            with st.container():
                col_num, col_cat, col_bbox, col_text = st.columns([0.5, 1.5, 2, 4])
                
                with col_num:
                    st.markdown(f"**{i}**")
                
                with col_cat:
                    st.markdown(f"{emoji} {category}")
                
                with col_bbox:
                    st.code(bbox_str)
                
                with col_text:
                    if display_text:
                        st.caption(display_text)
                    else:
                        st.caption("_Нет текста_")
                
                # Разделитель между элементами
                if i < len(elements):
                    st.markdown("---")'''
        
        if old_detail_code in content:
            content = content.replace(old_detail_code, new_detail_code)
            print("✅ Заменена детальная HTML таблица на текстовую")
        else:
            print("⚠️ Детальная таблица не найдена для замены")
        
        # Сохраняем исправленный файл
        with open("app_text_fallback.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Исправленный файл сохранен: app_text_fallback.py")
        print("💡 Переименуйте app_text_fallback.py в app.py для применения")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Создание текстового fallback решения\n")
    
    success = create_text_fallback_solution()
    
    if success:
        print("\n🎉 Текстовое решение готово!")
        print("📝 Следующие шаги:")
        print("   1. Переименуйте app_text_fallback.py в app.py")
        print("   2. Перезапустите Streamlit приложение")
        print("   3. Проверьте отображение BBOX - теперь без HTML!")
        print("\n💡 Это решение использует:")
        print("   - Метрики Streamlit вместо HTML карточек")
        print("   - Эмодзи вместо цветных элементов")
        print("   - Колонки и контейнеры вместо HTML таблиц")
    else:
        print("\n❌ Создание решения не удалось")