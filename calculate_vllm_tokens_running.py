#!/usr/bin/env python3
"""
Расчет оптимального количества токенов для уже запущенной dots.ocr в vLLM
"""

import json
import subprocess
import requests
from datetime import datetime

def get_current_vllm_status():
    """Получение текущего статуса vLLM"""
    
    print("🔍 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ vLLM")
    print("=" * 45)
    
    try:
        # Проверка здоровья сервера
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ vLLM сервер работает")
        else:
            print("❌ vLLM сервер недоступен")
            return None
        
        # Получение информации о моделях
        models_response = requests.get("http://localhost:8000/v1/models", timeout=5)
        if models_response.status_code == 200:
            models_data = models_response.json()
            
            for model in models_data.get("data", []):
                print(f"📊 Модель: {model['id']}")
                print(f"   📏 Текущий лимит: {model.get('max_model_len', 'неизвестно')} токенов")
                print(f"   📅 Создана: {model.get('created', 'неизвестно')}")
                
            return models_data
        else:
            print("❌ Не удается получить информацию о моделях")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка подключения к vLLM: {e}")
        return None

def get_gpu_memory_info():
    """Получение информации о GPU памяти"""
    
    print("\n🔍 АНАЛИЗ ИСПОЛЬЗОВАНИЯ GPU ПАМЯТИ")
    print("=" * 45)
    
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used,memory.free', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) == 3:
                    total_mb = int(parts[0])
                    used_mb = int(parts[1])
                    free_mb = int(parts[2])
                    
                    print(f"GPU {i}:")
                    print(f"  📊 Общая память: {total_mb} MB ({total_mb/1024:.2f} GB)")
                    print(f"  🔴 Используется: {used_mb} MB ({used_mb/1024:.2f} GB)")
                    print(f"  🟢 Свободно: {free_mb} MB ({free_mb/1024:.2f} GB)")
                    print(f"  📈 Утилизация: {(used_mb/total_mb)*100:.1f}%")
                    
                    return {
                        'total_mb': total_mb,
                        'used_mb': used_mb,
                        'free_mb': free_mb,
                        'total_gb': total_mb / 1024,
                        'used_gb': used_mb / 1024,
                        'free_gb': free_mb / 1024,
                        'utilization_percent': (used_mb/total_mb)*100
                    }
        
    except Exception as e:
        print(f"⚠️ Ошибка получения GPU информации: {e}")
    
    return None

