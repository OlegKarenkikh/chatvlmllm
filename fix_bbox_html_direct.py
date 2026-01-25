#!/usr/bin/env python3
"""
Прямое исправление HTML отображения BBOX
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_bbox_html_display():
    """Исправление HTML отображения BBOX"""
    
    print("🔧 Исправление HTML отображения BBOX...")
    
    try:
        # Читаем app.py
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        print("✅ Файл app.py прочитан")
        
        # Ищем функцию display_bbox_visualization_improved
        if "def display_bbox_visualization_improved" in content:
            print("✅ Найдена функция display_bbox_visualization_improved")
            
            # Заменяем проблемный код в функции display_bbox_visualization_improved
            old_code = '''        # HTML таблица с результатами
        try:
            from utils.bbox_table_renderer import BBoxTableRenderer
            
            table_renderer = BBoxTableRenderer()
            
            # Статистика
            st.markdown(table_renderer.render_statistics(elements), unsafe_allow_html=True)
            
            # Легенда
            st.markdown(table_renderer.render_legend(elements), unsafe_allow_html=True)
            
        except Exception as e:
            st.warning(f"⚠️ Не удалось отобразить HTML таблицу: {e}")'''
            
            new_code = '''        # HTML таблица с результатами - ИСПРАВЛЕНО
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
            
            if old_code in content:
                content = content.replace(old_code, new_code)
                print("✅ Заменен код HTML отображения статистики и легенды")
            else:
                print("⚠️ Точное совпадение не найдено для статистики")
            
            # Также исправляем детальную таблицу
            old_detail_code = '''        # HTML таблица с детальной информацией
        st.markdown("### 📋 Детальная информация")
        try:
            # Генерируем HTML таблицу
            table_html = table_renderer.render_elements_table(elements)
            
            # Отображаем с HTML поддержкой
            st.markdown(table_html, unsafe_allow_html=True)
            st.success("✅ HTML таблица отображена")
            
        except Exception as e:
            st.warning(f"⚠️ HTML таблица не работает: {e}")'''
            
            new_detail_code = '''        # HTML таблица с детальной информацией - ИСПРАВЛЕНО
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
            
            if old_detail_code in content:
                content = content.replace(old_detail_code, new_detail_code)
                print("✅ Заменен код HTML отображения детальной таблицы")
            else:
                print("⚠️ Точное совпадение не найдено для детальной таблицы")
        
        else:
            print("❌ Функция display_bbox_visualization_improved не найдена")
            return False
        
        # Сохраняем исправленный файл
        with open("app_bbox_html_direct_fixed.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Исправленный файл сохранен: app_bbox_html_direct_fixed.py")
        print("💡 Переименуйте app_bbox_html_direct_fixed.py в app.py для применения")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Прямое исправление HTML отображения BBOX\n")
    
    success = fix_bbox_html_display()
    
    if success:
        print("\n🎉 Исправление готово!")
        print("📝 Следующие шаги:")
        print("   1. Переименуйте app_bbox_html_direct_fixed.py в app.py")
        print("   2. Перезапустите Streamlit приложение")
        print("   3. Проверьте отображение BBOX")
    else:
        print("\n❌ Исправление не удалось")