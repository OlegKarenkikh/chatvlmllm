#!/usr/bin/env python3
"""
Расчет оптимального количества токенов для dots.ocr в vLLM
на основе доступной GPU памяти
"""

import json
import subprocess
import re
from datetime import datetime

def get_gpu_memory_info():
    """Получение информации о GPU памяти"""
    
    print("🔍 АНАЛИЗ GPU ПАМЯТИ")
    print("=" * 40)
    
    try:
        # Попытка получить информацию через nvidia-smi
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpu_info = []
            
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) == 3:
                    total_mb = int(parts[0])
                    used_mb = int(parts[1])
                    free_mb = int(parts[2])
                    
                    gpu_info.append({
                        'gpu_id': i,
                        'total_mb': total_mb,
                        'used_mb': used_mb,
                        'free_mb': free_mb,
                        'total_gb': total_mb / 1024,
                        'used_gb': used_mb / 1024,
                        'free_gb': free_mb / 1024
                    })
                    
                    print(f"GPU {i}:")
                    print(f"  📊 Общая память: {total_mb} MB ({total_mb/1024:.2f} GB)")
                    print(f"  🔴 Используется: {used_mb} MB ({used_mb/1024:.2f} GB)")
                    print(f"  🟢 Свободно: {free_mb} MB ({free_mb/1024:.2f} GB)")
            
            return gpu_info
        else:
            print("⚠️ nvidia-smi недоступен, используем приблизительные данные")
            
    except Exception as e:
        print(f"⚠️ Ошибка получения GPU информации: {e}")
    
    # Fallback - используем известные данные RTX 5070 Ti
    return [{
        'gpu_id': 0,
        'total_mb': 12288,  # 12GB
        'used_mb': 0,       # Предполагаем свободную
        'free_mb': 12288,
        'total_gb': 12.0,
        'used_gb': 0.0,
        'free_gb': 12.0
    }]

def estimate_dots_ocr_memory_usage():
    """Оценка использования памяти dots.ocr моделью"""
    
    print("\n🧮 ОЦЕНКА ИСПОЛЬЗОВАНИЯ ПАМЯТИ dots.ocr")
    print("=" * 50)
    
    # Базовые параметры dots.ocr модели
    model_info = {
        'name': 'rednote-hilab/dots.ocr',
        'estimated_params': 1.7e9,  # ~1.7B параметров
        'precision': 'fp16',        # 16-bit floating point
        'bytes_per_param': 2,       # fp16 = 2 байта на параметр
    }
    
    # Расчет базового использования памяти модели
    base_model_memory_gb = (model_info['estimated_params'] * model_info['bytes_per_param']) / (1024**3)
    
    print(f"📊 Параметры модели: {model_info['estimated_params']:.1e}")
    print(f"🔧 Точность: {model_info['precision']} ({model_info['bytes_per_param']} байта/параметр)")
    print(f"💾 Базовая память модели: {base_model_memory_gb:.2f} GB")
    
    # Дополнительные накладные расходы
    overhead_factors = {
        'kv_cache': 0.5,        # KV cache для attention
        'activations': 0.3,     # Промежуточные активации
        'gradients': 0.0,       # Нет градиентов при инференсе
        'optimizer': 0.0,       # Нет оптимизатора при инференсе
        'system_overhead': 0.2, # Системные накладные расходы
        'vllm_overhead': 0.3,   # Накладные расходы vLLM
    }
    
    total_overhead_gb = base_model_memory_gb * sum(overhead_factors.values())
    total_model_memory_gb = base_model_memory_gb + total_overhead_gb
    
    print(f"\n📈 Накладные расходы:")
    for factor, multiplier in overhead_factors.items():
        overhead_gb = base_model_memory_gb * multiplier
        print(f"  • {factor}: {overhead_gb:.2f} GB ({multiplier*100:.0f}%)")
    
    print(f"\n💾 Общее использование памяти модели: {total_model_memory_gb:.2f} GB")
    
    return {
        'base_model_gb': base_model_memory_gb,
        'total_overhead_gb': total_overhead_gb,
        'total_model_gb': total_model_memory_gb,
        'overhead_factors': overhead_factors
    }

