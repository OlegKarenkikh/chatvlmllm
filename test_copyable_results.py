"""
Тест возможности копирования результатов и форматирования
"""

from utils.xml_formatter import format_ocr_result
import sys

# Реальный пример от пользователя
real_example = """<table><tr><td>ИНН 7702000000</td><td>КПП 770201001</td><td></td></tr><tr><td>Получатель</td><td></td><td></td></tr><tr><td>ООО «Бетельгейзе Альфа Центавра-3»</td><td></td><td>Сч. № 40702890123456789012</td></tr><tr><td>Банк получателя</td><td></td><td>БИК 044525225</td></tr><tr><td>Сбербанк России ПАО г. Москва</td><td></td><td>Сч. № 30101810400000000225</td></tr></table> СЧЕТ № 151 от 14 апреля 2021 г. Плательщик: ООО «Бетельгейзе Альфа Центавра-3» Грузополучатель: ООО «Бетельгейзе Аль"""

def test_formatting_options():
    """Тестирует различные варианты форматирования"""
    
    print("🔍 ТЕСТИРОВАНИЕ ФОРМАТИРОВАНИЯ РЕЗУЛЬТАТОВ OCR")
    print("=" * 60)
    
    print("\n📋 ИСХОДНЫЙ ТЕКСТ:")
    print("-" * 40)
    print(real_example)
    
    print("\n\n✨ ВАРИАНТЫ ФОРМАТИРОВАНИЯ:")
    print("=" * 60)
    
    # 1. Чистый текст для копирования
    print("\n1️⃣ ЧИСТЫЙ ТЕКСТ (для копирования):")
    print("-" * 40)
    clean_text = format_ocr_result(real_example, "clean")
    print(clean_text)
    
    # 2. Смешанный формат
    print("\n2️⃣ СМЕШАННЫЙ ФОРМАТ (текст + таблицы):")
    print("-" * 40)
    mixed_format = format_ocr_result(real_example, "mixed")
    print(mixed_format)
    
    # 3. Markdown формат
    print("\n3️⃣ MARKDOWN ФОРМАТ:")
    print("-" * 40)
    markdown_format = format_ocr_result(real_example, "markdown")
    print(markdown_format)
    
    # 4. Специальный формат для платежных документов
    print("\n4️⃣ ПЛАТЕЖНЫЙ ДОКУМЕНТ:")
    print("-" * 40)
    payment_format = format_ocr_result(real_example, "payment")
    print(payment_format)
    
    print("\n\n📊 СТАТИСТИКА:")
    print("-" * 40)
    print(f"Длина исходного текста: {len(real_example)} символов")
    print(f"Длина чистого текста: {len(clean_text)} символов")
    print(f"Содержит XML: {'Да' if '<table' in real_example else 'Нет'}")
    print(f"Количество таблиц: {real_example.count('<table>')}")


def test_copyable_functionality():
    """Тестирует функциональность для копирования"""
    
    print("\n\n📋 ТЕСТ ФУНКЦИЙ ДЛЯ КОПИРОВАНИЯ")
    print("=" * 60)
    
    # Имитируем работу модели OCR
    class MockOCRModel:
        def get_copyable_text(self, text):
            return format_ocr_result(text, "clean")
        
        def get_formatted_result(self, text, format_type="mixed"):
            return format_ocr_result(text, format_type)
    
    model = MockOCRModel()
    
    print("\n✅ Функция get_copyable_text():")
    copyable = model.get_copyable_text(real_example)
    print(copyable)
    
    print("\n✅ Функция get_formatted_result('mixed'):")
    formatted = model.get_formatted_result(real_example, "mixed")
    print(formatted)
    
    print("\n✅ Функция get_formatted_result('payment'):")
    payment = model.get_formatted_result(real_example, "payment")
    print(payment)


def demonstrate_usage():
    """Демонстрирует использование в коде"""
    
    print("\n\n💻 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ В КОДЕ")
    print("=" * 60)
    
    code_examples = [
        """
# Получить чистый текст для копирования
from models.dots_ocr_final import DotsOCRFinalModel

model = DotsOCRFinalModel(config)
model.load_model()

# Только текст, без XML-обработки
clean_text = model.get_copyable_text(image)

# Или явно указать
raw_text = model.extract_text(image)  # Без XML
""",
        """
# Получить структурированные данные
structured_data = model.get_structured_result(image)

# Или с контролем XML-обработки
result_with_xml = model.process_image(image, process_xml=True)
result_without_xml = model.process_image(image, process_xml=False)
""",
        """
# Различные форматы вывода
from utils.xml_formatter import format_ocr_result

# Чистый текст
clean = format_ocr_result(ocr_text, "clean")

# Markdown таблицы
markdown = format_ocr_result(ocr_text, "markdown") 

# Платежный документ
payment = format_ocr_result(ocr_text, "payment")
"""
    ]
    
    for i, example in enumerate(code_examples, 1):
        print(f"\n{i}️⃣ Пример {i}:")
        print(example.strip())


if __name__ == "__main__":
    try:
        test_formatting_options()
        test_copyable_functionality()
        demonstrate_usage()
        
        print("\n\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("- Используйте format_type='clean' для копирования текста")
        print("- Используйте format_type='mixed' для удобного просмотра")
        print("- Используйте format_type='payment' для платежных документов")
        print("- Используйте process_xml=False для отключения XML-обработки")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()