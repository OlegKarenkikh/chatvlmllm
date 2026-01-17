#!/usr/bin/env python3
"""Анализ всех кешированных моделей HuggingFace и проверка совместимости."""

import os
import json
from pathlib import Path
from transformers import AutoConfig
import yaml

def get_cache_dir():
    """Получить директорию кеша HuggingFace."""
    return Path.home() / ".cache" / "huggingface" / "hub"

def analyze_model(model_path):
    """Анализ одной модели."""
    try:
        # Попытка загрузить конфигурацию
        config_path = model_path / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            model_type = config.get('model_type', 'unknown')
            architectures = config.get('architectures', [])
            
            # Проверка, является ли это моделью машинного зрения
            is_vlm = any(arch for arch in architectures if any(keyword in arch.lower() 
                        for keyword in ['vision', 'vlm', 'multimodal', 'qwen', 'phi', 'idefics', 'vila']))
            
            # Проверка, является ли это OCR моделью
            is_ocr = any(keyword in str(model_path).lower() 
                        for keyword in ['ocr', 'got', 'dots'])
            
            return {
                'model_type': model_type,
                'architectures': architectures,
                'is_vlm': is_vlm,
                'is_ocr': is_ocr,
                'config': config
            }
    except Exception as e:
        return {'error': str(e)}
    
    return {'error': 'Конфигурация не найдена'}

def get_model_size(model_path):
    """Вычислить размер модели в ГБ."""
    total_size = 0
    for root, dirs, files in os.walk(model_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size / (1024**3)  # Конвертация в ГБ

def main():
    """Основная функция."""
    print("🔍 Анализ всех кешированных моделей HuggingFace...")
    print("=" * 60)
    
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        print("❌ Директория кеша HuggingFace не найдена!")
        return
    
    # Поиск всех директорий моделей
    model_dirs = [d for d in cache_dir.iterdir() if d.is_dir() and d.name.startswith('models--')]
    
    print(f"📁 Найдено {len(model_dirs)} кешированных моделей")
    print()
    
    vlm_models = []
    ocr_models = []
    other_models = []
    total_size = 0
    
    for model_dir in sorted(model_dirs):
        # Извлечение имени модели
        model_name = model_dir.name.replace('models--', '').replace('--', '/')
        
        # Поиск фактических файлов модели (в снимках)
        snapshots_dir = model_dir / "snapshots"
        if not snapshots_dir.exists():
            continue
            
        # Получение последнего снимка
        snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
        if not snapshot_dirs:
            continue
            
        latest_snapshot = max(snapshot_dirs, key=lambda x: x.stat().st_mtime)
        
        # Вычисление размера
        size_gb = get_model_size(model_dir)
        total_size += size_gb
        
        # Анализ модели
        analysis = analyze_model(latest_snapshot)
        
        model_info = {
            'name': model_name,
            'path': str(model_dir),
            'size_gb': round(size_gb, 2),
            'analysis': analysis
        }
        
        # Категоризация
        if analysis.get('is_vlm'):
            vlm_models.append(model_info)
        elif analysis.get('is_ocr'):
            ocr_models.append(model_info)
        else:
            other_models.append(model_info)
    
    # Вывод результатов
    print("🤖 МОДЕЛИ МАШИННОГО ЗРЕНИЯ (VLM)")
    print("-" * 40)
    for model in vlm_models:
        print(f"📊 {model['name']}")
        print(f"   Размер: {model['size_gb']} ГБ")
        if 'architectures' in model['analysis']:
            print(f"   Архитектура: {', '.join(model['analysis']['architectures'])}")
        print(f"   Тип: {model['analysis'].get('model_type', 'неизвестно')}")
        print()
    
    print("🔍 OCR МОДЕЛИ")
    print("-" * 40)
    for model in ocr_models:
        print(f"📊 {model['name']}")
        print(f"   Размер: {model['size_gb']} ГБ")
        if 'architectures' in model['analysis']:
            print(f"   Архитектура: {', '.join(model['analysis']['architectures'])}")
        print(f"   Тип: {model['analysis'].get('model_type', 'неизвестно')}")
        print()
    
    print("📦 ДРУГИЕ МОДЕЛИ")
    print("-" * 40)
    for model in other_models:
        print(f"📊 {model['name']}")
        print(f"   Размер: {model['size_gb']} ГБ")
        if 'architectures' in model['analysis']:
            print(f"   Архитектура: {', '.join(model['analysis']['architectures'])}")
        print(f"   Тип: {model['analysis'].get('model_type', 'неизвестно')}")
        print()
    
    # Сводка
    print("📈 СВОДКА")
    print("-" * 40)
    print(f"Всего моделей: {len(model_dirs)}")
    print(f"VLM модели: {len(vlm_models)}")
    print(f"OCR модели: {len(ocr_models)}")
    print(f"Другие модели: {len(other_models)}")
    print(f"Общий размер кеша: {round(total_size, 2)} ГБ")
    print()
    
    # Рекомендации
    print("💡 РЕКОМЕНДАЦИИ ПО ИНТЕГРАЦИИ")
    print("-" * 40)
    
    # Проверка, какие модели можно добавить в конфигурацию
    current_config_path = Path("config.yaml")
    if current_config_path.exists():
        with open(current_config_path, 'r', encoding='utf-8') as f:
            current_config = yaml.safe_load(f)
        
        current_models = set(current_config.get('models', {}).keys())
        
        print("🔧 Модели, которые можно добавить в config.yaml:")
        
        for model in vlm_models + ocr_models:
            model_key = model['name'].lower().replace('/', '_').replace('-', '_')
            if model_key not in current_models:
                print(f"   + {model['name']} ({model['size_gb']} ГБ)")
                print(f"     Предлагаемый ключ: {model_key}")
        
        print()
    
    print("✅ Анализ завершен!")

if __name__ == "__main__":
    main()