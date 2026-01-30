#!/usr/bin/env python3
"""
Прямой тест BBOX функциональности без Streamlit
"""

from PIL import Image
import json
import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bbox_visualizer():
    """Тестирование BBoxVisualizer напрямую"""
    
    print("🔧 Тестирование BBOX функциональности...")
    
    try:
        from utils.bbox_visualizer import BBoxVisualizer
        print("✅ BBoxVisualizer импортирован успешно")
        
        # Создаем тестовое изображение
        test_image = Image.new('RGB', (800, 600), color='white')
        print(f"✅ Тестовое изображение создано: {test_image.size}")
        
        # Тестовые BBOX данные
        test_response = '''[
        {"bbox": [81, 28, 220, 114], "category": "Picture", "text": ""},
        {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
        {"bbox": [309, 103, 873, 154], "category": "Section-header", "text": "РОССИЙСКАЯ ФЕДЕРАЦИЯ"},
        {"bbox": [81, 154, 220, 205], "category": "Text", "text": "1. ИВАНОВ"},
        {"bbox": [81, 205, 220, 256], "category": "Text", "text": "2. ИВАН"}
        ]'''
        
        print(f"✅ Тестовые данные подготовлены: {len(json.loads(test_response))} элементов")
        
        # Инициализируем визуализатор
        visualizer = BBoxVisualizer()
        print("✅ BBoxVisualizer инициализирован")
        
        # Обрабатываем ответ
        image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
            test_image, 
            test_response,
            show_labels=True,
            create_legend_img=True
        )
        
        print(f"✅ Обработка завершена:")
        print(f"   - Найдено элементов: {len(elements)}")
        print(f"   - Изображение с BBOX: {image_with_boxes.size if image_with_boxes else 'None'}")
        print(f"   - Легенда: {legend_img.size if legend_img else 'None'}")
        
        # Сохраняем результаты
        if image_with_boxes:
            image_with_boxes.save("test_bbox_result.png")
            print("✅ Изображение с BBOX сохранено: test_bbox_result.png")
        
        if legend_img:
            legend_img.save("test_bbox_legend.png")
            print("✅ Легенда сохранена: test_bbox_legend.png")
        
        # Показываем статистику
        stats = visualizer.get_statistics(elements)
        print(f"✅ Статистика:")
        print(f"   - Всего элементов: {stats.get('total_elements', 0)}")
        print(f"   - Уникальных категорий: {stats.get('unique_categories', 0)}")
        print(f"   - Категории: {list(stats.get('categories', {}).keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

def test_bbox_table_renderer():
    """Тестирование BBoxTableRenderer"""
    
    print("\n🔧 Тестирование BBoxTableRenderer...")
    
    try:
        from utils.bbox_table_renderer import BBoxTableRenderer
        print("✅ BBoxTableRenderer импортирован успешно")
        
        # Тестовые элементы
        test_elements = [
            {"bbox": [81, 28, 220, 114], "category": "Picture", "text": ""},
            {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
            {"bbox": [81, 154, 220, 205], "category": "Text", "text": "1. ИВАНОВ"}
        ]
        
        renderer = BBoxTableRenderer()
        print("✅ BBoxTableRenderer инициализирован")
        
        # Тестируем рендеринг статистики
        stats_html = renderer.render_statistics(test_elements)
        print(f"✅ Статистика HTML сгенерирована: {len(stats_html)} символов")
        
        # Тестируем рендеринг легенды
        legend_html = renderer.render_legend(test_elements)
        print(f"✅ Легенда HTML сгенерирована: {len(legend_html)} символов")
        
        # Тестируем рендеринг таблицы элементов
        table_html = renderer.render_elements_table(test_elements)
        print(f"✅ Таблица элементов HTML сгенерирована: {len(table_html)} символов")
        
        # Сохраняем HTML для проверки
        with open("test_bbox_table.html", "w", encoding="utf-8") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"><title>BBOX Test</title></head>
            <body>
            <h1>Тест BBOX Table Renderer</h1>
            <h2>Статистика</h2>
            {stats_html}
            <h2>Легенда</h2>
            {legend_html}
            <h2>Таблица элементов</h2>
            {table_html}
            </body>
            </html>
            """)
        
        print("✅ HTML файл сохранен: test_bbox_table.html")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании BBoxTableRenderer: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов BBOX функциональности\n")
    
    success1 = test_bbox_visualizer()
    success2 = test_bbox_table_renderer()
    
    print(f"\n📊 Результаты тестирования:")
    print(f"   - BBoxVisualizer: {'✅ Успешно' if success1 else '❌ Ошибка'}")
    print(f"   - BBoxTableRenderer: {'✅ Успешно' if success2 else '❌ Ошибка'}")
    
    if success1 and success2:
        print("\n🎉 Все тесты прошли успешно! BBOX функциональность работает.")
    else:
        print("\n⚠️ Некоторые тесты не прошли. Проверьте ошибки выше.")