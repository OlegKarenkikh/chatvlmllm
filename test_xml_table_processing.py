"""
Тестирование обработки XML-таблиц в OCR моделях
"""

import json
import os
from PIL import Image
import sys

# Добавляем пути
sys.path.append('.')
sys.path.append('./models')
sys.path.append('./utils')

from utils.xml_table_parser import analyze_ocr_output, XMLTableParser, PaymentDocumentParser
from utils.ocr_output_processor import OCROutputProcessor, process_ocr_text


def test_xml_parser():
    """Тестирует XML парсер"""
    print("=== Тестирование XML парсера ===")
    
    # Тестовый XML из примера
    test_xml = """ООО «Бетельгейзе Альфа Центавра-3»
Адрес: 100001, г. Москва, Веселый проспект, дом 13, офис 13
Образец заполнения платежного поручения
<table>
<tr><td>ИНН 7702000000</td><td>КПП 770201001</td><td></td></tr>
<tr><td>Получатель</td><td></td><td>Сч. №</td></tr>
<tr><td>ООО «Бетельгейзе Альфа Центавра-3»</td><td></td><td>40702890123456789012</td></tr>
<tr><td>Банк получателя</td><td></td><td>БИК</td></tr>
<tr><td>Сбербанк России ПАО г. Москва</td><td></td><td>Сч. №</td></tr>
<tr><td></td><td></td><td>30101810400000000225</td></tr>
</table>"""
    
    # Тестируем базовый парсер
    parser = XMLTableParser()
    xml_tables = parser.extract_xml_tables(test_xml)
    print(f"Найдено XML таблиц: {len(xml_tables)}")
    
    if xml_tables:
        parsed_table = parser.parse_table_xml(xml_tables[0])
        if parsed_table:
            print(f"Размер таблицы: {parsed_table.rows}x{parsed_table.cols}")
            print(f"Количество ячеек: {len(parsed_table.cells)}")
            
            # Конвертируем в словарь
            table_dict = parser.table_to_dict(parsed_table)
            print("\nДанные таблицы:")
            for i, row in enumerate(table_dict['data']):
                print(f"Строка {i}: {row}")
    
    print("\n" + "="*50)


