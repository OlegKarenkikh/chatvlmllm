#!/usr/bin/env python3
"""
Скрипт для исправления вызовов process_image в app.py
Заменяет selected_model на активную модель из менеджера
"""

def fix_vllm_calls():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем проблемные вызовы
    old_pattern = 'result = adapter.process_image(image, prompt, selected_model, safe_max_tokens)'
    
    new_pattern = '''# ИСПРАВЛЕНИЕ: Используем активную модель из менеджера
                                    active_model_key = adapter.container_manager.get_active_model()
                                    if active_model_key:
                                        active_config = adapter.container_manager.models_config[active_model_key]
                                        vllm_model = active_config["model_path"]
                                        result = adapter.process_image(image, prompt, vllm_model, safe_max_tokens)
                                    else:
                                        st.error("❌ Нет активной модели")
                                        result = None'''
    
    # Подсчитываем количество замен
    count = content.count(old_pattern)
    print(f"Найдено {count} вхождений для замены")
    
    if count > 0:
        # Выполняем замену
        content = content.replace(old_pattern, new_pattern)
        
        # Сохраняем файл
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Выполнено {count} замен в app.py")
    else:
        print("❌ Не найдено вхождений для замены")

if __name__ == "__main__":
    fix_vllm_calls()