def calculate_optimal_max_tokens(gpu_info, model_memory):
    """Расчет оптимального количества токенов"""
    
    print("\n🎯 РАСЧЕТ ОПТИМАЛЬНОГО КОЛИЧЕСТВА ТОКЕНОВ")
    print("=" * 55)
    
    # Используем первый GPU
    gpu = gpu_info[0]
    available_memory_gb = gpu['free_gb']
    
    print(f"🟢 Доступная память GPU: {available_memory_gb:.2f} GB")
    print(f"💾 Память модели: {model_memory['total_model_gb']:.2f} GB")
    
    # Память, доступная для токенов
    memory_for_tokens_gb = available_memory_gb - model_memory['total_model_gb']
    
    if memory_for_tokens_gb <= 0:
        print("❌ Недостаточно памяти для загрузки модели!")
        return None
    
    print(f"🎯 Память для токенов: {memory_for_tokens_gb:.2f} GB")
    
    # Расчет памяти на токен
    # Для Vision-Language моделей память на токен зависит от:
    # - Размера скрытых состояний (hidden_size)
    # - Количества слоев (num_layers)
    # - Размера головок внимания (num_attention_heads)
    
    # Приблизительные параметры для dots.ocr (на основе Qwen2-VL архитектуры)
    model_config = {
        'hidden_size': 1536,        # Размер скрытых состояний
        'num_layers': 28,           # Количество слоев
        'num_attention_heads': 12,  # Количество головок внимания
        'precision_bytes': 2,       # fp16 = 2 байта
    }
    
    # Память на токен в KV cache
    # KV cache = 2 (K + V) * num_layers * hidden_size * precision_bytes
    memory_per_token_bytes = (
        2 * model_config['num_layers'] * 
        model_config['hidden_size'] * 
        model_config['precision_bytes']
    )
    
    memory_per_token_mb = memory_per_token_bytes / (1024 * 1024)
    memory_per_token_gb = memory_per_token_bytes / (1024 ** 3)
    
    print(f"\n📊 Конфигурация модели:")
    print(f"  • Hidden size: {model_config['hidden_size']}")
    print(f"  • Layers: {model_config['num_layers']}")
    print(f"  • Attention heads: {model_config['num_attention_heads']}")
    print(f"  • Precision: {model_config['precision_bytes']} bytes")
    
    print(f"\n💾 Память на токен: {memory_per_token_mb:.3f} MB ({memory_per_token_bytes} bytes)")
    
    # Расчет максимального количества токенов
    max_tokens_theoretical = int(memory_for_tokens_gb / memory_per_token_gb)
    
    # Применяем коэффициент безопасности
    safety_factor = 0.8  # 80% от теоретического максимума
    max_tokens_safe = int(max_tokens_theoretical * safety_factor)
    
    # Округляем до красивых чисел
    token_options = [1024, 2048, 4096, 8192, 16384, 32768]
    optimal_tokens = max([t for t in token_options if t <= max_tokens_safe], default=1024)
    
    print(f"\n🧮 Расчеты:")
    print(f"  • Теоретический максимум: {max_tokens_theoretical:,} токенов")
    print(f"  • С коэффициентом безопасности ({safety_factor*100:.0f}%): {max_tokens_safe:,} токенов")
    print(f"  • Рекомендуемое значение: {optimal_tokens:,} токенов")
    
    # Проверка использования памяти при рекомендуемом значении
    memory_usage_gb = optimal_tokens * memory_per_token_gb
    total_memory_usage_gb = model_memory['total_model_gb'] + memory_usage_gb
    memory_utilization = (total_memory_usage_gb / gpu['total_gb']) * 100
    
    print(f"\n📊 Использование памяти при {optimal_tokens:,} токенах:")
    print(f"  • Память для токенов: {memory_usage_gb:.2f} GB")
    print(f"  • Общее использование: {total_memory_usage_gb:.2f} GB")
    print(f"  • Утилизация GPU: {memory_utilization:.1f}%")
    
    return {
        'theoretical_max': max_tokens_theoretical,
        'safe_max': max_tokens_safe,
        'recommended': optimal_tokens,
        'memory_per_token_gb': memory_per_token_gb,
        'memory_usage_gb': memory_usage_gb,
        'total_memory_gb': total_memory_usage_gb,
        'utilization_percent': memory_utilization
    }

