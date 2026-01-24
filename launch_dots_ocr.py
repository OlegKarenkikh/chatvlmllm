#!/usr/bin/env python3
"""
ЗАПУСК DOTS.OCR ЧЕРЕЗ VLLM ДЛЯ RTX 5070 TI

Оптимизированный запуск с поддержкой Blackwell архитектуры
"""

import subprocess
import sys
import os

def launch_dots_ocr_vllm():
    """Запускаем dots.ocr через vLLM сервер."""
    print("🚀 ЗАПУСК DOTS.OCR ЧЕРЕЗ VLLM")
    print("=" * 50)
    
    # Команда запуска vLLM сервера
    vllm_cmd = [
        "vllm", "serve", "rednote-hilab/dots.ocr",
        "--trust-remote-code",
        "--async-scheduling",
        "--gpu-memory-utilization", "0.95",
        "--tensor-parallel-size", "1",
        "--max-model-len", "4096",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    
    print(f"Команда запуска: {' '.join(vllm_cmd)}")
    print("🌐 Сервер будет доступен на http://localhost:8000")
    print("📋 Для остановки нажмите Ctrl+C")
    print()
    
    try:
        # Запускаем vLLM сервер
        subprocess.run(vllm_cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️ Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска vLLM: {e}")

def launch_dots_ocr_docker():
    """Запускаем dots.ocr через Docker."""
    print("🐳 ЗАПУСК DOTS.OCR ЧЕРЕЗ DOCKER")
    print("=" * 50)
    
    # Команда запуска Docker контейнера
    docker_cmd = [
        "docker", "run", "--gpus", "all",
        "-e", "VLLM_GPU_MEMORY_UTILIZATION=0.9",
        "-e", "VLLM_TENSOR_PARALLEL_SIZE=1", 
        "-e", "VLLM_MAX_MODEL_LEN=4096",
        "-p", "8000:8000",
        "rednotehilab/dots.ocr:vllm-openai-v0.9.1"
    ]
    
    print(f"Команда запуска: {' '.join(docker_cmd)}")
    print("🌐 Сервер будет доступен на http://localhost:8000")
    print("📋 Для остановки нажмите Ctrl+C")
    print()
    
    try:
        # Запускаем Docker контейнер
        subprocess.run(docker_cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️ Docker контейнер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска Docker: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "docker":
        launch_dots_ocr_docker()
    else:
        launch_dots_ocr_vllm()
