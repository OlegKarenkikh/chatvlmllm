#!/usr/bin/env python3
"""
Диагностика проблемы с отображением BBOX
"""

import json
from PIL import Image, ImageDraw
from utils.bbox_visualizer import BBoxVisualizer

def test_bbox_parsing():
    """Тестирование парсинга BBOX из вашего примера"""
    
    # Ваш пример данных из водительского удостоверения
    sample_bbox_data = [
        {"bbox": [81, 28, 220, 114], "category": "Picture"},
        {"bbox": [309, 52, 873, 103], "category": "Section-header", "text": "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ"},
        {"bbox": [45, 147, 284, 489], "category": "Picture"},
        {"bbox": [334, 129, 575, 180], "category": "List-item", "text": "1. ВАКАРИНЦЕВ\n VAKARINTSEV"},
        {"bbox": [332, 184, 664, 237], "category": "List-item", "text": "2. АНДРЕЙ ПАВЛОВИЧ\n ANDREY PAVLOVICH"},
        {"bbox": [332, 241, 636, 325], "category": "List-item", "text": "3. 13.09.1995\n АЛТАЙСКИЙ КРАЙ\n ALTAYSKIY KRAY"},
        {"bbox": [332, 328, 521, 360], "category": "List-item", "text": "4а) 03.01.2014"},
        {"bbox": [583, 328, 770, 362], "category": "List-item", "text": "4b) 03.01.2020"},
        {"bbox": [332, 362, 544, 412], "category": "List-item", "text": "4с) ГИБДД 2247\n GIBDD 2247"},
        {"bbox": [330, 416, 548, 448], "category": "List-item", "text": "5. 22 13 616660"},
        {"bbox": [329, 450, 635, 503], "category": "List-item", "text": "8. АЛТАЙСКИЙ КРАЙ\n ALTAYSKIY KRAY"},
        {"bbox": [329, 517, 417, 559], "category": "List-item", "text": "9. B"},
        {"bbox": [34, 501, 60, 528], "category": "Text", "text": "6."},
        {"bbox": [33, 537, 247, 610], "category": "Picture"}
    ]
    
    print("🔍 ДИАГНОСТИКА ПРОБЛЕМЫ С BBOX")
    print("=" * 50)
    
    # 1. Проверяем парсинг данных
    print("\n1️⃣ Проверка данных BBOX:")
    print(f"   📊 Всего элементов: {len(sample_bbox_data)}")
    
    # Анализируем координаты
    max_x = max(max(item['bbox'][0], item['bbox'][2]) for item in sample_bbox_data)
    max_y = max(max(item['bbox'][1], item['bbox'][3]) for item in sample_bbox_data)
    
    print(f"   📐 Максимальные координаты: X={max_x}, Y={max_y}")
    print(f"   📏 Предполагаемый размер изображения: {max_x}x{max_y}")
    
    # Проверяем категории
    categories = {}
    for item in sample_bbox_data:
        cat = item['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"   🏷️ Категории: {categories}")
    
    # 2. Создаем тестовое изображение подходящего размера
    print(f"\n2️⃣ Создание тестового изображения:")
    
    # Добавляем отступы к размеру изображения
    img_width = max_x + 100
    img_height = max_y + 100
    
    print(f"   📏 Размер изображения: {img_width}x{img_height}")
    
    # Создаем белое изображение
    test_image = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(test_image)
    
    # Добавляем некоторый контент для наглядности
    draw.text((309, 52), "ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ", fill='black')
    draw.text((334, 129), "1. ВАКАРИНЦЕВ", fill='black')
    draw.text((332, 184), "2. АНДРЕЙ ПАВЛОВИЧ", fill='black')
    draw.text((332, 241), "3. 13.09.1995", fill='black')
    
    # Рисуем прямоугольники для Picture элементов
    draw.rectangle([81, 28, 220, 114], outline='gray', width=2)  # Фото
    draw.rectangle([45, 147, 284, 489], outline='gray', width=2)  # Большое фото
    draw.rectangle([33, 537, 247, 610], outline='gray', width=2)  # Подпись
    
    test_image.save("debug_driver_license_test.png")
    print(f"   ✅ Тестовое изображение сохранено: debug_driver_license_test.png")
    
    # 3. Тестируем BBoxVisualizer
    print(f"\n3️⃣ Тестирование BBoxVisualizer:")
    
    visualizer = BBoxVisualizer()
    
    # Конвертируем данные в JSON строку для тестирования парсера
    json_response = json.dumps(sample_bbox_data, ensure_ascii=False, indent=2)
    
    try:
        # Обрабатываем ответ
        image_with_boxes, legend_img, elements = visualizer.process_dots_ocr_response(
            test_image, 
            json_response,
            show_labels=True,
            create_legend_img=True
        )
        
        print(f"   ✅ Обработка успешна!")
        print(f"   📊 Обработано элементов: {len(elements)}")
        
        # Сохраняем результаты
        image_with_boxes.save("debug_bbox_visualization.png")
        print(f"   💾 Изображение с BBOX: debug_bbox_visualization.png")
        
        if legend_img:
            legend_img.save("debug_bbox_legend.png")
            print(f"   💾 Легенда: debug_bbox_legend.png")
        
        # Статистика
        stats = visualizer.get_statistics(elements)
        print(f"   📈 Статистика: {stats}")
        
        # 4. Проверяем каждый BBOX индивидуально
        print(f"\n4️⃣ Детальная проверка BBOX:")
        
        for i, element in enumerate(elements):
            bbox = element['bbox']
            category = element.get('category', 'Unknown')
            text = element.get('text', '')[:30] + "..." if len(element.get('text', '')) > 30 else element.get('text', '')
            
            # Проверяем валидность координат
            x1, y1, x2, y2 = bbox
            width = x2 - x1
            height = y2 - y1
            
            valid = (x1 >= 0 and y1 >= 0 and x2 <= img_width and y2 <= img_height and width > 0 and height > 0)
            status = "✅" if valid else "❌"
            
            print(f"   {status} #{i+1}: [{x1}, {y1}, {x2}, {y2}] {width}x{height} - {category} - {text}")
            
            if not valid:
                print(f"      ⚠️ Проблема: координаты выходят за границы изображения или некорректны")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка обработки: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_color_mapping():
    """Тестирование цветового маппинга категорий"""
    
    print(f"\n5️⃣ Тестирование цветов категорий:")
    
    visualizer = BBoxVisualizer()
    
    categories = ["Picture", "Section-header", "List-item", "Text"]
    
    for category in categories:
        color = visualizer.get_category_color(category)
        print(f"   🎨 {category}: {color}")

def main():
    """Главная функция диагностики"""
    
    success = test_bbox_parsing()
    test_color_mapping()
    
    print(f"\n" + "=" * 50)
    if success:
        print("✅ ДИАГНОСТИКА ЗАВЕРШЕНА УСПЕШНО")
        print("📁 Проверьте созданные файлы:")
        print("   • debug_driver_license_test.png - тестовое изображение")
        print("   • debug_bbox_visualization.png - изображение с BBOX")
        print("   • debug_bbox_legend.png - легенда категорий")
        print("\n💡 Если BBOX отображаются некорректно, проблема может быть в:")
        print("   1. Неправильных координатах от модели")
        print("   2. Несоответствии размера изображения")
        print("   3. Ошибке в коде визуализации")
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        print("🔧 Требуется дополнительная диагностика")

if __name__ == "__main__":
    main()