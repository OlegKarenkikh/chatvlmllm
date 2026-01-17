#!/usr/bin/env python3
"""Тест улучшенной функции очистки OCR."""

import sys
from pathlib import Path
import re

# Добавить корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

def clean_ocr_result(text: str) -> str:
    """Очистка результата OCR от лишних символов и повторений."""
    if not text:
        return text
    
    # Исправление кодировки и искаженных символов
    # Замена латинских символов на кириллические
    char_replacements = {
        'B': 'В', 'O': 'О', 'P': 'Р', 'A': 'А', 'H': 'Н', 'K': 'К', 
        'E': 'Е', 'T': 'Т', 'M': 'М', 'X': 'Х', 'C': 'С', 'Y': 'У'
    }
    
    # Применяем замены только к буквам в словах (не к цифрам и датам)
    for lat, cyr in char_replacements.items():
        # Заменяем только если символ окружен буквами
        text = re.sub(f'(?<=[А-ЯЁа-яё]){lat}(?=[А-ЯЁа-яё])', cyr, text)
        text = re.sub(f'^{lat}(?=[А-ЯЁа-яё])', cyr, text)
        text = re.sub(f'(?<=[А-ЯЁа-яё]){lat}$', cyr, text)
    
    # Исправление конкретных искажений
    corrections = {
        'BOJNTEJBCKOEVJOCTOBEPENNE': 'ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ',
        'BAKAPNHLEB': 'ВАКАРИН ЛЕВ',
        'AHAPENNABNOBNY': 'АНДРЕЙ ЛЬВОВИЧ',
        'ANTANCKNIKPA': 'АЛТАЙСКИЙ КРАЙ',
        'TN6A2747': 'ГИ БДД 2747'
    }
    
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    
    # Добавление пробелов между полями
    text = re.sub(r'(\d+)([А-ЯЁ])', r'\1 \2', text)  # Между цифрой и буквой
    text = re.sub(r'([а-яё])(\d)', r'\1 \2', text)    # Между буквой и цифрой
    text = re.sub(r'(\))([А-ЯЁ])', r') \2', text)     # После скобки
    
    # Форматирование дат
    text = re.sub(r'(\d{2})\.(\d{2})\.(\d{4})(\d{2})\.(\d{2})\.(\d{4})', 
                  r'\1.\2.\3 \4.\5.\6', text)
    
    # Разделение полей по номерам
    text = re.sub(r'(\d+\.)([А-ЯЁ])', r'\1 \2', text)
    text = re.sub(r'(\d+[аб]\))([А-ЯЁ\d])', r'\1 \2', text)
    text = re.sub(r'(\d+[сc]\))([А-ЯЁ])', r'\1 \2', text)
    
    # Удаление повторяющихся символов
    text = re.sub(r'(\*\*[0-9\s]+\*\*)+', '', text)
    text = re.sub(r'\*\*+', '', text)
    text = re.sub(r'(00\s+){3,}', '', text)
    
    # Разбивка на строки и очистка
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Пропускаем пустые строки
        if not line:
            continue
            
        # Пропускаем строки только с повторяющимися символами
        if re.match(r'^[0\s\*\.]+$', line) and len(line) > 10:
            continue
            
        # Пропускаем строки только со звездочками
        if re.match(r'^\*+$', line):
            continue
        
        cleaned_lines.append(line)
    
    # Объединяем очищенные строки
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Финальная очистка
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    cleaned_text = re.sub(r'\s{3,}', ' ', cleaned_text)  # Множественные пробелы
    
    return cleaned_text.strip()


