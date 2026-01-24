"""
Пример API для обработки XML-таблиц в OCR
"""

from flask import Flask, request, jsonify, send_file
from PIL import Image
import io
import json
import os
import tempfile
from datetime import datetime
import sys

# Добавляем пути
sys.path.append('.')
sys.path.append('./models')
sys.path.append('./utils')

from utils.ocr_output_processor import OCROutputProcessor, process_ocr_text
from utils.xml_table_parser import XMLTableParser, PaymentDocumentParser

app = Flask(__name__)

# Глобальный процессор
ocr_processor = OCROutputProcessor()


@app.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'xml_processor_available': True
    })


@app.route('/process_text', methods=['POST'])
def process_text():
    """Обработка текста OCR с XML-таблицами"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        model_name = data.get('model_name', 'api_request')
        output_format = data.get('output_format', 'structured')
        extract_tables = data.get('extract_tables', True)
        extract_fields = data.get('extract_fields', True)
        
        # Обработка текста
        result = ocr_processor.process_ocr_output(
            text=text,
            model_name=model_name,
            extract_tables=extract_tables,
            extract_fields=extract_fields,
            output_format=output_format
        )
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/process_payment_document', methods=['POST'])
def process_payment_document():
    """Специализированная обработка платежных документов"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        
        # Используем специализированный парсер
        parser = PaymentDocumentParser()
        result = parser.parse_payment_document(text)
        
        return jsonify({
            'success': True,
            'document_type': 'payment_document',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/extract_tables', methods=['POST'])
def extract_tables():
    """Извлечение только таблиц из текста"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        
        # Используем XML парсер
        parser = XMLTableParser()
        xml_tables = parser.extract_xml_tables(text)
        
        tables_data = []
        for i, xml_table in enumerate(xml_tables):
            parsed_table = parser.parse_table_xml(xml_table)
            if parsed_table:
                table_dict = parser.table_to_dict(parsed_table)
                table_dict['table_id'] = i
                tables_data.append(table_dict)
        
        return jsonify({
            'success': True,
            'tables_count': len(tables_data),
            'tables': tables_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/export_tables', methods=['POST'])
def export_tables():
    """Экспорт таблиц в файл"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        export_format = data.get('format', 'json')  # json, excel
        
        # Обработка текста
        result = ocr_processor.process_ocr_output(text, "api_export")
        
        # Создание временного файла
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{export_format}') as tmp_file:
            tmp_filename = tmp_file.name
        
        # Экспорт в зависимости от формата
        if export_format == 'excel' or export_format == 'xlsx':
            success = ocr_processor.export_tables_to_excel(result, tmp_filename)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:  # JSON по умолчанию
            success = ocr_processor.export_to_json(result, tmp_filename)
            mimetype = 'application/json'
        
        if success and os.path.exists(tmp_filename):
            return send_file(
                tmp_filename,
                as_attachment=True,
                download_name=f'tables_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{export_format}',
                mimetype=mimetype
            )
        else:
            return jsonify({'error': 'Export failed'}), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/analyze_document_type', methods=['POST'])
def analyze_document_type():
    """Анализ типа документа"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        text = data['text']
        
        # Определяем тип документа
        doc_type = ocr_processor._detect_document_type(text)
        has_xml = ocr_processor._has_xml_tables(text)
        
        # Извлекаем XML таблицы для анализа
        parser = XMLTableParser()
        xml_tables = parser.extract_xml_tables(text)
        
        analysis = {
            'document_type': doc_type,
            'has_xml_tables': has_xml,
            'xml_tables_count': len(xml_tables),
            'text_length': len(text),
            'contains_numbers': bool(re.search(r'\d+', text)),
            'contains_dates': bool(re.search(r'\d{1,2}[./]\d{1,2}[./]\d{2,4}', text)),
            'language': 'ru' if any(c in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for c in text.lower()) else 'en'
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/batch_process', methods=['POST'])
def batch_process():
    """Пакетная обработка нескольких текстов"""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({'error': 'Texts array is required'}), 400
        
        texts = data['texts']
        if not isinstance(texts, list):
            return jsonify({'error': 'Texts must be an array'}), 400
        
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = process_ocr_text(text, f"batch_item_{i}", "structured")
                results.append({
                    'index': i,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'processed_count': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Добавляем импорт для regex
import re


if __name__ == '__main__':
    print("🚀 Запуск API для обработки XML-таблиц OCR")
    print("Доступные эндпоинты:")
    print("  GET  /health - проверка состояния")
    print("  POST /process_text - обработка текста OCR")
    print("  POST /process_payment_document - обработка платежных документов")
    print("  POST /extract_tables - извлечение таблиц")
    print("  POST /export_tables - экспорт таблиц")
    print("  POST /analyze_document_type - анализ типа документа")
    print("  POST /batch_process - пакетная обработка")
    print("\nПример запроса:")
    print("""
curl -X POST http://localhost:5000/process_text \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "ООО «Тест» <table><tr><td>ИНН 1234567890</td></tr></table>",
    "model_name": "dots_ocr",
    "output_format": "structured"
  }'
    """)
    
    app.run(host='0.0.0.0', port=5000, debug=True)