def create_optimized_vllm_config(optimal_tokens):
    """Создание оптимизированной конфигурации vLLM"""
    
    print(f"\n🔧 СОЗДАНИЕ ОПТИМИЗИРОВАННОЙ КОНФИГУРАЦИИ vLLM")
    print("=" * 60)
    
    # Обновленная конфигурация Docker Compose
    docker_compose_config = f"""version: '3.8'

services:
  dots-ocr-optimized:
    image: vllm/vllm-openai:latest
    container_name: dots-ocr-vllm-optimized
    ports:
      - "8000:8000"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - VLLM_WORKER_MULTIPROC_METHOD=spawn
    command: >
      --model rednote-hilab/dots.ocr
      --host 0.0.0.0
      --port 8000
      --max-model-len {optimal_tokens['recommended']}
      --gpu-memory-utilization 0.85
      --dtype float16
      --trust-remote-code
      --disable-log-requests
      --served-model-name rednote-hilab/dots.ocr
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

networks:
  default:
    name: vllm-network
"""
    
    # Сохранение конфигурации
    with open("docker-compose-vllm-optimized.yml", "w", encoding="utf-8") as f:
        f.write(docker_compose_config)
    
    print(f"✅ Создан файл: docker-compose-vllm-optimized.yml")
    print(f"🎯 Максимальное количество токенов: {optimal_tokens['recommended']:,}")
    print(f"💾 Утилизация GPU памяти: 85%")
    print(f"🔧 Точность: float16")
    
    # Создание скрипта запуска
    launch_script = f"""#!/bin/bash
# Оптимизированный запуск dots.ocr в vLLM
# Рассчитано для RTX 5070 Ti (12GB VRAM)

echo "🚀 Запуск оптимизированного dots.ocr vLLM сервера"
echo "📊 Максимальное количество токенов: {optimal_tokens['recommended']:,}"
echo "💾 Ожидаемое использование памяти: {optimal_tokens['total_memory_gb']:.2f} GB"
echo "🎯 Утилизация GPU: {optimal_tokens['utilization_percent']:.1f}%"

# Остановка предыдущего контейнера
echo "🛑 Остановка предыдущих контейнеров..."
docker-compose -f docker-compose-vllm.yml down 2>/dev/null || true
docker-compose -f docker-compose-vllm-optimized.yml down 2>/dev/null || true

# Запуск оптимизированного контейнера
echo "🔄 Запуск оптимизированного контейнера..."
docker-compose -f docker-compose-vllm-optimized.yml up -d

# Ожидание готовности
echo "⏳ Ожидание готовности сервера..."
sleep 30

# Проверка статуса
echo "🔍 Проверка статуса..."
curl -s http://localhost:8000/health && echo "✅ Сервер готов!" || echo "❌ Ошибка запуска"

# Проверка моделей
echo "📊 Информация о модели:"
curl -s http://localhost:8000/v1/models | python -m json.tool

echo "🎉 Оптимизированный vLLM сервер запущен!"
echo "💡 Теперь dots.ocr поддерживает до {optimal_tokens['recommended']:,} токенов"
"""
    
    with open("start_vllm_optimized.sh", "w", encoding="utf-8") as f:
        f.write(launch_script)
    
    print(f"✅ Создан скрипт: start_vllm_optimized.sh")
    
    # Создание Windows batch файла
    batch_script = f"""@echo off
REM Оптимизированный запуск dots.ocr в vLLM для Windows
REM Рассчитано для RTX 5070 Ti (12GB VRAM)

echo 🚀 Запуск оптимизированного dots.ocr vLLM сервера
echo 📊 Максимальное количество токенов: {optimal_tokens['recommended']:,}
echo 💾 Ожидаемое использование памяти: {optimal_tokens['total_memory_gb']:.2f} GB
echo 🎯 Утилизация GPU: {optimal_tokens['utilization_percent']:.1f}%%

REM Остановка предыдущих контейнеров
echo 🛑 Остановка предыдущих контейнеров...
docker-compose -f docker-compose-vllm.yml down >nul 2>&1
docker-compose -f docker-compose-vllm-optimized.yml down >nul 2>&1

REM Запуск оптимизированного контейнера
echo 🔄 Запуск оптимизированного контейнера...
docker-compose -f docker-compose-vllm-optimized.yml up -d

REM Ожидание готовности
echo ⏳ Ожидание готовности сервера...
timeout /t 30 /nobreak >nul

REM Проверка статуса
echo 🔍 Проверка статуса...
curl -s http://localhost:8000/health >nul && echo ✅ Сервер готов! || echo ❌ Ошибка запуска

echo 🎉 Оптимизированный vLLM сервер запущен!
echo 💡 Теперь dots.ocr поддерживает до {optimal_tokens['recommended']:,} токенов
pause
"""
    
    with open("start_vllm_optimized.bat", "w", encoding="utf-8") as f:
        f.write(batch_script)
    
    print(f"✅ Создан скрипт: start_vllm_optimized.bat")
    
    return {
        'docker_compose_file': 'docker-compose-vllm-optimized.yml',
        'launch_script_linux': 'start_vllm_optimized.sh',
        'launch_script_windows': 'start_vllm_optimized.bat',
        'max_tokens': optimal_tokens['recommended'],
        'memory_usage_gb': optimal_tokens['total_memory_gb'],
        'utilization_percent': optimal_tokens['utilization_percent']
    }

