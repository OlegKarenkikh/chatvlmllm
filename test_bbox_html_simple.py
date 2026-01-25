#!/usr/bin/env python3
"""
Простой тест HTML генерации для BBOX без Streamlit
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_html_generation():
    """Тестирование генерации HTML"""
    
    print("🔧 Тестирование HTML генерации для BBOX...")
    
    try:
        from utils.bbox_table_renderer import BBoxTableRenderer
        print("✅ BBoxTableRenderer импортирован успешно")
        
        # Тестовые данные
        test_elements = [
            {"bbox": [81, 28, 220, 114], "category": "Picture", "text": ""},
            {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
            {"bbox": [309, 103, 873, 154], "category": "Section-header", "text": "РОССИЙСКАЯ ФЕДЕРАЦИЯ"},
            {"bbox": [81, 154, 220, 205], "category": "Text", "text": "1. ИВАНОВ"},
            {"bbox": [81, 205, 220, 256], "category": "Text", "text": "2. ИВАН"}
        ]
        
        print(f"✅ Тестовые данные: {len(test_elements)} элементов")
        
        renderer = BBoxTableRenderer()
        print("✅ BBoxTableRenderer инициализирован")
        
        # Генерируем HTML
        table_html = renderer.render_elements_table(test_elements)
        print(f"✅ HTML таблица сгенерирована: {len(table_html)} символов")
        
        # Сохраняем HTML файл для проверки
        with open("test_bbox_html_output.html", "w", encoding="utf-8") as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>BBOX HTML Test</title>
</head>
<body>
    <h1>Тест HTML таблицы BBOX</h1>
    {table_html}
</body>
</html>
            """)
        
        print("✅ HTML файл сохранен: test_bbox_html_output.html")
        
        # Показываем первые 500 символов
        print("\n📋 Первые 500 символов HTML:")
        print("-" * 50)
        print(table_html[:500])
        print("-" * 50)
        
        # Проверяем, что HTML содержит ожидаемые элементы
        checks = [
            ('<table class="bbox-table">', "Основная таблица"),
            ('<thead>', "Заголовок таблицы"),
            ('<tbody>', "Тело таблицы"),
            ('Picture', "Категория Picture"),
            ('Section-header', "Категория Section-header"),
            ('[81, 28, 220, 114]', "BBOX координаты"),
            ('ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ', "Текст элемента")
        ]
        
        print("\n🔍 Проверка содержимого HTML:")
        all_good = True
        for check, description in checks:
            if check in table_html:
                print(f"✅ {description}: найдено")
            else:
                print(f"❌ {description}: НЕ найдено")
                all_good = False
        
        if all_good:
            print("\n🎉 Все проверки прошли успешно!")
            print("💡 HTML генерируется корректно")
            return True
        else:
            print("\n⚠️ Некоторые проверки не прошли")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

def create_fixed_app():
    """Создание исправленной версии app.py"""
    
    print("\n🔧 Создание исправленной версии app.py...")
    
    try:
        # Читаем текущий app.py
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        print("✅ Файл app.py прочитан")
        
        # Ищем проблемный участок с детальной информацией
        old_code = '''        # HTML таблица с детальной информацией
        try:
            st.markdown("### 📋 Детальная информация")
            st.markdown(table_renderer.render_elements_table(elements), unsafe_allow_html=True)
        except:
            # Fallback на обычное отображение
            with st.expander("📊 Детали по категориям"):
                for category, count in stats.get('categories', {}).items():
                    st.write(f"**{category}:** {count}")'''
        
        # Новый исправленный код
        new_code = '''        # HTML таблица с детальной информацией
        st.markdown("### 📋 Детальная информация")
        try:
            # Генерируем HTML таблицу
            table_html = table_renderer.render_elements_table(elements)
            
            # Отображаем с HTML поддержкой
            st.markdown(table_html, unsafe_allow_html=True)
            st.success("✅ HTML таблица отображена")
            
        except Exception as e:
            st.warning(f"⚠️ HTML таблица не работает: {e}")
            
            # Fallback - красивое текстовое отображение
            st.markdown("**Элементы (текстовый формат):**")
            
            for i, element in enumerate(elements, 1):
                bbox = element.get('bbox', [0, 0, 0, 0])
                category = element.get('category', 'Unknown')
                text = element.get('text', '')
                
                # Цвет для категории (используем эмодзи как fallback)
                category_emoji = {
                    'Picture': '🖼️',
                    'Section-header': '📋',
                    'Text': '📝',
                    'List-item': '📌',
                    'Table': '📊',
                    'Title': '🏷️'
                }.get(category, '📄')
                
                # Форматирование BBOX
                bbox_str = f"[{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]"
                
                # Ограничение длины текста
                display_text = text[:100] + "..." if len(text) > 100 else text
                
                # Отображение элемента
                with st.container():
                    col_num, col_cat, col_bbox, col_text = st.columns([0.5, 1.5, 2, 4])
                    
                    with col_num:
                        st.markdown(f"**{i}**")
                    
                    with col_cat:
                        st.markdown(f"{category_emoji} {category}")
                    
                    with col_bbox:
                        st.code(bbox_str)
                    
                    with col_text:
                        if display_text:
                            st.caption(display_text)
                        else:
                            st.caption("_Нет текста_")'''
        
        # Заменяем код
        if old_code in content:
            new_content = content.replace(old_code, new_code)
            print("✅ Найден и заменен проблемный код")
        else:
            print("⚠️ Точное совпадение не найдено, ищем альтернативные варианты...")
            
            # Ищем более общий паттерн
            import re
            pattern = r'# HTML таблица с детальной информацией.*?st\.write\(f"\*\*{category}:\*\* {count}"\)'
            
            if re.search(pattern, content, re.DOTALL):
                new_content = re.sub(pattern, new_code.strip(), content, flags=re.DOTALL)
                print("✅ Найден и заменен код через регулярное выражение")
            else:
                print("❌ Не удалось найти код для замены")
                return False
        
        # Сохраняем исправленный файл
        with open("app_bbox_html_fixed.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("✅ Исправленный файл сохранен: app_bbox_html_fixed.py")
        print("💡 Переименуйте app_bbox_html_fixed.py в app.py для применения исправлений")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания исправленного файла: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Тест HTML генерации и исправление app.py\n")
    
    # Тестируем HTML генерацию
    html_ok = test_html_generation()
    
    # Создаем исправленную версию app.py
    if html_ok:
        app_ok = create_fixed_app()
        
        print(f"\n📊 Результаты:")
        print(f"   - HTML генерация: {'✅ Успешно' if html_ok else '❌ Ошибка'}")
        print(f"   - Исправление app.py: {'✅ Успешно' if app_ok else '❌ Ошибка'}")
        
        if html_ok and app_ok:
            print("\n🎉 Все исправления готовы!")
            print("📝 Следующие шаги:")
            print("   1. Переименуйте app_bbox_html_fixed.py в app.py")
            print("   2. Перезапустите Streamlit приложение")
            print("   3. Проверьте отображение детальной информации BBOX")
        else:
            print("\n⚠️ Некоторые исправления не удались")
    else:
        print("\n❌ HTML генерация не работает, исправление app.py пропущено")