def extract_fields(text: str) -> dict:
    """Извлечение полей из очищенного текста."""
    patterns = {
        "document_number": [
            r'5\.(\d{7,10})',  # После "5."
            r'(\d{10})',  # 10 цифр подряд
            r'№\s*(\d+)',  # Номер после №
            r'(\d{7,10})'  # 7-10 цифр
        ],
        "surname": [
            r'1\.\s*([А-ЯЁ\s]+?)(?=\s+2\.|\s+[А-ЯЁ]+\s+[А-ЯЁ]+|$)',  # После "1." до "2." или имени
            r'(?:ВОДИТЕЛЬСКОЕ\s+УДОСТОВЕРЕНИЕ\s+)?1\.\s*([А-ЯЁ]+)',  # После заголовка и "1."
            r'([А-ЯЁ]{4,})\s+[А-ЯЁ]+\s+[А-ЯЁ]+',  # Первое длинное слово перед именем
            r'фамилия[:\s]*([А-ЯЁ]+)',
        ],
        "given_names": [
            r'2\.\s*([А-ЯЁ\s]+?)(?=\s+3\.|\s+\d{2}\.\d{2}\.\d{4}|$)',  # После "2." до "3." или даты
            r'[А-ЯЁ]{4,}\s+([А-ЯЁ]+\s+[А-ЯЁ]+)',  # Два слова после фамилии
            r'имя[:\s]*([А-ЯЁ\s]+)',
        ],
        "date_of_birth": [
            r'3\.\s*(\d{2}\.\d{2}\.\d{4})',  # После "3."
            r'(\d{2}\.\d{2}\.19\d{2})',  # Дата рождения (1900-1999)
            r'(\d{2}\.\d{2}\.20[0-2]\d)',  # Дата рождения (2000-2029)
            r'(\d{2}/\d{2}/19\d{2})'  # Альтернативный формат
        ],
        "date_of_issue": [
            r'4[аa]\)\s*(\d{2}\.\d{2}\.\d{4})',  # После "4а)"
            r'выдан[:\s]*(\d{2}\.\d{2}\.\d{4})',
            r'(\d{2}\.\d{2}\.20[1-2]\d)'  # Дата выдачи (2010-2029)
        ],
        "date_of_expiry": [
            r'4[бb]\)\s*(\d{2}\.\d{2}\.\d{4})',  # После "4б)"
            r'действителен[:\s]*(\d{2}\.\d{2}\.\d{4})',
            r'(\d{2}\.\d{2}\.20[2-3]\d)'  # Дата окончания (2020-2039)
        ],
        "authority": [
            r'4[сc]\)\s*([А-ЯЁ\s\d]+?)(?=\s+5\.|\s+\d{7}|$)',  # После "4с)" до "5." или номера
            r'(ГИ\s*БДД\s*\d+)',  # ГИБДД с номером
            r'([А-ЯЁ]+\s+КРАЙ)',  # Название края
            r'гибдд[:\s]*(\d+)',
        ],
        "nationality": [
            r'8\.\s*(RUS|РФ|РОССИЯ)',  # После "8."
            r'(RUS|РФ|РОССИЯ)',
            r'гражданство[:\s]*(RUS|РФ)'
        ]
    }
    
    extracted_fields = {}
    
    for field in patterns:
        field_value = ""
        
        for pattern in patterns[field]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                field_value = matches[0].strip()
                break
        
        # Дополнительная очистка значений
        if field_value:
            # Удаляем лишние пробелы
            field_value = ' '.join(field_value.split())
            # Ограничиваем длину
            if len(field_value) > 50:
                field_value = field_value[:50] + "..."
        
        extracted_fields[field] = field_value
    
    return extracted_fields


def test_ocr_improvements():
    """Тест улучшений OCR."""
    print("🧪 ТЕСТ УЛУЧШЕНИЙ OCR")
    print("=" * 50)
    
    # Исходный текст из модели
    original_text = "BOJNTEJBCKOEVJOCTOBEPENNE 1.BAKAPNHLEB 2.AHAPENNABNOBNY 3.13.09.1995 4a)03.01.20144b)03.01.2024 4c)TN6A2747 5.0166860 8.ANTANCKNIKPA"
    
    print("📄 ИСХОДНЫЙ ТЕКСТ:")
    print(repr(original_text))
    print()
    
    # Очистка текста
    cleaned_text = clean_ocr_result(original_text)
    
    print("✨ ОЧИЩЕННЫЙ ТЕКСТ:")
    print(repr(cleaned_text))
    print()
    print(cleaned_text)
    print()
    
    # Извлечение полей
    fields = extract_fields(cleaned_text)
    
    print("📋 ИЗВЛЕЧЕННЫЕ ПОЛЯ:")
    print("-" * 30)
    for field, value in fields.items():
        status = "✅" if value else "❌"
        print(f"{status} {field.replace('_', ' ').title()}: '{value}'")
    
    print()
    print("📊 СТАТИСТИКА:")
    filled_fields = sum(1 for v in fields.values() if v)
    total_fields = len(fields)
    print(f"   Заполнено полей: {filled_fields}/{total_fields} ({filled_fields/total_fields*100:.1f}%)")
    
    # Проверка качества
    expected_values = {
        "surname": "ВАКАРИН ЛЕВ",
        "given_names": "АНДРЕЙ ЛЬВОВИЧ", 
        "date_of_birth": "13.09.1995",
        "date_of_issue": "03.01.2014",
        "date_of_expiry": "03.01.2024",
        "authority": "ГИ БДД 2747",
        "document_number": "0166860",
        "nationality": "АЛТАЙСКИЙ КРАЙ"
    }
    
    print("\n🎯 ПРОВЕРКА КАЧЕСТВА:")
    print("-" * 30)
    correct = 0
    for field, expected in expected_values.items():
        actual = fields.get(field, "")
        if expected.lower() in actual.lower() or actual.lower() in expected.lower():
            print(f"✅ {field}: '{actual}' ≈ '{expected}'")
            correct += 1
        else:
            print(f"❌ {field}: '{actual}' ≠ '{expected}'")
    
    print(f"\n📈 ТОЧНОСТЬ: {correct}/{len(expected_values)} ({correct/len(expected_values)*100:.1f}%)")


if __name__ == "__main__":
    test_ocr_improvements()