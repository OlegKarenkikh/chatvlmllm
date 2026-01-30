# Руководство по обработке XML-таблиц в OCR

## Обзор

Система обработки XML-таблиц позволяет автоматически анализировать и структурировать вывод OCR моделей, содержащий XML-разметку таблиц. Особенно полезно для обработки платежных документов, счетов-фактур и других структурированных документов.

## Основные компоненты

### 1. XMLTableParser
Базовый парсер для обработки XML-таблиц.

```python
from utils.xml_table_parser import XMLTableParser

parser = XMLTableParser()

# Извлечение XML-таблиц из текста
xml_tables = parser.extract_xml_tables(text)

# Парсинг конкретной таблицы
parsed_table = parser.parse_table_xml(xml_table)

# Конвертация в DataFrame
df = parser.table_to_dataframe(parsed_table)

# Конвертация в словарь
table_dict = parser.table_to_dict(parsed_table)
```

### 2. PaymentDocumentParser
Специализированный парсер для платежных документов.

```python
from utils.xml_table_parser import PaymentDocumentParser

parser = PaymentDocumentParser()
result = parser.parse_payment_document(text)

# Результат содержит:
# - header_info: информация из заголовка
# - tables: структурированные таблицы
# - extracted_fields: извлеченные реквизиты (ИНН, КПП, БИК и т.д.)
```

### 3. OCROutputProcessor
Комплексный процессор для обработки вывода OCR.

```python
from utils.ocr_output_processor import OCROutputProcessor

processor = OCROutputProcessor()

result = processor.process_ocr_output(
    text=ocr_text,
    model_name="dots_ocr",
    extract_tables=True,
    extract_fields=True,
    output_format='structured'
)
```

## Интеграция с OCR моделями

### Обновленная модель dots.ocr

Модель `DotsOCRFinalModel` теперь поддерживает автоматическую обработку XML-таблиц:

```python
from models.dots_ocr_final import DotsOCRFinalModel

# Инициализация с поддержкой XML
config = {
    'model_name': 'ucaslcl/GOT-OCR2_0',
    'process_xml_tables': True,
    'extract_structured_fields': True
}

model = DotsOCRFinalModel(config)
model.load_model()

# Обработка изображения с автоматическим извлечением таблиц
result = model.process_image(image, mode="table_extraction")

# Для платежных документов
payment_data = model.extract_payment_document(image)

# Экспорт данных
model.export_table_data(image, "output.xlsx")
```

## Примеры использования

### 1. Базовая обработка XML-таблицы

```python
from utils.xml_table_parser import analyze_ocr_output

# Текст с XML-таблицей
text = """ООО «Компания»
<table>
<tr><td>ИНН 1234567890</td><td>КПП 123456789</td></tr>
<tr><td>Получатель</td><td>Сч. № 40702810000000000000</td></tr>
</table>"""

# Анализ
result = analyze_ocr_output(text, output_format='dict')
print(result)
```

### 2. Обработка платежного документа

```python
from utils.xml_table_parser import PaymentDocumentParser

payment_text = """ООО «Бетельгейзе Альфа Центавра-3»
Адрес: 100001, г. Москва, Веселый проспект, дом 13, офис 13
Образец заполнения платежного поручения
<table>
<tr><td>ИНН 7702000000</td><td>КПП 770201001</td><td></td></tr>
<tr><td>Получатель</td><td></td><td>Сч. №</td></tr>
<tr><td>ООО «Бетельгейзе Альфа Центавра-3»</td><td></td><td>40702890123456789012</td></tr>
</table>"""

parser = PaymentDocumentParser()
result = parser.parse_payment_document(payment_text)

# Извлеченные данные
print("Организация:", result['header_info'].get('organization'))
print("ИНН:", result['extracted_fields'].get('inn'))
print("Счет:", result['extracted_fields'].get('account'))
```

### 3. Экспорт в Excel

```python
from utils.ocr_output_processor import OCROutputProcessor

processor = OCROutputProcessor()
result = processor.process_ocr_output(text, "model_name")

# Экспорт таблиц в Excel
success = processor.export_tables_to_excel(result, "tables.xlsx")
```

### 4. API использование

```bash
# Обработка текста через API
curl -X POST http://localhost:5000/process_text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ООО «Тест» <table><tr><td>ИНН 1234567890</td></tr></table>",
    "model_name": "dots_ocr",
    "output_format": "structured"
  }'

# Специализированная обработка платежного документа
curl -X POST http://localhost:5000/process_payment_document \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Платежное поручение <table>...</table>"
  }'

# Экспорт таблиц
curl -X POST http://localhost:5000/export_tables \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Документ с таблицей <table>...</table>",
    "format": "excel"
  }' \
  --output tables.xlsx
```

