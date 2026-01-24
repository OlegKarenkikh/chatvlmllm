"""
XML Table Parser for OCR Model Output
Обработчик XML-таблиц из вывода OCR моделей
"""

import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import json
from dataclasses import dataclass


@dataclass
class TableCell:
    """Ячейка таблицы"""
    content: str
    row: int
    col: int
    colspan: int = 1
    rowspan: int = 1


@dataclass
class ParsedTable:
    """Распарсенная таблица"""
    cells: List[TableCell]
    rows: int
    cols: int
    metadata: Dict[str, Any]


class XMLTableParser:
    """Парсер XML-таблиц из вывода OCR"""
    
    def __init__(self):
        self.table_patterns = [
            r'<table[^>]*>(.*?)</table>',
            r'<TABLE[^>]*>(.*?)</TABLE>'
        ]
    
    def extract_xml_tables(self, text: str) -> List[str]:
        """Извлекает XML-таблицы из текста"""
        tables = []
        
        for pattern in self.table_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                full_table = f"<table>{match}</table>"
                tables.append(full_table)
        
        return tables
    
    def parse_table_xml(self, xml_content: str) -> Optional[ParsedTable]:
        """Парсит XML-таблицу в структурированный формат"""
        try:
            # Очистка и подготовка XML
            xml_content = self._clean_xml(xml_content)
            
            # Парсинг XML
            root = ET.fromstring(xml_content)
            
            cells = []
            max_row = 0
            max_col = 0
            
            # Обработка строк таблицы
            for row_idx, tr in enumerate(root.findall('.//tr')):
                for col_idx, td in enumerate(tr.findall('.//td')):
                    content = self._extract_cell_content(td)
                    
                    # Получение атрибутов ячейки
                    colspan = int(td.get('colspan', 1))
                    rowspan = int(td.get('rowspan', 1))
                    
                    cell = TableCell(
                        content=content,
                        row=row_idx,
                        col=col_idx,
                        colspan=colspan,
                        rowspan=rowspan
                    )
                    cells.append(cell)
                    
                    max_row = max(max_row, row_idx)
                    max_col = max(max_col, col_idx)
            
            return ParsedTable(
                cells=cells,
                rows=max_row + 1,
                cols=max_col + 1,
                metadata={}
            )
            
        except ET.ParseError as e:
            print(f"XML Parse Error: {e}")
            return None
        except Exception as e:
            print(f"Table parsing error: {e}")
            return None
    
    def _clean_xml(self, xml_content: str) -> str:
        """Очищает и исправляет XML"""
        # Удаление лишних пробелов
        xml_content = re.sub(r'\s+', ' ', xml_content.strip())
        
        # Исправление незакрытых тегов
        xml_content = re.sub(r'<td([^>]*)>([^<]*?)(?=<td|</tr|</table|$)', r'<td\1>\2</td>', xml_content)
        xml_content = re.sub(r'<tr([^>]*)>([^<]*?)(?=<tr|</table|$)', r'<tr\1>\2</tr>', xml_content)
        
        # Добавление корневого элемента если нужно
        if not xml_content.startswith('<table'):
            xml_content = f"<table>{xml_content}</table>"
        
        return xml_content
    
    def _extract_cell_content(self, td_element) -> str:
        """Извлекает содержимое ячейки"""
        if td_element.text:
            content = td_element.text.strip()
        else:
            content = ""
        
        # Обработка вложенных элементов
        for child in td_element:
            if child.text:
                content += child.text.strip()
            if child.tail:
                content += child.tail.strip()
        
        return content
    
    def table_to_dataframe(self, parsed_table: ParsedTable) -> pd.DataFrame:
        """Конвертирует таблицу в pandas DataFrame"""
        # Создание матрицы данных
        data_matrix = [["" for _ in range(parsed_table.cols)] for _ in range(parsed_table.rows)]
        
        # Заполнение матрицы
        for cell in parsed_table.cells:
            for r in range(cell.rowspan):
                for c in range(cell.colspan):
                    row_idx = cell.row + r
                    col_idx = cell.col + c
                    if row_idx < parsed_table.rows and col_idx < parsed_table.cols:
                        data_matrix[row_idx][col_idx] = cell.content
        
        return pd.DataFrame(data_matrix)
    
    def table_to_dict(self, parsed_table: ParsedTable) -> Dict[str, Any]:
        """Конвертирует таблицу в словарь"""
        result = {
            "rows": parsed_table.rows,
            "cols": parsed_table.cols,
            "cells": [],
            "data": []
        }
        
        # Добавление информации о ячейках
        for cell in parsed_table.cells:
            result["cells"].append({
                "content": cell.content,
                "row": cell.row,
                "col": cell.col,
                "colspan": cell.colspan,
                "rowspan": cell.rowspan
            })
        
        # Создание матрицы данных
        data_matrix = [["" for _ in range(parsed_table.cols)] for _ in range(parsed_table.rows)]
        
        for cell in parsed_table.cells:
            for r in range(cell.rowspan):
                for c in range(cell.colspan):
                    row_idx = cell.row + r
                    col_idx = cell.col + c
                    if row_idx < parsed_table.rows and col_idx < parsed_table.cols:
                        data_matrix[row_idx][col_idx] = cell.content
        
        result["data"] = data_matrix
        return result


