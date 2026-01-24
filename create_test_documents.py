#!/usr/bin/env python3
"""
Создание разнообразных тестовых документов для проверки производительности и точности OCR
"""

from PIL import Image, ImageDraw, ImageFont
import os
import random

def create_test_documents():
    """Создание различных типов тестовых документов"""
    
    # Создание папки для тестов
    os.makedirs("test_documents", exist_ok=True)
    
    # Попытка загрузить разные шрифты
    fonts = []
    font_paths = [
        "arial.ttf", "times.ttf", "calibri.ttf", 
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/times.ttf", 
        "C:/Windows/Fonts/calibri.ttf"
    ]
    
    for font_path in font_paths:
        try:
            fonts.append(ImageFont.truetype(font_path, 20))
            break
        except:
            continue
    
    if not fonts:
        fonts = [ImageFont.load_default()]
    
    font = fonts[0]
    
    # 1. Простой текстовый документ
    create_simple_text_document(font)
    
    # 2. Документ с таблицей
    create_table_document(font)
    
    # 3. Многоколоночный документ
    create_multicolumn_document(font)
    
    # 4. Документ с числами и формулами
    create_numbers_document(font)
    
    # 5. Смешанный документ (текст + числа + символы)
    create_mixed_document(font)
    
    # 6. Документ низкого качества (имитация скана)
    create_low_quality_document(font)
    
    # 7. Документ с разными размерами шрифта
    create_multi_size_document()
    
    print("✅ Все тестовые документы созданы в папке test_documents/")

def create_simple_text_document(font):
    """Простой текстовый документ"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    text = """ТЕСТОВЫЙ ДОКУМЕНТ №1
    
Это простой текстовый документ для проверки базовой функциональности OCR.
Документ содержит обычный текст на русском и английском языках.

This is a simple text document for testing basic OCR functionality.
The document contains regular text in Russian and English languages.

Основные характеристики:
- Четкий шрифт
- Хороший контраст
- Стандартный размер текста
- Простая структура

Key features:
- Clear font
- Good contrast  
- Standard text size
- Simple structure"""
    
    y_position = 50
    for line in text.split('\n'):
        draw.text((50, y_position), line.strip(), fill='black', font=font)
        y_position += 25
    
    img.save("test_documents/01_simple_text.png")

def create_table_document(font):
    """Документ с таблицей"""
    img = Image.new('RGB', (900, 700), color='white')
    draw = ImageDraw.Draw(img)
    
    # Заголовок
    draw.text((50, 30), "ТАБЛИЦА ПРОДАЖ ЗА 2024 ГОД", fill='black', font=font)
    
    # Таблица
    table_data = [
        ["Месяц", "Продажи", "Прибыль", "Рост %"],
        ["Январь", "150,000", "45,000", "+12.5%"],
        ["Февраль", "165,000", "52,000", "+10.0%"],
        ["Март", "180,000", "58,000", "+9.1%"],
        ["Апрель", "195,000", "63,000", "+8.3%"],
        ["Май", "210,000", "68,000", "+7.7%"],
        ["Июнь", "225,000", "74,000", "+7.1%"]
    ]
    
    x_start = 50
    y_start = 80
    col_widths = [120, 120, 120, 100]
    
    for row_idx, row in enumerate(table_data):
        y_pos = y_start + row_idx * 40
        
        # Рисуем границы строки
        draw.rectangle([x_start, y_pos, x_start + sum(col_widths), y_pos + 35], 
                      outline='black', width=1)
        
        x_pos = x_start
        for col_idx, cell in enumerate(row):
            # Рисуем границы колонки
            draw.line([x_pos, y_pos, x_pos, y_pos + 35], fill='black', width=1)
            
            # Заголовки жирным (имитация)
            if row_idx == 0:
                draw.text((x_pos + 5, y_pos + 8), cell, fill='black', font=font)
                draw.text((x_pos + 6, y_pos + 8), cell, fill='black', font=font)  # Имитация жирного
            else:
                draw.text((x_pos + 5, y_pos + 8), cell, fill='black', font=font)
            
            x_pos += col_widths[col_idx]
    
    # Итоги
    draw.text((50, y_start + len(table_data) * 40 + 30), 
              "ИТОГО: 1,125,000 руб. | Средний рост: +9.1%", fill='black', font=font)
    
    img.save("test_documents/02_table.png")

def create_multicolumn_document(font):
    """Многоколоночный документ"""
    img = Image.new('RGB', (1000, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Заголовок
    draw.text((50, 30), "НОВОСТИ ТЕХНОЛОГИЙ", fill='black', font=font)
    
    # Левая колонка
    left_text = """ИСКУССТВЕННЫЙ ИНТЕЛЛЕКТ

