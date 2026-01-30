#!/usr/bin/env python3
"""
Исправление проблем с токенами и моделями в vLLM интерфейсе
"""

import json
import requests
from datetime import datetime

def analyze_vllm_model_info():
    """Анализ информации о модели в vLLM"""
    
    print("🔍 АНАЛИЗ МОДЕЛИ vLLM")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/v1/models", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            
            print("📊 Информация о загруженных моделях:")
            for model in models_data.get("data", []):
                print(f"\n🤖 Модель: {model['id']}")
                print(f"   📏 Максимальная длина: {model.get('max_model_len', 'неизвестно')} токенов")
                print(f"   🏢 Владелец: {model.get('owned_by', 'неизвестно')}")
                print(f"   📅 Создана: {model.get('created', 'неизвестно')}")
                
                # Проблема: max_model_len слишком мал
                max_len = model.get('max_model_len', 0)
                if max_len < 2048:
                    print(f"   ⚠️ ПРОБЛЕМА: Максимальная длина {max_len} токенов слишком мала!")
                    print(f"   💡 Рекомендуется: минимум 2048 токенов")
            
            return models_data
        else:
            print(f"❌ Ошибка получения моделей: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка подключения к vLLM: {e}")
        return None

def create_vllm_fixes():
    """Создание исправлений для vLLM"""
    
    fixes = {
        "timestamp": datetime.now().isoformat(),
        "problems_identified": [
            {
                "problem": "dots.ocr max_model_len = 1024 токенов",
                "severity": "HIGH",
                "impact": "Ошибки при увеличении токенов в интерфейсе",
                "solution": "Ограничить токены в UI для vLLM режима"
            },
            {
                "problem": "Интерфейс показывает модели из config.yaml, а не из vLLM",
                "severity": "MEDIUM", 
                "impact": "Пользователь видит неправильные модели",
                "solution": "Динамически получать модели из vLLM API"
            }
        ],
        "fixes_to_apply": [
            {
                "file": "app.py",
                "change": "Добавить проверку max_model_len для vLLM режима",
                "code_location": "Настройки токенов в sidebar"
            },
            {
                "file": "vllm_streamlit_adapter.py", 
                "change": "Добавить получение max_model_len из API",
                "code_location": "get_available_models метод"
            },
            {
                "file": "app.py",
                "change": "Использовать vLLM модели вместо config моделей в vLLM режиме",
                "code_location": "Выбор модели в sidebar"
            }
        ]
    }
    
    return fixes

def main():
    """Главная функция анализа и исправления"""
    
    print("🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМ vLLM ТОКЕНОВ И МОДЕЛЕЙ")
    print("=" * 60)
    
    # Анализ текущего состояния
    models_data = analyze_vllm_model_info()
    
    if not models_data:
        print("\n❌ Не удается получить информацию о моделях vLLM")
        print("💡 Убедитесь, что vLLM сервер запущен:")
        print("   docker-compose -f docker-compose-vllm.yml up -d")
        return
    
    # Создание исправлений
    fixes = create_vllm_fixes()
    
    # Сохранение отчета
    with open("vllm_token_issues_analysis.json", "w", encoding="utf-8") as f:
        json.dump({
            "models_data": models_data,
            "fixes": fixes
        }, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("📊 ВЫВОДЫ И РЕКОМЕНДАЦИИ")
    print("=" * 60)
    
    # Анализ проблем
    for model in models_data.get("data", []):
        max_len = model.get('max_model_len', 0)
        model_id = model.get('id', 'unknown')
        
        if max_len < 2048:
            print(f"\n🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА:")
            print(f"   Модель: {model_id}")
            print(f"   Максимум токенов: {max_len}")
            print(f"   Проблема: При установке >1024 токенов в UI будут ошибки")
            print(f"   Решение: Ограничить токены в интерфейсе до {max_len}")
    
    print(f"\n💡 НЕОБХОДИМЫЕ ИСПРАВЛЕНИЯ:")
    for fix in fixes["fixes_to_apply"]:
        print(f"   📁 {fix['file']}: {fix['change']}")
    
    print(f"\n📄 Подробный анализ сохранен: vllm_token_issues_analysis.json")

if __name__ == "__main__":
    main()