def calculate_optimal_tokens_for_running_model(gpu_info, current_max_tokens=1024):
    """Расчет оптимального количества токенов для уже запущенной модели"""
    
    print(f"\n🧮 РАСЧЕТ ОПТИМАЛЬНОГО КОЛИЧЕСТВА ТОКЕНОВ")
    print("=" * 55)
    
    if not gpu_info:
        print("❌ Нет информации о GPU")
        return None
    
    # Текущее использование памяти включает модель + KV cache для текущих токенов
    current_model_memory_gb = gpu_info['used_gb']
    available_memory_gb = gpu_info['free_gb']
    total_memory_gb = gpu_info['total_gb']
    
    print(f"📊 Текущее состояние:")
    print(f"  • Используется: {current_model_memory_gb:.2f} GB")
    print(f"  • Доступно: {available_memory_gb:.2f} GB")
    print(f"  • Общая память: {total_memory_gb:.2f} GB")
    print(f"  • Текущий лимит токенов: {current_max_tokens:,}")
    
    # Оценка памяти на токен на основе архитектуры Vision-Language модели
    # Для dots.ocr (основана на Qwen2-VL архитектуре)
    model_config = {
        'hidden_size': 1536,        # Приблизительный размер скрытых состояний
        'num_layers': 28,           # Приблизительное количество слоев
        'precision_bytes': 2,       # fp16 = 2 байта
    }
    
    # KV cache память на токен = 2 (K + V) * num_layers * hidden_size * precision_bytes
    memory_per_token_bytes = (
        2 * model_config['num_layers'] * 
        model_config['hidden_size'] * 
        model_config['precision_bytes']
    )
    
    memory_per_token_mb = memory_per_token_bytes / (1024 * 1024)
    memory_per_token_gb = memory_per_token_bytes / (1024 ** 3)
    
    print(f"\n💾 Память на токен:")
    print(f"  • {memory_per_token_mb:.3f} MB на токен")
    print(f"  • {memory_per_token_bytes:,} байт на токен")
    
    # Расчет памяти, используемой текущими токенами
    current_tokens_memory_gb = current_max_tokens * memory_per_token_gb
    
    # Базовая память модели (без KV cache)
    base_model_memory_gb = current_model_memory_gb - current_tokens_memory_gb
    
    print(f"\n🔍 Анализ текущего использования:")
    print(f"  • Базовая модель: {base_model_memory_gb:.2f} GB")
    print(f"  • KV cache ({current_max_tokens:,} токенов): {current_tokens_memory_gb:.2f} GB")
    
    # Расчет максимального количества токенов
    # Используем всю доступную память + освобождаем память от текущего KV cache
    total_available_for_tokens_gb = available_memory_gb + current_tokens_memory_gb
    
    # Применяем коэффициент безопасности
    safety_factor = 0.9  # 90% от доступной памяти
    safe_memory_for_tokens_gb = total_available_for_tokens_gb * safety_factor
    
    max_tokens_theoretical = int(safe_memory_for_tokens_gb / memory_per_token_gb)
    
    # Округляем до стандартных значений
    token_options = [1024, 2048, 4096, 8192, 16384, 32768]
    optimal_tokens = max([t for t in token_options if t <= max_tokens_theoretical], default=1024)
    
    print(f"\n🧮 Расчеты:")
    print(f"  • Доступно для токенов: {total_available_for_tokens_gb:.2f} GB")
    print(f"  • С коэффициентом безопасности: {safe_memory_for_tokens_gb:.2f} GB")
    print(f"  • Теоретический максимум: {max_tokens_theoretical:,} токенов")
    print(f"  • Рекомендуемое значение: {optimal_tokens:,} токенов")
    
    # Проверка итогового использования памяти
    new_tokens_memory_gb = optimal_tokens * memory_per_token_gb
    total_memory_usage_gb = base_model_memory_gb + new_tokens_memory_gb
    final_utilization = (total_memory_usage_gb / total_memory_gb) * 100
    
    print(f"\n📊 Прогноз использования памяти при {optimal_tokens:,} токенах:")
    print(f"  • Базовая модель: {base_model_memory_gb:.2f} GB")
    print(f"  • KV cache: {new_tokens_memory_gb:.2f} GB")
    print(f"  • Общее использование: {total_memory_usage_gb:.2f} GB")
    print(f"  • Утилизация GPU: {final_utilization:.1f}%")
    print(f"  • Свободно останется: {total_memory_gb - total_memory_usage_gb:.2f} GB")
    
    # Сравнение с текущим состоянием
    improvement_factor = optimal_tokens / current_max_tokens
    
    print(f"\n📈 Улучшения:")
    print(f"  • Увеличение токенов в {improvement_factor:.1f} раз")
    print(f"  • С {current_max_tokens:,} до {optimal_tokens:,} токенов")
    print(f"  • Дополнительная память: {new_tokens_memory_gb - current_tokens_memory_gb:.2f} GB")
    
    return {
        'current_tokens': current_max_tokens,
        'recommended_tokens': optimal_tokens,
        'improvement_factor': improvement_factor,
        'memory_per_token_gb': memory_per_token_gb,
        'base_model_memory_gb': base_model_memory_gb,
        'new_tokens_memory_gb': new_tokens_memory_gb,
        'total_memory_usage_gb': total_memory_usage_gb,
        'final_utilization_percent': final_utilization,
        'theoretical_max': max_tokens_theoretical
    }