Развитие ИИ продолжает 
ускоряться. Новые модели 
показывают впечатляющие 
результаты в обработке 
естественного языка.

Основные достижения:
• GPT-4 и аналоги
• Мультимодальные модели  
• Автономные системы
• Робототехника

Применение ИИ расширяется
во всех сферах жизни."""
    
    # Правая колонка
    right_text = """КВАНТОВЫЕ КОМПЬЮТЕРЫ

Квантовые вычисления 
приближаются к практическому
применению. IBM и Google 
демонстрируют прорывы.

Ключевые направления:
• Криптография
• Оптимизация
• Моделирование
• Машинное обучение

Ожидается коммерциализация
в ближайшие 5-10 лет."""
    
    # Рисуем колонки
    y_pos = 80
    for line in left_text.split('\n'):
        draw.text((50, y_pos), line.strip(), fill='black', font=font)
        y_pos += 25
    
    y_pos = 80
    for line in right_text.split('\n'):
        draw.text((520, y_pos), line.strip(), fill='black', font=font)
        y_pos += 25
    
    # Разделительная линия
    draw.line([500, 70, 500, 600], fill='gray', width=2)
    
    img.save("test_documents/03_multicolumn.png")

def create_numbers_document(font):
    """Документ с числами и формулами"""
    img = Image.new('RGB', (800, 700), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 30), "ФИНАНСОВЫЙ ОТЧЕТ", fill='black', font=font)
    
    content = """БАЛАНС НА 31.12.2024

АКТИВЫ:
Денежные средства: 1,250,000.00 руб.
Дебиторская задолженность: 850,000.00 руб.
Товарно-материальные запасы: 2,100,000.00 руб.
Основные средства: 5,500,000.00 руб.
ИТОГО АКТИВЫ: 9,700,000.00 руб.

ПАССИВЫ:
Уставный капитал: 3,000,000.00 руб.
Нераспределенная прибыль: 4,200,000.00 руб.
Кредиторская задолженность: 2,500,000.00 руб.
ИТОГО ПАССИВЫ: 9,700,000.00 руб.

КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ:
ROE = 15.8%
ROA = 12.3%
Коэффициент ликвидности = 1.85
Долг/Капитал = 0.34

ФОРМУЛЫ:
ROE = (Чистая прибыль / Собственный капитал) × 100%
ROA = (Чистая прибыль / Активы) × 100%
Ликвидность = Оборотные активы / Краткосрочные обязательства"""
    
    y_pos = 80
    for line in content.split('\n'):
        draw.text((50, y_pos), line.strip(), fill='black', font=font)
        y_pos += 25
    
    img.save("test_documents/04_numbers.png")

def create_mixed_document(font):
    """Смешанный документ с разным контентом"""
    img = Image.new('RGB', (900, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    content = """ДОГОВОР ПОСТАВКИ №12345 от 15.01.2024

ПОСТАВЩИК: ООО "Технологии Будущего"
ИНН: 7701234567, КПП: 770101001
Адрес: 123456, г. Москва, ул. Инновационная, д. 10

ПОКУПАТЕЛЬ: АО "Прогресс Плюс"  
ИНН: 7702345678, КПП: 770201001
Адрес: 654321, г. Санкт-Петербург, пр. Технологический, д. 25

