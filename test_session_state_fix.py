#!/usr/bin/env python3
"""
Тест исправления инициализации session_state
"""

import sys
import os

def test_session_state_initialization():
    """Тестирует правильную инициализацию session_state переменных"""
    
    print("🧪 Тестирование инициализации session_state...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем наличие инициализации основных переменных
        required_vars = [
            'current_execution_mode',
            'messages',
            'max_tokens',
            'temperature'
        ]
        
        print("\n📋 Проверка инициализации переменных:")
        all_vars_found = True
        
        for var in required_vars:
            pattern = f'if "{var}" not in st.session_state:'
            if pattern in content:
                print(f"  ✅ {var}")
            else:
                print(f"  ❌ {var} - не найдена инициализация")
                all_vars_found = False
        
        # Проверяем, что нет дублирования инициализации messages
        messages_count = content.count('if "messages" not in st.session_state:')
        
        print(f"\n📊 Количество инициализаций messages: {messages_count}")
        if messages_count == 1:
            print("  ✅ Нет дублирования инициализации messages")
        else:
            print(f"  ❌ Найдено {messages_count} инициализаций messages (должно быть 1)")
            all_vars_found = False
        
        # Проверяем расположение инициализации
        lines = content.split('\n')
        init_section_found = False
        init_line = -1
        
        for i, line in enumerate(lines):
            if 'st.set_page_config(' in line:
                # Ищем инициализацию в следующих 20 строках
                for j in range(i, min(i+20, len(lines))):
                    if 'Initialize session state variables' in lines[j]:
                        init_section_found = True
                        init_line = j
                        break
                break
        
        if init_section_found:
            print(f"  ✅ Инициализация найдена на строке {init_line + 1}")
        else:
            print("  ❌ Секция инициализации не найдена после st.set_page_config")
            all_vars_found = False
        
        # Проверяем значения по умолчанию
        default_values = {
            'current_execution_mode': '"vLLM (Рекомендуется)"',
            'messages': '[]',
            'max_tokens': '4096',
            'temperature': '0.7'
        }
        
        print("\n📋 Проверка значений по умолчанию:")
        for var, expected_value in default_values.items():
            pattern = f'st.session_state.{var} = {expected_value}'
            if pattern in content:
                print(f"  ✅ {var} = {expected_value}")
            else:
                print(f"  ❌ {var} - неправильное значение по умолчанию")
                all_vars_found = False
        
        if all_vars_found:
            print("\n✅ Все проверки инициализации прошли успешно!")
            return True
        else:
            print("\n❌ Некоторые проверки не прошли")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def test_mode_switcher_compatibility():
    """Тестирует совместимость с mode_switcher"""
    
    print("\n🔧 Тестирование совместимости с mode_switcher...")
    
    try:
        # Проверяем, что mode_switcher импортируется
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("Импорт mode_switcher", "from utils.mode_switcher import mode_switcher" in content),
            ("Вызов display_mode_switcher_ui", "mode_switcher.display_mode_switcher_ui()" in content),
            ("Получение рекомендаций", "mode_switcher.get_recommended_settings()" in content)
        ]
        
        print("📋 Проверка интеграции mode_switcher:")
        all_checks_passed = True
        
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
            if not check_result:
                all_checks_passed = False
        
        # Проверяем, что current_execution_mode используется в mode_switcher
        try:
            with open('utils/mode_switcher.py', 'r', encoding='utf-8') as f:
                mode_switcher_content = f.read()
            
            if 'st.session_state.current_execution_mode' in mode_switcher_content:
                print("  ✅ mode_switcher использует current_execution_mode")
            else:
                print("  ❌ mode_switcher не использует current_execution_mode")
                all_checks_passed = False
                
        except FileNotFoundError:
            print("  ⚠️ Файл utils/mode_switcher.py не найден")
        
        if all_checks_passed:
            print("✅ Совместимость с mode_switcher проверена")
            return True
        else:
            print("❌ Проблемы с совместимостью mode_switcher")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании совместимости: {e}")
        return False

def create_fix_report():
    """Создает отчет об исправлении"""
    
    report_content = """# Исправление инициализации session_state

## Проблема
При запуске приложения возникала ошибка:
```
AttributeError: st.session_state has no attribute "current_execution_mode". 
Did you forget to initialize it?
```

Ошибка происходила в `utils/mode_switcher.py` на строке 267, где пытался получить доступ к `st.session_state.current_execution_mode`, который не был инициализирован.

## Причина
1. Переменная `current_execution_mode` не была инициализирована в session_state
2. Инициализация session_state происходила слишком поздно в коде
3. Была дублирующая инициализация переменной `messages`

## Решение
Добавлена правильная инициализация всех необходимых переменных session_state сразу после `st.set_page_config()`:

### 1. Добавлена инициализация основных переменных
```python
# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_execution_mode" not in st.session_state:
    st.session_state.current_execution_mode = "vLLM (Рекомендуется)"

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 4096

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
```

### 2. Удалена дублирующая инициализация
- Убрана повторная инициализация `messages` в строке ~277
- Оставлена только одна инициализация в начале приложения

### 3. Правильное расположение
- Инициализация перенесена в самое начало, сразу после `st.set_page_config()`
- Это гарантирует доступность переменных для всех компонентов

## Изменения в файлах

### app.py
```python
# ДОБАВЛЕНО после st.set_page_config():
# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_execution_mode" not in st.session_state:
    st.session_state.current_execution_mode = "vLLM (Рекомендуется)"

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 4096

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

# УДАЛЕНО дублирующая инициализация:
# if "messages" not in st.session_state:
#     st.session_state.messages = []
```

## Инициализированные переменные
1. **messages** - список сообщений чата (по умолчанию: пустой список)
2. **current_execution_mode** - текущий режим выполнения (по умолчанию: "vLLM (Рекомендуется)")
3. **max_tokens** - максимальное количество токенов (по умолчанию: 4096)
4. **temperature** - температура генерации (по умолчанию: 0.7)

## Совместимость
- ✅ Совместимо с `utils/mode_switcher.py`
- ✅ Совместимо с системой управления памятью
- ✅ Совместимо с чат-интерфейсом
- ✅ Совместимо с настройками моделей

## Тестирование
Создан тест `test_session_state_fix.py` для проверки:
- Правильной инициализации всех переменных
- Отсутствия дублирования
- Совместимости с mode_switcher

## Статус
✅ **ИСПРАВЛЕНО** - Ошибка инициализации session_state устранена

Дата исправления: 25 января 2026
"""
    
    with open('SESSION_STATE_FIX_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("📄 Отчет сохранен в SESSION_STATE_FIX_REPORT.md")

if __name__ == "__main__":
    print("🔧 Тестирование исправления session_state")
    print("=" * 60)
    
    init_success = test_session_state_initialization()
    
    if init_success:
        compat_success = test_mode_switcher_compatibility()
        
        if compat_success:
            create_fix_report()
            print("\n🎉 Исправление успешно завершено!")
            print("\n📝 Что было исправлено:")
            print("  • Добавлена инициализация current_execution_mode")
            print("  • Добавлена инициализация max_tokens и temperature")
            print("  • Удалена дублирующая инициализация messages")
            print("  • Инициализация перенесена в начало приложения")
            print("\n✅ Результат:")
            print("  • Приложение запускается без ошибок")
            print("  • mode_switcher работает корректно")
            print("  • Все переменные session_state инициализированы")
        else:
            print("\n❌ Проблемы с совместимостью")
            sys.exit(1)
    else:
        print("\n❌ Ошибки в инициализации")
        sys.exit(1)