def create_restart_command(optimal_tokens):
    """Создание команды для перезапуска с оптимальными токенами"""
    
    print(f"\n🔧 КОМАНДЫ ДЛЯ ПЕРЕЗАПУСКА С ОПТИМАЛЬНЫМИ ТОКЕНАМИ")
    print("=" * 65)
    
    # Команда остановки
    stop_commands = [
        "# Остановка текущего контейнера",
        "docker-compose -f docker-compose-vllm.yml down",
        "",
        "# Или остановка по имени контейнера",
        "docker stop dots-ocr-vllm 2>/dev/null || true",
        "docker rm dots-ocr-vllm 2>/dev/null || true"
    ]
    
    # Команда запуска с оптимальными параметрами
    start_command = f"""# Запуск с оптимальными параметрами
docker run -d \\
  --name dots-ocr-vllm-optimized \\
  --gpus all \\
  -p 8000:8000 \\
  -v ~/.cache/huggingface:/root/.cache/huggingface \\
  -e CUDA_VISIBLE_DEVICES=0 \\
  vllm/vllm-openai:latest \\
  --model rednote-hilab/dots.ocr \\
  --host 0.0.0.0 \\
  --port 8000 \\
  --max-model-len {optimal_tokens['recommended_tokens']} \\
  --gpu-memory-utilization 0.90 \\
  --dtype float16 \\
  --trust-remote-code \\
  --disable-log-requests"""
    
    # Docker Compose версия
    docker_compose_optimized = f"""version: '3.8'

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
      --max-model-len {optimal_tokens['recommended_tokens']}
      --gpu-memory-utilization 0.90
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
"""
    
    # Сохранение файлов
    with open("docker-compose-vllm-optimized.yml", "w", encoding="utf-8") as f:
        f.write(docker_compose_optimized)
    
    # Скрипт перезапуска
    restart_script = f"""#!/bin/bash
# Перезапуск dots.ocr vLLM с оптимальными токенами

echo "🔄 ПЕРЕЗАПУСК dots.ocr vLLM С ОПТИМАЛЬНЫМИ ТОКЕНАМИ"
echo "📊 Новый лимит токенов: {optimal_tokens['recommended_tokens']:,}"
echo "📈 Увеличение в {optimal_tokens['improvement_factor']:.1f} раз"
echo "💾 Ожидаемое использование памяти: {optimal_tokens['total_memory_usage_gb']:.2f} GB"

# Остановка текущего контейнера
echo "🛑 Остановка текущего контейнера..."
docker-compose -f docker-compose-vllm.yml down 2>/dev/null || true
docker stop dots-ocr-vllm 2>/dev/null || true
docker rm dots-ocr-vllm 2>/dev/null || true

# Небольшая пауза для освобождения GPU памяти
echo "⏳ Ожидание освобождения GPU памяти..."
sleep 5

# Запуск оптимизированного контейнера
echo "🚀 Запуск оптимизированного контейнера..."
docker-compose -f docker-compose-vllm-optimized.yml up -d

# Ожидание готовности
echo "⏳ Ожидание готовности сервера (может занять 1-2 минуты)..."
sleep 60

# Проверка статуса
echo "🔍 Проверка статуса..."
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Сервер готов!"
    
    # Проверка новых лимитов
    echo "📊 Проверка лимитов токенов..."
    curl -s http://localhost:8000/v1/models | python -c "
import sys, json
data = json.load(sys.stdin)
for model in data.get('data', []):
    print(f'🎯 Модель: {{model[\"id\"]}}')
    print(f'📏 Лимит токенов: {{model.get(\"max_model_len\", \"неизвестно\"):,}}')
"
    
    echo "🎉 Оптимизация завершена успешно!"
    echo "💡 Теперь dots.ocr поддерживает до {optimal_tokens['recommended_tokens']:,} токенов"
else
    echo "❌ Ошибка запуска сервера"
    echo "💡 Проверьте логи: docker-compose -f docker-compose-vllm-optimized.yml logs"
fi
"""
    
    with open("restart_vllm_optimized.sh", "w", encoding="utf-8") as f:
        f.write(restart_script)
    
    # Windows batch версия
    batch_script = f"""@echo off
REM Перезапуск dots.ocr vLLM с оптимальными токенами

echo 🔄 ПЕРЕЗАПУСК dots.ocr vLLM С ОПТИМАЛЬНЫМИ ТОКЕНАМИ
echo 📊 Новый лимит токенов: {optimal_tokens['recommended_tokens']:,}
echo 📈 Увеличение в {optimal_tokens['improvement_factor']:.1f} раз
echo 💾 Ожидаемое использование памяти: {optimal_tokens['total_memory_usage_gb']:.2f} GB

REM Остановка текущего контейнера
echo 🛑 Остановка текущего контейнера...
docker-compose -f docker-compose-vllm.yml down >nul 2>&1
docker stop dots-ocr-vllm >nul 2>&1
docker rm dots-ocr-vllm >nul 2>&1

REM Пауза для освобождения GPU памяти
echo ⏳ Ожидание освобождения GPU памяти...
timeout /t 5 /nobreak >nul

REM Запуск оптимизированного контейнера
echo 🚀 Запуск оптимизированного контейнера...
docker-compose -f docker-compose-vllm-optimized.yml up -d

REM Ожидание готовности
echo ⏳ Ожидание готовности сервера (может занять 1-2 минуты)...
timeout /t 60 /nobreak >nul

REM Проверка статуса
echo 🔍 Проверка статуса...
curl -s http://localhost:8000/health >nul
if %errorlevel% == 0 (
    echo ✅ Сервер готов!
    echo 🎉 Оптимизация завершена успешно!
    echo 💡 Теперь dots.ocr поддерживает до {optimal_tokens['recommended_tokens']:,} токенов
) else (
    echo ❌ Ошибка запуска сервера
    echo 💡 Проверьте логи: docker-compose -f docker-compose-vllm-optimized.yml logs
)

pause
"""
    
    with open("restart_vllm_optimized.bat", "w", encoding="utf-8") as f:
        f.write(batch_script)
    
    print("✅ Созданы файлы конфигурации:")
    print("  • docker-compose-vllm-optimized.yml")
    print("  • restart_vllm_optimized.sh (Linux/Mac)")
    print("  • restart_vllm_optimized.bat (Windows)")
    
    print(f"\n🚀 КОМАНДЫ ДЛЯ ПЕРЕЗАПУСКА:")
    print("  Linux/Mac:")
    print("    chmod +x restart_vllm_optimized.sh")
    print("    ./restart_vllm_optimized.sh")
    print("  Windows:")
    print("    restart_vllm_optimized.bat")
    print("  Docker Compose:")
    print("    docker-compose -f docker-compose-vllm-optimized.yml up -d")
    
    return {
        'docker_compose_file': 'docker-compose-vllm-optimized.yml',
        'restart_script_linux': 'restart_vllm_optimized.sh',
        'restart_script_windows': 'restart_vllm_optimized.bat'
    }

