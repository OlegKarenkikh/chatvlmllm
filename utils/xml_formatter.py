"""
Утилиты для форматирования XML-таблиц в читаемый вид
"""

import re
from typing import Dict, Any, List, Optional
from .xml_table_parser import XMLTableParser, analyze_ocr_output


class XMLTableFormatter:
    """Форматировщик XML-таблиц для удобного отображения"""
    
    def __init__(self):
        self.parser = XMLTableParser()
    
    def format_table_as_text(self, table_data: Dict[str, Any], 
                           separator: str = " | ", 
                           show_empty: bool = False) -> str:
        """Форматирует таблицу как текст с разделителями"""
        if 'data' not in table_data:
            return ""
        
        lines = []
        for row in table_data['data']:
            # Фильтруем пустые ячейки если нужно
            if not show_empty:
                row = [cell for cell in row if cell.strip()]
            
            if row:  # Если в строке есть данные
                lines.append(separator.join(row))
        
        return "\n".join(lines)
    
    def format_table_as_markdown(self, table_data: Dict[str, Any]) -> str:
        """Форматирует таблицу как Markdown"""
        if 'data' not in table_data:
            return ""
        
        data = table_data['data']
        if not data:
            return ""
        
        lines = []
        
        # Заголовок (первая строка)
        header = [cell if cell.strip() else "—" for cell in data[0]]
        lines.append("| " + " | ".join(header) + " |")
        
        # Разделитель
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        
        # Остальные строки
        for row in data[1:]:
            formatted_row = [cell if cell.strip() else "—" for cell in row]
            # Дополняем строку до нужной длины
            while len(formatted_row) < len(header):
                formatted_row.append("—")
            lines.append("| " + " | ".join(formatted_row[:len(header)]) + " |")
        
        return "\n".join(lines)
    
    def format_payment_document(self, processed_data: Dict[str, Any]) -> str:
        """Специальное форматирование для платежных документов"""
        result = []
        
        # Заголовочная информация
        if 'header_info' in processed_data:
            header = processed_data['header_info']
            if 'organization' in header:
                result.append(f"Организация: {header['organization']}")
            if 'address' in header:
                result.append(f"Адрес: {header['address']}")
            if 'document_type' in header:
                result.append(f"Тип документа: {header['document_type']}")
            result.append("")
        
        # Извлеченные поля
        if 'extracted_fields' in processed_data:
            fields = processed_data['extracted_fields']
            result.append("Реквизиты:")
            if 'inn' in fields:
                result.append(f"  ИНН: {fields['inn']}")
            if 'kpp' in fields:
                result.append(f"  КПП: {fields['kpp']}")
            if 'account' in fields:
                result.append(f"  Счет: {fields['account']}")
            if 'bik' in fields:
                result.append(f"  БИК: {fields['bik']}")
            if 'recipient' in fields:
                result.append(f"  Получатель: {fields['recipient']}")
            if 'bank' in fields:
                result.append(f"  Банк: {fields['bank']}")
            result.append("")
        
        # Таблицы
        if 'tables' in processed_data:
            for i, table in enumerate(processed_data['tables']):
                result.append(f"Таблица {i+1}:")
                result.append(self.format_table_as_text(table, show_empty=False))
                result.append("")
        
        return "\n".join(result)
    
    def extract_key_value_pairs(self, text: str) -> Dict[str, str]:
        """Извлекает пары ключ-значение из текста"""
        pairs = {}
        
        # Паттерны для извлечения
        patterns = [
            r'ИНН\s*:?\s*(\d+)',
            r'КПП\s*:?\s*(\d+)', 
            r'БИК\s*:?\s*(\d+)',
            r'Сч\.\s*№?\s*:?\s*(\d+)',
            r'Счет\s*№?\s*:?\s*(\d+)',
            r'№\s*(\d+)',
            r'от\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
        ]
        
        field_names = ['ИНН', 'КПП', 'БИК', 'Счет', 'Счет', 'Номер', 'Дата']
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                field_name = field_names[i]
                if field_name not in pairs:  # Берем первое найденное значение
                    pairs[field_name] = matches[0]
        
        return pairs
    
    def format_mixed_content(self, text: str, 
                           format_tables: bool = True,
                           extract_fields: bool = True) -> str:
        """Форматирует смешанный контент (текст + XML таблицы)"""
        result = []
        
        # Если есть XML таблицы
        if '<table' in text.lower():
            # Анализируем весь контент
            analysis = analyze_ocr_output(text)
            
            # Добавляем чистый текст
            if 'processed_data' in analysis and 'clean_text' in analysis['processed_data']:
                clean_text = analysis['processed_data']['clean_text']
                result.append("Текст документа:")
                result.append(clean_text)
                result.append("")
            
            # Добавляем извлеченные поля
            if extract_fields and 'processed_data' in analysis and 'fields' in analysis['processed_data']:
                fields = analysis['processed_data']['fields']
                if fields:
                    result.append("Извлеченные данные:")
                    for key, value in fields.items():
                        result.append(f"  {key.upper()}: {value}")
                    result.append("")
            
            # Добавляем таблицы
            if format_tables and 'tables' in analysis:
                for i, table in enumerate(analysis['tables']):
                    result.append(f"Таблица {i+1}:")
                    result.append(self.format_table_as_text(table, show_empty=False))
                    result.append("")
        else:
            # Простой текст без XML
            result.append(text)
            
            # Извлекаем ключевые поля
            if extract_fields:
                pairs = self.extract_key_value_pairs(text)
                if pairs:
                    result.append("")
                    result.append("Извлеченные данные:")
                    for key, value in pairs.items():
                        result.append(f"  {key}: {value}")
        
        return "\n".join(result)