class PaymentDocumentParser(XMLTableParser):
    """Специализированный парсер для платежных документов"""
    
    def __init__(self):
        super().__init__()
        self.payment_fields = {
            'inn': r'ИНН\s*(\d+)',
            'kpp': r'КПП\s*(\d+)',
            'account': r'(?:Сч\.|Счет)\s*№?\s*(\d+)',
            'bik': r'БИК\s*(\d+)',
            'recipient': r'Получатель[:\s]*([^<\n]+)',
            'bank': r'Банк\s+получателя[:\s]*([^<\n]+)'
        }
    
    def parse_payment_document(self, text: str) -> Dict[str, Any]:
        """Парсит платежный документ"""
        result = {
            'header_info': self._extract_header_info(text),
            'tables': [],
            'extracted_fields': self._extract_payment_fields(text)
        }
        
        # Извлечение и парсинг таблиц
        xml_tables = self.extract_xml_tables(text)
        
        for xml_table in xml_tables:
            parsed_table = self.parse_table_xml(xml_table)
            if parsed_table:
                table_dict = self.table_to_dict(parsed_table)
                result['tables'].append(table_dict)
        
        return result
    
    def _extract_header_info(self, text: str) -> Dict[str, str]:
        """Извлекает информацию из заголовка документа"""
        header_info = {}
        
        # Извлечение названия организации
        org_match = re.search(r'ООО\s+[«"]([^»"]+)[»"]', text)
        if org_match:
            header_info['organization'] = org_match.group(0)
        
        # Извлечение адреса
        address_match = re.search(r'Адрес:\s*([^<\n]+)', text)
        if address_match:
            header_info['address'] = address_match.group(1).strip()
        
        # Извлечение типа документа
        doc_type_match = re.search(r'(Образец\s+заполнения\s+[^<\n]+)', text)
        if doc_type_match:
            header_info['document_type'] = doc_type_match.group(1).strip()
        
        return header_info
    
    def _extract_payment_fields(self, text: str) -> Dict[str, str]:
        """Извлекает платежные реквизиты"""
        fields = {}
        
        for field_name, pattern in self.payment_fields.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields[field_name] = match.group(1).strip()
        
        return fields


def analyze_ocr_output(text: str, output_format: str = 'dict') -> Dict[str, Any]:
    """
    Анализирует вывод OCR модели и обрабатывает XML-таблицы
    
    Args:
        text: Текст вывода OCR модели
        output_format: Формат вывода ('dict', 'json', 'dataframe')
    
    Returns:
        Структурированные данные
    """
    # Определение типа документа
    if 'платежн' in text.lower() or 'получатель' in text.lower():
        parser = PaymentDocumentParser()
        result = parser.parse_payment_document(text)
    else:
        parser = XMLTableParser()
        result = {
            'tables': [],
            'raw_text': text
        }
        
        xml_tables = parser.extract_xml_tables(text)
        for xml_table in xml_tables:
            parsed_table = parser.parse_table_xml(xml_table)
            if parsed_table:
                table_dict = parser.table_to_dict(parsed_table)
                result['tables'].append(table_dict)
    
    if output_format == 'json':
        return json.dumps(result, ensure_ascii=False, indent=2)
    elif output_format == 'dataframe' and result.get('tables'):
        # Возвращаем первую таблицу как DataFrame
        parser = XMLTableParser()
        first_table = result['tables'][0]
        # Создаем ParsedTable из словаря для конвертации
        cells = [TableCell(
            content=cell['content'],
            row=cell['row'],
            col=cell['col'],
            colspan=cell['colspan'],
            rowspan=cell['rowspan']
        ) for cell in first_table['cells']]
        
        parsed_table = ParsedTable(
            cells=cells,
            rows=first_table['rows'],
            cols=first_table['cols'],
            metadata={}
        )
        
        return parser.table_to_dataframe(parsed_table)
    
    return result


if __name__ == "__main__":
    # Тестовый пример
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
    
    result = analyze_ocr_output(test_text)
    print(json.dumps(result, ensure_ascii=False, indent=2))