## Структура результата

### Структурированный формат

```json
{
  "model_name": "dots_ocr",
  "document_type": "payment",
  "has_xml_tables": true,
  "raw_text": "...",
  "processed_data": {
    "tables": [
      {
        "table_id": 0,
        "rows": 3,
        "cols": 3,
        "cells": [...],
        "data": [
          ["ИНН 7702000000", "КПП 770201001", ""],
          ["Получатель", "", "Сч. №"],
          ["ООО «Компания»", "", "40702890123456789012"]
        ],
        "analysis": {
          "has_numbers": true,
          "has_dates": false,
          "has_currency": false,
          "fill_rate": 0.67,
          "key_fields": ["инн", "кпп", "счет"]
        }
      }
    ],
    "fields": {
      "inn": "7702000000",
      "kpp": "770201001",
      "account": "40702890123456789012"
    },
    "clean_text": "ООО «Компания» ИНН 7702000000 КПП 770201001..."
  }
}
```

### Упрощенный формат

```json
{
  "document_type": "payment",
  "text": "Очищенный текст без XML",
  "tables": [
    {
      "rows": 3,
      "cols": 3,
      "data": [...]
    }
  ],
  "fields": {
    "inn": "7702000000",
    "kpp": "770201001"
  }
}
```

## Поддерживаемые типы документов

1. **Платежные документы** (`payment`)
   - Платежные поручения
   - Банковские документы
   - Извлекает: ИНН, КПП, БИК, номера счетов

2. **Счета-фактуры** (`invoice`)
   - Накладные
   - Счета
   - Извлекает: суммы, НДС, реквизиты

3. **Паспорта** (`passport`)
   - Документы удостоверения личности
   - Извлекает: серия, номер, дата выдачи

4. **Договоры** (`contract`)
   - Соглашения
   - Контракты
   - Извлекает: стороны, даты, суммы

## Настройки и конфигурация

### Конфигурация OCR модели

```python
config = {
    'model_name': 'ucaslcl/GOT-OCR2_0',
    'process_xml_tables': True,        # Включить обработку XML
    'extract_structured_fields': True, # Извлекать поля
    'max_new_tokens': 2048
}
```

### Настройки процессора

```python
processor = OCROutputProcessor()

result = processor.process_ocr_output(
    text=text,
    model_name="dots_ocr",
    extract_tables=True,      # Извлекать таблицы
    extract_fields=True,      # Извлекать поля
    output_format='structured' # Формат: structured, json, simple
)
```

## Тестирование

Запуск тестов:

```bash
python test_xml_table_processing.py
```

Тесты включают:
- Парсинг XML-таблиц
- Обработка платежных документов
- Экспорт данных
- API функциональность

## API сервер

Запуск API сервера:

```bash
python api_xml_table_example.py
```

Доступные эндпоинты:
- `GET /health` - проверка состояния
- `POST /process_text` - обработка текста
- `POST /process_payment_document` - платежные документы
- `POST /extract_tables` - извлечение таблиц
- `POST /export_tables` - экспорт данных
- `POST /analyze_document_type` - анализ типа документа
- `POST /batch_process` - пакетная обработка

## Ограничения и рекомендации

1. **Качество XML**: Система пытается исправить некорректный XML, но лучше работает с правильно сформированными таблицами.

2. **Размер таблиц**: Оптимально работает с таблицами до 20x20 ячеек.

3. **Кодировка**: Поддерживает UTF-8, корректно обрабатывает русский текст.

4. **Память**: При обработке больших документов рекомендуется мониторить использование памяти.

5. **Производительность**: Для пакетной обработки используйте соответствующий API эндпоинт.

## Примеры интеграции

### С Streamlit

```python
import streamlit as st
from utils.ocr_output_processor import process_ocr_text

st.title("Обработка OCR с XML-таблицами")

text_input = st.text_area("Введите текст OCR:")
if st.button("Обработать"):
    result = process_ocr_text(text_input, "streamlit", "structured")
    
    if result.get('processed_data', {}).get('tables'):
        st.subheader("Найденные таблицы:")
        for i, table in enumerate(result['processed_data']['tables']):
            st.write(f"Таблица {i+1}: {table['rows']}x{table['cols']}")
            st.dataframe(table['data'])
```

### С FastAPI

```python
from fastapi import FastAPI
from utils.ocr_output_processor import process_ocr_text

app = FastAPI()

@app.post("/process")
async def process_ocr(text: str):
    result = process_ocr_text(text, "fastapi", "structured")
    return result
```

## Заключение

Система обработки XML-таблиц значительно расширяет возможности OCR моделей, позволяя автоматически структурировать и анализировать табличные данные. Особенно эффективна для обработки финансовых и юридических документов с четкой структурой.