def test_payment_parser():
    """Тестирует парсер платежных документов"""
    print("=== Тестирование парсера платежных документов ===")
    
    test_text = """ООО «Бетельгейзе Альфа Центавра-3»
Адрес: 100001, г. Москва, Веселый проспект, дом 13, офис 13
Образец заполнения платежного поручения
<table>
<tr><td>ИНН 7702000000</td><td>КПП 770201001</td><td></td></tr>
<tr><td>Получатель</td><td></td><td>Сч. №</td></tr>
<tr><td>ООО «Бетельгейзе Альфа Центавра-3»</td><td></td><td>40702890123456789012</td></tr>
<tr><td>Банк получателя</td><td></td><td>БИК</td></tr>
<tr><td>Сбербанк России ПАО г. Москва</td><td></td><td>Сч. №</td></tr>
<tr><td></td><td></td><td>30101810400000000225</td></tr>
</table>"""
    
    parser = PaymentDocumentParser()
    result = parser.parse_payment_document(test_text)
    
    print("Результат парсинга платежного документа:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*50)


def test_ocr_processor():
    """Тестирует OCR процессор"""
    print("=== Тестирование OCR процессора ===")
    
    test_text = """ООО «Бетельгейзе Альфа Центавра-3»
Адрес: 100001, г. Москва, Веселый проспект, дом 13, офис 13
Образец заполнения платежного поручения
<table>
<tr><td>ИНН 7702000000</td><td>КПП 770201001</td><td></td></tr>
<tr><td>Получатель</td><td></td><td>Сч. №</td></tr>
<tr><td>ООО «Бетельгейзе Альфа Центавра-3»</td><td></td><td>40702890123456789012</td></tr>
<tr><td>Банк получателя</td><td></td><td>БИК</td></tr>
<tr><td>Сбербанк России ПАО г. Москва</td><td></td><td>Сч. №</td></tr>
<tr><td></td><td></td><td>30101810400000000225</td></tr>
</table>"""
    
    processor = OCROutputProcessor()
    
    # Структурированный формат
    result_structured = processor.process_ocr_output(
        text=test_text,
        model_name="dots_ocr_test",
        extract_tables=True,
        extract_fields=True,
        output_format='structured'
    )
    
    print("Структурированный результат:")
    print(f"Тип документа: {result_structured['document_type']}")
    print(f"Есть XML таблицы: {result_structured['has_xml_tables']}")
    
    if 'tables' in result_structured['processed_data']:
        tables = result_structured['processed_data']['tables']
        print(f"Количество таблиц: {len(tables)}")
        
        for i, table in enumerate(tables):
            print(f"\nТаблица {i+1}:")
            print(f"  Размер: {table['rows']}x{table['cols']}")
            print(f"  Анализ: {table['analysis']}")
    
    if 'fields' in result_structured['processed_data']:
        fields = result_structured['processed_data']['fields']
        print(f"\nИзвлеченные поля: {fields}")
    
    # Упрощенный формат
    result_simple = processor.process_ocr_output(
        text=test_text,
        model_name="dots_ocr_test",
        output_format='simple'
    )
    
    print(f"\nУпрощенный результат:")
    print(f"Тип документа: {result_simple['document_type']}")
    print(f"Количество таблиц: {len(result_simple.get('tables', []))}")
    
    print("\n" + "="*50)


def test_quick_function():
    """Тестирует быструю функцию обработки"""
    print("=== Тестирование быстрой функции ===")
    
    test_text = """Счет-фактура № 123 от 15.01.2024
<table>
<tr><td>Наименование</td><td>Количество</td><td>Цена</td><td>Сумма</td></tr>
<tr><td>Товар 1</td><td>2</td><td>100.00</td><td>200.00</td></tr>
<tr><td>Товар 2</td><td>1</td><td>150.00</td><td>150.00</td></tr>
<tr><td>Итого:</td><td></td><td></td><td>350.00</td></tr>
</table>"""
    
    result = process_ocr_text(test_text, "test_model", "structured")
    
    print("Результат быстрой обработки:")
    print(f"Модель: {result['model_name']}")
    print(f"Тип документа: {result['document_type']}")
    
    if result['processed_data'].get('tables'):
        table = result['processed_data']['tables'][0]
        print(f"Таблица {table['rows']}x{table['cols']}:")
        for i, row in enumerate(table['data']):
            print(f"  {i}: {row}")
    
    print("\n" + "="*50)


def test_export_functionality():
    """Тестирует функции экспорта"""
    print("=== Тестирование экспорта ===")
    
    test_text = """Таблица данных
<table>
<tr><td>Название</td><td>Значение</td><td>Единица</td></tr>
<tr><td>Температура</td><td>25</td><td>°C</td></tr>
<tr><td>Давление</td><td>760</td><td>мм рт.ст.</td></tr>
<tr><td>Влажность</td><td>65</td><td>%</td></tr>
</table>"""
    
    processor = OCROutputProcessor()
    result = processor.process_ocr_output(test_text, "test_model")
    
    # Экспорт в JSON
    json_file = "test_export.json"
    success = processor.export_to_json(result, json_file)
    print(f"Экспорт в JSON: {'успешно' if success else 'ошибка'}")
    
    if success and os.path.exists(json_file):
        print(f"Файл {json_file} создан")
        # Читаем и показываем содержимое
        with open(json_file, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        print(f"Экспортированных таблиц: {len(exported_data.get('processed_data', {}).get('tables', []))}")
    
    print("\n" + "="*50)


def main():
    """Основная функция тестирования"""
    print("Тестирование системы обработки XML-таблиц OCR")
    print("=" * 60)
    
    try:
        test_xml_parser()
        test_payment_parser()
        test_ocr_processor()
        test_quick_function()
        test_export_functionality()
        
        print("\n🎉 Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()