def format_ocr_result(text: str, 
                     format_type: str = "mixed",
                     show_tables: bool = True,
                     show_fields: bool = True) -> str:
    """
    Быстрая функция для форматирования результата OCR
    
    Args:
        text: Текст от OCR
        format_type: Тип форматирования ('mixed', 'clean', 'markdown', 'payment')
        show_tables: Показывать таблицы
        show_fields: Показывать извлеченные поля
    
    Returns:
        Отформатированный текст
    """
    formatter = XMLTableFormatter()
    
    if format_type == "clean":
        # Только чистый текст без XML с правильными пробелами
        clean_text = re.sub(r'<[^>]+>', ' ', text)  # Заменяем теги на пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # Нормализуем пробелы
        return clean_text
    
    elif format_type == "markdown":
        if '<table' in text.lower():
            analysis = analyze_ocr_output(text)
            result = []
            
            if 'tables' in analysis:
                for i, table in enumerate(analysis['tables']):
                    result.append(f"## Таблица {i+1}")
                    result.append(formatter.format_table_as_markdown(table))
                    result.append("")
            
            return "\n".join(result)
        else:
            return text
    
    elif format_type == "payment":
        if '<table' in text.lower():
            analysis = analyze_ocr_output(text)
            return formatter.format_payment_document(analysis)
        else:
            return text
    
    else:  # mixed
        return formatter.format_mixed_content(text, show_tables, show_fields)


if __name__ == "__main__":
    # Тест с реальным примером
    test_text = """<table><tr><td>ИНН 7702000000</td><td>КПП 770201001</td><td></td></tr><tr><td>Получатель</td><td></td><td></td></tr><tr><td>ООО «Бетельгейзе Альфа Центавра-3»</td><td></td><td>Сч. № 40702890123456789012</td></tr><tr><td>Банк получателя</td><td></td><td>БИК 044525225</td></tr><tr><td>Сбербанк России ПАО г. Москва</td><td></td><td>Сч. № 30101810400000000225</td></tr></table> СЧЕТ № 151 от 14 апреля 2021 г. Плательщик: ООО «Бетельгейзе Альфа Центавра-3» Грузополучатель: ООО «Бетельгейзе Аль"""
    
    print("=== Тест форматирования ===")
    
    print("\n1. Смешанный формат:")
    print(format_ocr_result(test_text, "mixed"))
    
    print("\n2. Чистый текст:")
    print(format_ocr_result(test_text, "clean"))
    
    print("\n3. Markdown:")
    print(format_ocr_result(test_text, "markdown"))
    
    print("\n4. Платежный документ:")
    print(format_ocr_result(test_text, "payment"))