#!/usr/bin/env python3
"""
Мониторинг системы ChatVLMLLM в реальном времени
"""

import time
import requests
import os
import psutil
import torch
from datetime import datetime

def check_gpu_status():
    """Проверяет статус GPU"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        allocated_memory = torch.cuda.memory_allocated(0) / 1024**3
        cached_memory = torch.cuda.memory_reserved(0) / 1024**3
        
        return {
            "available": True,
            "name": gpu_name,
            "total_memory_gb": round(total_memory, 2),
            "allocated_memory_gb": round(allocated_memory, 2),
            "cached_memory_gb": round(cached_memory, 2),
            "free_memory_gb": round(total_memory - cached_memory, 2)
        }
    else:
        return {"available": False}

def check_streamlit_status():
    """Проверяет статус Streamlit"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        return {
            "status": "running" if response.status_code == 200 else "error",
            "status_code": response.status_code,
            "url": "http://localhost:8501"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "url": "http://localhost:8501"
        }

def check_api_status():
    """Проверяет статус FastAPI"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return {
            "status": "running" if response.status_code == 200 else "error",
            "status_code": response.status_code,
            "url": "http://localhost:8000",
            "data": response.json() if response.status_code == 200 else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "url": "http://localhost:8000"
        }

def check_system_resources():
    """Проверяет системные ресурсы"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('.')
    
    return {
        "cpu_percent": cpu_percent,
        "memory_total_gb": round(memory.total / 1024**3, 2),
        "memory_used_gb": round(memory.used / 1024**3, 2),
        "memory_percent": memory.percent,
        "disk_total_gb": round(disk.total / 1024**3, 2),
        "disk_used_gb": round(disk.used / 1024**3, 2),
        "disk_percent": round((disk.used / disk.total) * 100, 1)
    }

def check_log_files():
    """Проверяет наличие и размер лог файлов"""
    log_files = ["logs/chatvlmllm.log"]
    log_status = {}
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                last_lines = lines[-5:] if len(lines) >= 5 else lines
            
            log_status[log_file] = {
                "exists": True,
                "size_bytes": size,
                "size_kb": round(size / 1024, 2),
                "lines_count": len(lines),
                "last_lines": [line.strip() for line in last_lines]
            }
        else:
            log_status[log_file] = {
                "exists": False,
                "message": "Лог файл еще не создан"
            }
    
    return log_status

def print_status_report():
    """Выводит полный отчет о статусе системы"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n{'='*60}")
    print(f"🔍 МОНИТОРИНГ СИСТЕМЫ ChatVLMLLM - {timestamp}")
    print(f"{'='*60}")
    
    # GPU статус
    gpu_status = check_gpu_status()
    print(f"\n🎮 GPU СТАТУС:")
    if gpu_status["available"]:
        print(f"   ✅ {gpu_status['name']}")
        print(f"   📊 Память: {gpu_status['allocated_memory_gb']:.2f}GB / {gpu_status['total_memory_gb']:.2f}GB")
        print(f"   🆓 Свободно: {gpu_status['free_memory_gb']:.2f}GB")
    else:
        print(f"   ❌ GPU недоступна")
    
    # Streamlit статус
    streamlit_status = check_streamlit_status()
    print(f"\n🌐 STREAMLIT (Веб-интерфейс):")
    if streamlit_status["status"] == "running":
        print(f"   ✅ Работает: {streamlit_status['url']}")
    else:
        print(f"   ❌ Ошибка: {streamlit_status.get('error', 'Unknown')}")
    
    # API статус
    api_status = check_api_status()
    print(f"\n🚀 FastAPI (REST API):")
    if api_status["status"] == "running":
        print(f"   ✅ Работает: {api_status['url']}")
        if api_status.get("data"):
            data = api_status["data"]
            print(f"   📊 Модели загружены: {data.get('models_loaded', 0)}")
            print(f"   💾 VRAM использовано: {data.get('vram_used_gb', 0):.2f}GB")
    else:
        print(f"   ❌ Ошибка: {api_status.get('error', 'Unknown')}")
    
    # Системные ресурсы
    system_status = check_system_resources()
    print(f"\n💻 СИСТЕМНЫЕ РЕСУРСЫ:")
    print(f"   🔥 CPU: {system_status['cpu_percent']:.1f}%")
    print(f"   🧠 RAM: {system_status['memory_used_gb']:.1f}GB / {system_status['memory_total_gb']:.1f}GB ({system_status['memory_percent']:.1f}%)")
    print(f"   💾 Диск: {system_status['disk_used_gb']:.1f}GB / {system_status['disk_total_gb']:.1f}GB ({system_status['disk_percent']:.1f}%)")
    
    # Логи
    log_status = check_log_files()
    print(f"\n📋 ЛОГИ:")
    for log_file, status in log_status.items():
        if status["exists"]:
            print(f"   ✅ {log_file}: {status['size_kb']:.1f}KB ({status['lines_count']} строк)")
            if status["last_lines"]:
                print(f"   📝 Последние записи:")
                for line in status["last_lines"][-3:]:  # Показываем только последние 3 строки
                    if line:
                        print(f"      {line}")
        else:
            print(f"   ⚠️ {log_file}: {status['message']}")

def main():
    """Основная функция мониторинга"""
    print("🔍 Запуск мониторинга системы ChatVLMLLM...")
    print("Нажмите Ctrl+C для остановки")
    
    try:
        while True:
            print_status_report()
            print(f"\n⏰ Следующая проверка через 30 секунд...")
            time.sleep(30)
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Мониторинг остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка мониторинга: {e}")

if __name__ == "__main__":
    main()