ПРЕДМЕТ ДОГОВОРА:
1. Серверы Dell PowerEdge R750 - 5 шт. × 450,000 = 2,250,000 руб.
2. Коммутаторы Cisco Catalyst 9300 - 3 шт. × 180,000 = 540,000 руб.
3. СХД NetApp FAS2750 - 1 шт. × 850,000 = 850,000 руб.

ИТОГО: 3,640,000 (Три миллиона шестьсот сорок тысяч) рублей
НДС 20%: 728,000 руб.
К ДОПЛАТЕ: 4,368,000 руб.

СРОКИ: Поставка до 28.02.2024
ОПЛАТА: 50% предоплата, 50% по факту поставки

Подписи сторон:
Поставщик: _________________ /И.И. Иванов/
Покупатель: ________________ /П.П. Петров/

М.П.                                    М.П."""
    
    y_pos = 50
    for line in content.split('\n'):
        draw.text((50, y_pos), line.strip(), fill='black', font=font)
        y_pos += 22
    
    img.save("test_documents/05_mixed.png")

def create_low_quality_document(font):
    """Документ низкого качества (имитация плохого скана)"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Добавляем шум
    for _ in range(1000):
        x = random.randint(0, 799)
        y = random.randint(0, 599)
        draw.point((x, y), fill='lightgray')
    
    # Слегка наклоненный текст (имитация плохого скана)
    content = """СПРАВКА О ДОХОДАХ

Выдана: Петрову Петру Петровичу
Должность: Ведущий специалист
Период: январь-декабрь 2024 г.

Заработная плата: 1,200,000 руб.
Премии: 180,000 руб.
Компенсации: 45,000 руб.

ИТОГО доход: 1,425,000 руб.

Справка выдана для предоставления
в банк для получения кредита.

Дата: 20.01.2025
Подпись: _______________"""
    
    y_pos = 80
    for line in content.split('\n'):
        # Добавляем небольшой случайный сдвиг для имитации плохого качества
        x_offset = random.randint(-3, 3)
        draw.text((50 + x_offset, y_pos), line.strip(), fill='darkgray', font=font)
        y_pos += 25
    
    img.save("test_documents/06_low_quality.png")

def create_multi_size_document():
    """Документ с разными размерами шрифта"""
    img = Image.new('RGB', (800, 700), color='white')
    draw = ImageDraw.Draw(img)
    
    # Разные размеры шрифтов
    try:
        font_large = ImageFont.truetype("arial.ttf", 32)
        font_medium = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Заголовок крупным шрифтом
    draw.text((50, 30), "ОБЪЯВЛЕНИЕ", fill='black', font=font_large)
    
    # Основной текст средним шрифтом
    draw.text((50, 100), "Продается квартира в центре города", fill='black', font=font_medium)
    draw.text((50, 130), "3 комнаты, 85 кв.м, 5/9 этаж", fill='black', font=font_medium)
    draw.text((50, 160), "Цена: 12,500,000 рублей", fill='black', font=font_medium)
    
    # Детали мелким шрифтом
    details = """Подробности:
- Кирпичный дом 2010 года постройки
- Евроремонт, мебель остается
- Рядом метро, школы, магазины
- Документы готовы, один собственник
- Возможна ипотека, материнский капитал
- Торг уместен при быстрой сделке"""
    
    y_pos = 220
    for line in details.split('\n'):
        draw.text((50, y_pos), line.strip(), fill='black', font=font_small)
        y_pos += 18
    
    # Контакты средним шрифтом
    draw.text((50, 400), "Контакты:", fill='black', font=font_medium)
    draw.text((50, 430), "Телефон: +7 (495) 123-45-67", fill='black', font=font_medium)
    draw.text((50, 460), "Email: realty@example.com", fill='black', font=font_medium)
    
    img.save("test_documents/07_multi_size.png")

if __name__ == "__main__":
    create_test_documents()