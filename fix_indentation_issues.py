#!/usr/bin/env python3
"""
Скрипт для исправления проблем с отступами в app.py
Исправляет неправильные отступы после замен в коде
"""

import re

def fix_indentation_issues():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Паттерн для поиска неправильных отступов после комментария ИСПРАВЛЕНИЕ
    pattern = r'(\s+)# ИСПРАВЛЕНИЕ: Используем активную модель из менеджера\n(\s+)active_model_key = adapter\.container_manager\.get_active_model\(\)'
    
    def fix_indent(match):
        base_indent = match.group(1)  # Отступ комментария
        # Используем тот же отступ для кода
        return f'{base_indent}# ИСПРАВЛЕНИЕ: Используем активную модель из менеджера\n{base_indent}active_model_key = adapter.container_manager.get_active_model()'
    
    # Применяем исправление
    fixed_content = re.sub(pattern, fix_indent, content)
    
    # Дополнительно исправляем все строки с неправильными отступами после active_model_key
    lines = fixed_content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # Если это строка с active_model_key, проверяем следующие строки
        if 'active_model_key = adapter.container_manager.get_active_model()' in line:
            base_indent = len(line) - len(line.lstrip())
            
            # Исправляем следующие строки блока
            i += 1
            while i < len(lines) and (lines[i].strip() == '' or 
                                    'if active_model_key:' in lines[i] or
                                    'active_config = adapter.container_manager.models_config[active_model_key]' in lines[i] or
                                    'vllm_model = active_config["model_path"]' in lines[i] or
                                    'model_max_tokens = adapter.get_model_max_tokens(vllm_model)' in lines[i] or
                                    'else:' in lines[i] or
                                    'model_max_tokens = 1024' in lines[i]):
                
                if lines[i].strip() == '':
                    fixed_lines.append('')
                elif 'if active_model_key:' in lines[i]:
                    fixed_lines.append(' ' * base_indent + 'if active_model_key:')
                elif 'else:' in lines[i] and 'model_max_tokens' in lines[i+1] if i+1 < len(lines) else False:
                    fixed_lines.append(' ' * base_indent + 'else:')
                elif any(keyword in lines[i] for keyword in ['active_config =', 'vllm_model =', 'model_max_tokens =']):
                    # Эти строки должны быть с дополнительным отступом (внутри if/else)
                    fixed_lines.append(' ' * (base_indent + 4) + lines[i].strip())
                else:
                    fixed_lines.append(lines[i])
                i += 1
            i -= 1  # Откатываемся на одну строку назад
        
        i += 1
    
    # Сохраняем исправленный файл
    fixed_content = '\n'.join(fixed_lines)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Исправлены проблемы с отступами в app.py")

if __name__ == "__main__":
    fix_indentation_issues()