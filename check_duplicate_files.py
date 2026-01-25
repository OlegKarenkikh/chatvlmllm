#!/usr/bin/env python3
"""
Проверка дублирующих файлов приложения
"""

import os

# Проверяем наличие дублирующих файлов
duplicate_files = [
    'app_bbox_fixed.py',
    'app_backup.py', 
    'app_old.py',
    'app_original.py'
]

print("🔍 Проверка дублирующих файлов приложения:")

for file in duplicate_files:
    if os.path.exists(file):
        print(f"⚠️  НАЙДЕН ДУБЛЬ: {file}")
        
        # Читаем первые строки для проверки
        with open(file, 'r', encoding='utf-8') as f:
            first_lines = f.read(500)
        
        if 'st.chat_message' in first_lines:
            print(f"   📝 {file} содержит логику чата - МОЖЕТ КОНФЛИКТОВАТЬ!")
            
            # Предлагаем переименовать
            backup_name = f"{file}.backup"
            try:
                os.rename(file, backup_name)
                print(f"   ✅ Переименован в {backup_name}")
            except Exception as e:
                print(f"   ❌ Ошибка переименования: {e}")
        else:
            print(f"   ✅ {file} не содержит логику чата")
    else:
        print(f"✅ {file} - не найден")

print("\n🔍 Проверка основного файла app.py:")
if os.path.exists('app.py'):
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие нашего логирования
    if 'log_html_debug' in content:
        print("✅ app.py содержит наше логирование")
    else:
        print("❌ app.py НЕ содержит наше логирование")
    
    # Проверяем наличие HTML логики
    if 'unsafe_allow_html=True' in content:
        print("✅ app.py содержит HTML рендеринг")
    else:
        print("❌ app.py НЕ содержит HTML рендеринг")
    
    # Считаем количество секций чата
    chat_sections = content.count('with st.chat_message')
    print(f"📊 Найдено секций чата: {chat_sections}")
    
    if chat_sections > 2:
        print("⚠️  ВНИМАНИЕ: Слишком много секций чата - возможны дубли!")

else:
    print("❌ app.py не найден!")

print("\n✅ Проверка завершена")