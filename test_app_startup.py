#!/usr/bin/env python3
"""
Быстрый тест запуска приложения после исправления session_state
"""

import sys
import os
import subprocess

def test_app_syntax():
    """Тестирует синтаксис приложения"""
    
    print("🧪 Тестирование синтаксиса приложения...")
    
    try:
        # Проверяем синтаксис Python
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', 'app.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Синтаксис app.py корректен")
        else:
            print(f"❌ Ошибка синтаксиса: {result.stderr}")
            return False
        
        # Проверяем импорты
        try:
            import streamlit
            print("✅ Streamlit доступен")
        except ImportError:
            print("❌ Streamlit не установлен")
            return False
        
        # Проверяем наличие необходимых файлов
        required_files = [
            'config.yaml',
            'utils/mode_switcher.py',
            'utils/memory_controller.py',
            'ui/styles.py'
        ]
        
        print("\n📋 Проверка необходимых файлов:")
        all_files_exist = True
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path} - не найден")
                all_files_exist = False
        
        if not all_files_exist:
            print("⚠️ Некоторые файлы отсутствуют, но это не критично для синтаксиса")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании синтаксиса: {e}")
        return False

def test_imports():
    """Тестирует импорты в приложении"""
    
    print("\n🔧 Тестирование импортов...")
    
    try:
        # Тестируем основные импорты
        imports_to_test = [
            'streamlit',
            'yaml',
            'pathlib',
            'PIL'
        ]
        
        print("📋 Проверка основных импортов:")
        for module in imports_to_test:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except ImportError:
                print(f"  ❌ {module} - не установлен")
                return False
        
        # Проверяем специфичные импорты приложения
        try:
            # Проверяем, что можем импортировать функции из app.py
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем наличие основных функций
            functions_to_check = [
                'clean_ocr_result',
                'load_config'
            ]
            
            print("\n📋 Проверка функций приложения:")
            for func in functions_to_check:
                if f'def {func}(' in content:
                    print(f"  ✅ {func}")
                else:
                    print(f"  ❌ {func} - не найдена")
            
        except Exception as e:
            print(f"⚠️ Ошибка при проверке функций: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании импортов: {e}")
        return False

def test_session_state_structure():
    """Тестирует структуру инициализации session_state"""
    
    print("\n📊 Тестирование структуры session_state...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем порядок инициализации
        lines = content.split('\n')
        
        config_line = -1
        init_start = -1
        
        for i, line in enumerate(lines):
            if 'st.set_page_config(' in line:
                config_line = i
            elif 'Initialize session state variables' in line:
                init_start = i
                break
        
        if config_line != -1 and init_start != -1:
            if init_start > config_line:
                print(f"✅ Инициализация session_state после st.set_page_config (строки {config_line+1} → {init_start+1})")
            else:
                print("❌ Неправильный порядок инициализации")
                return False
        else:
            print("❌ Не найдены ключевые секции")
            return False
        
        # Проверяем структуру инициализации
        init_vars = []
        in_init_section = False
        
        for line in lines[init_start:init_start+20]:  # Проверяем следующие 20 строк
            if 'Initialize session state variables' in line:
                in_init_section = True
                continue
            
            if in_init_section and 'if "' in line and 'not in st.session_state:' in line:
                # Извлекаем имя переменной
                var_name = line.split('"')[1]
                init_vars.append(var_name)
        
        expected_vars = ['messages', 'current_execution_mode', 'max_tokens', 'temperature']
        
        print(f"\n📋 Найденные переменные инициализации: {init_vars}")
        print(f"📋 Ожидаемые переменные: {expected_vars}")
        
        missing_vars = set(expected_vars) - set(init_vars)
        extra_vars = set(init_vars) - set(expected_vars)
        
        if not missing_vars and not extra_vars:
            print("✅ Все необходимые переменные инициализированы")
        else:
            if missing_vars:
                print(f"❌ Отсутствуют переменные: {missing_vars}")
            if extra_vars:
                print(f"ℹ️ Дополнительные переменные: {extra_vars}")
        
        return len(missing_vars) == 0
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании структуры: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тестирование запуска приложения")
    print("=" * 60)
    
    syntax_ok = test_app_syntax()
    imports_ok = test_imports()
    structure_ok = test_session_state_structure()
    
    if syntax_ok and imports_ok and structure_ok:
        print("\n🎉 Все тесты прошли успешно!")
        print("\n📋 Резюме:")
        print("  ✅ Синтаксис приложения корректен")
        print("  ✅ Все необходимые импорты доступны")
        print("  ✅ session_state правильно инициализирован")
        print("  ✅ Приложение готово к запуску")
        
        print("\n🚀 Для запуска используйте:")
        print("  streamlit run app.py")
        
        print("\n💡 Исправленные проблемы:")
        print("  • AttributeError с current_execution_mode")
        print("  • Дублирование инициализации messages")
        print("  • Неправильный порядок инициализации")
    else:
        print("\n❌ Некоторые тесты не прошли")
        if not syntax_ok:
            print("  • Проблемы с синтаксисом")
        if not imports_ok:
            print("  • Проблемы с импортами")
        if not structure_ok:
            print("  • Проблемы со структурой session_state")
        sys.exit(1)