def main():
    """Главная функция"""
    
    print("🧮 ОПТИМИЗАЦИЯ ТОКЕНОВ ДЛЯ ЗАПУЩЕННОЙ dots.ocr vLLM")
    print("=" * 65)
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    
    # Получение статуса vLLM
    vllm_status = get_current_vllm_status()
    if not vllm_status:
        print("❌ vLLM сервер недоступен")
        return
    
    # Получение текущего лимита токенов
    current_max_tokens = 1024  # По умолчанию
    for model in vllm_status.get("data", []):
        current_max_tokens = model.get("max_model_len", 1024)
        break
    
    # Получение информации о GPU
    gpu_info = get_gpu_memory_info()
    if not gpu_info:
        print("❌ Не удается получить информацию о GPU")
        return
    
    # Расчет оптимальных токенов
    optimal_tokens = calculate_optimal_tokens_for_running_model(gpu_info, current_max_tokens)
    if not optimal_tokens:
        print("❌ Не удается рассчитать оптимальные токены")
        return
    
    # Создание команд перезапуска
    restart_info = create_restart_command(optimal_tokens)
    
    # Создание отчета
    report = {
        'timestamp': datetime.now().isoformat(),
        'current_status': {
            'vllm_running': True,
            'current_max_tokens': current_max_tokens,
            'gpu_info': gpu_info
        },
        'optimization_results': optimal_tokens,
        'restart_files': restart_info,
        'summary': {
            'current_tokens': current_max_tokens,
            'recommended_tokens': optimal_tokens['recommended_tokens'],
            'improvement_factor': optimal_tokens['improvement_factor'],
            'memory_usage_gb': optimal_tokens['total_memory_usage_gb'],
            'gpu_utilization_percent': optimal_tokens['final_utilization_percent']
        }
    }
    
    with open("vllm_optimization_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 65)
    print("🎉 АНАЛИЗ И ОПТИМИЗАЦИЯ ЗАВЕРШЕНЫ!")
    print("=" * 65)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ:")
    print(f"  • Текущий лимит: {current_max_tokens:,} токенов")
    print(f"  • Рекомендуемый лимит: {optimal_tokens['recommended_tokens']:,} токенов")
    print(f"  • Увеличение в {optimal_tokens['improvement_factor']:.1f} раз")
    print(f"  • Использование памяти: {optimal_tokens['total_memory_usage_gb']:.2f} GB")
    print(f"  • Утилизация GPU: {optimal_tokens['final_utilization_percent']:.1f}%")
    
    if optimal_tokens['recommended_tokens'] > current_max_tokens:
        print(f"\n🚀 РЕКОМЕНДАЦИЯ: ПЕРЕЗАПУСТИТЬ С ОПТИМАЛЬНЫМИ ТОКЕНАМИ")
        print(f"  Команда: ./restart_vllm_optimized.sh")
        print(f"  Ожидаемые улучшения:")
        print(f"    • Поддержка длинных документов")
        print(f"    • Более детальные ответы")
        print(f"    • Лучшее качество OCR")
        print(f"    • Нет ошибок превышения токенов")
    else:
        print(f"\n✅ ТЕКУЩИЕ НАСТРОЙКИ УЖЕ ОПТИМАЛЬНЫ")
        print(f"  Дополнительная оптимизация не требуется")
    
    print(f"\n📄 Подробный отчет: vllm_optimization_report.json")

if __name__ == "__main__":
    main()