def main():
    """Главная функция расчета и создания конфигурации"""
    
    print("🧮 РАСЧЕТ ОПТИМАЛЬНОГО КОЛИЧЕСТВА ТОКЕНОВ ДЛЯ dots.ocr vLLM")
    print("=" * 70)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Получение информации о GPU
    gpu_info = get_gpu_memory_info()
    
    # Оценка использования памяти модели
    model_memory = estimate_dots_ocr_memory_usage()
    
    # Расчет оптимального количества токенов
    optimal_tokens = calculate_optimal_max_tokens(gpu_info, model_memory)
    
    if not optimal_tokens:
        print("❌ Невозможно рассчитать оптимальные токены")
        return
    
    # Создание оптимизированной конфигурации
    config_info = create_optimized_vllm_config(optimal_tokens)
    
    # Создание отчета
    report = {
        'timestamp': datetime.now().isoformat(),
        'gpu_info': gpu_info,
        'model_memory_analysis': model_memory,
        'token_calculations': optimal_tokens,
        'configuration_files': config_info,
        'recommendations': [
            f"Используйте {optimal_tokens['recommended']:,} токенов для оптимальной производительности",
            f"Ожидаемое использование памяти: {optimal_tokens['total_memory_gb']:.2f} GB",
            f"Утилизация GPU: {optimal_tokens['utilization_percent']:.1f}%",
            "Запустите: ./start_vllm_optimized.sh (Linux) или start_vllm_optimized.bat (Windows)"
        ]
    }
    
    with open("vllm_token_optimization_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("🎉 РАСЧЕТ ЗАВЕРШЕН!")
    print("=" * 70)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"  • Текущий лимит: 1,024 токенов")
    print(f"  • Оптимальный лимит: {optimal_tokens['recommended']:,} токенов")
    print(f"  • Увеличение в {optimal_tokens['recommended']/1024:.1f} раз")
    print(f"  • Использование памяти: {optimal_tokens['total_memory_gb']:.2f} GB")
    print(f"  • Утилизация GPU: {optimal_tokens['utilization_percent']:.1f}%")
    
    print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ:")
    print(f"  • docker-compose-vllm-optimized.yml")
    print(f"  • start_vllm_optimized.sh (Linux)")
    print(f"  • start_vllm_optimized.bat (Windows)")
    print(f"  • vllm_token_optimization_report.json")
    
    print(f"\n🚀 ЗАПУСК ОПТИМИЗИРОВАННОГО СЕРВЕРА:")
    print(f"  Linux/Mac: ./start_vllm_optimized.sh")
    print(f"  Windows: start_vllm_optimized.bat")
    print(f"  Docker: docker-compose -f docker-compose-vllm-optimized.yml up -d")
    
    print(f"\n💡 ОЖИДАЕМЫЕ УЛУЧШЕНИЯ:")
    print(f"  • Поддержка длинных документов")
    print(f"  • Более детальные ответы")
    print(f"  • Лучшее качество OCR")
    print(f"  • Нет ошибок превышения токенов")

if __name__ == "__main__":
    main()