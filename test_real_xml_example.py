"""
Тест реального примера XML от пользователя
"""

from utils.xml_table_parser import XMLTableParser, analyze_ocr_output
import json

# Реальный пример от пользователя
real_xml = """<table><tr><td>ИНН 7702000000</td><td>КПП 770201001</td><td></td></tr><tr><td>Получатель</td><td></td><td></td></tr><tr><td>ООО «Бетельгейзе Альфа Центавра-3»</td><td></td><td>Сч. № 40702890123456789012</td></tr><tr><td>Банк получателя</td><td></td><td>БИК 044525225</td></tr><tr><td>Сбербанк России ПАО г. Москва</td><td></td><td>Сч. № 30101810400000000225</td></tr></table> СЧЕТ № 151 от 14 апреля 2021 г. Плательщик: ООО «Бетельгейзе Альфа Центавра-3» Грузополучатель: ООО «Бетельгейзе Аль"""

print("=== Тестирование реального примера ===")
print("Исходный текст:")
print(real_xml)
print("\n" + "="*50)

# Тестируем парсер
parser = XMLTableParser()
xml_tables = parser.extract_xml_tables(real_xml)
print(f"Найдено XML таблиц: {len(xml_tables)}")

if xml_tables:
    print("\nИзвлеченная XML таблица:")
    print(xml_tables[0])
    
    parsed_table = parser.parse_table_xml(xml_tables[0])
    if parsed_table:
        print(f"\nРазмер таблицы: {parsed_table.rows}x{parsed_table.cols}")
        
        table_dict = parser.table_to_dict(parsed_table)
        print("\nДанные таблицы:")
        for i, row in enumerate(table_dict['data']):
            print(f"Строка {i}: {row}")
    else:
        print("Ошибка парсинга таблицы")

# Тестируем полный анализ
print("\n" + "="*50)
print("=== Полный анализ ===")
result = analyze_ocr_output(real_xml)
print(json.dumps(result, ensure_ascii=False, indent=2))