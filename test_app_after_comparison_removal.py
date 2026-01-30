#!/usr/bin/env python3
"""
Быстрый тест приложения после удаления раздела сравнения
"""

import sys
import os

def test_app_navigation():
    """Тестирует навигацию приложения"""
    
    print("🧪 Тестирование навигации приложения...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем структуру навигации
        navigation_found = False
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'page = st.radio(' in line:
                # Ищем следующие строки с массивом разделов
                for j in range(i, min(i+5, len(lines))):
                    if '[' in lines[j] and ']' in lines[j]:
                        navigation_line = lines[j]
                        navigation_found = True
                        break
                break
        
        if navigation_found:
            print(f"📋 Найдена навигация: {navigation_line.strip()}")
            
            # Проверяем разделы
            expected_sections = ["🏠 Главная", "📄 Режим OCR", "💬 Режим чата", "📚 Документация"]
            sections_found = []
            
            for section in expected_sections:
                if section in navigation_line:
                    sections_found.append(section)
            
            print(f"\n📊 Найденные разделы ({len(sections_found)}/4):")
            for section in sections_found:
                print(f"  ✅ {section}")
            
            # Проверяем, что сравнение удалено
            if "Сравнение" not in navigation_line:
                print("  ✅ Раздел 'Сравнение моделей' успешно удален")
            else:
                print("  ❌ Раздел 'Сравнение моделей' все еще присутствует")
                return False
            
            if len(sections_found) == 4:
                print("\n✅ Навигация работает корректно")
                return True
            else:
                print(f"\n❌ Найдено {len(sections_found)} разделов вместо 4")
                return False
        else:
            print("❌ Не найдена строка навигации")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании навигации: {e}")
        return False

def test_main_page_layout():
    """Тестирует макет главной страницы"""
    
    print("\n🎨 Тестирование макета главной страницы...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем структуру колонок
        if 'col1, col2 = st.columns(2)' in content:
            print("✅ Найдена структура из 2 колонок")
        else:
            print("❌ Не найдена структура из 2 колонок")
            return False
        
        # Проверяем карточки
        cards_found = []
        if '<h3>📄 Режим OCR</h3>' in content:
            cards_found.append("OCR")
        if '<h3>💬 Режим чата</h3>' in content:
            cards_found.append("Чат")
        if '<h3>📊 Сравнение</h3>' in content:
            cards_found.append("Сравнение (НЕ ДОЛЖНО БЫТЬ!)")
        
        print(f"\n📊 Найденные карточки ({len(cards_found)}):")
        for card in cards_found:
            if "НЕ ДОЛЖНО БЫТЬ" in card:
                print(f"  ❌ {card}")
                return False
            else:
                print(f"  ✅ {card}")
        
        if len(cards_found) == 2:
            print("✅ Макет главной страницы корректен")
            return True
        else:
            print(f"❌ Найдено {len(cards_found)} карточек вместо 2")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании макета: {e}")
        return False

def test_code_structure():
    """Тестирует структуру кода"""
    
    print("\n🔧 Тестирование структуры кода...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем разделы кода
        sections = {
            "Главная": 'if "🏠 Главная" in page:' in content,
            "OCR": 'elif "📄 Режим OCR" in page:' in content,
            "Чат": 'elif "💬 Режим чата" in page:' in content,
            "Документация": 'else:  # Документация' in content
        }
        
        print("📋 Разделы кода:")
        all_sections_ok = True
        for section_name, found in sections.items():
            status = "✅" if found else "❌"
            print(f"  {status} {section_name}")
            if not found:
                all_sections_ok = False
        
        # Проверяем, что код сравнения удален
        comparison_code_removed = 'elif "📊 Сравнение моделей" in page:' not in content
        
        if comparison_code_removed:
            print("  ✅ Код раздела сравнения удален")
        else:
            print("  ❌ Код раздела сравнения все еще присутствует")
            all_sections_ok = False
        
        # Проверяем импорты
        performance_analyzer_import = 'from utils.performance_analyzer import PerformanceAnalyzer' in content
        
        if not performance_analyzer_import:
            print("  ✅ Неиспользуемый импорт PerformanceAnalyzer удален")
        else:
            print("  ⚠️ Импорт PerformanceAnalyzer все еще присутствует")
        
        if all_sections_ok:
            print("✅ Структура кода корректна")
            return True
        else:
            print("❌ Проблемы в структуре кода")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании структуры: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тестирование приложения после удаления раздела сравнения")
    print("=" * 60)
    
    nav_ok = test_app_navigation()
    layout_ok = test_main_page_layout()
    code_ok = test_code_structure()
    
    if nav_ok and layout_ok and code_ok:
        print("\n🎉 Все тесты прошли успешно!")
        print("\n📋 Резюме:")
        print("  ✅ Навигация упрощена до 4 разделов")
        print("  ✅ Главная страница использует 2 колонки")
        print("  ✅ Код раздела сравнения полностью удален")
        print("  ✅ Приложение готово к использованию")
        
        print("\n💡 Оставшиеся разделы:")
        print("  • 🏠 Главная - обзор проекта")
        print("  • 📄 Режим OCR - извлечение текста")
        print("  • 💬 Режим чата - интерактивное общение")
        print("  • 📚 Документация - справочная информация")
    else:
        print("\n❌ Некоторые тесты не прошли")
        sys.exit(1)