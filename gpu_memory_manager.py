#!/usr/bin/env python3
"""
Управление GPU памятью для решения проблем с vLLM
"""

import subprocess
import time
import psutil
import os

def get_gpu_info():
    """Получение информации о GPU"""
    try:
        result = subprocess.run([
            "nvidia-smi", 
            "--query-gpu=index,name,memory.total,memory.free,memory.used,utilization.gpu",
            "--format=csv,noheader,nounits"
        ], capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\n')
        gpus = []
        
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 6:
                gpus.append({
                    'index': int(parts[0]),
                    'name': parts[1],
                    'total_mb': int(parts[2]),
                    'free_mb': int(parts[3]),
                    'used_mb': int(parts[4]),
                    'utilization': int(parts[5])
                })
        
        return gpus
    except Exception as e:
        print(f"❌ Ошибка получения информации о GPU: {e}")
        return []

def get_gpu_processes():
    """Получение процессов, использующих GPU"""
    try:
        result = subprocess.run([
            "nvidia-smi", 
            "--query-compute-apps=pid,process_name,used_memory",
            "--format=csv,noheader,nounits"
        ], capture_output=True, text=True, check=True)
        
        lines = result.stdout.strip().split('\n')
        processes = []
        
        for line in lines:
            if line.strip():
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    processes.append({
                        'pid': int(parts[0]),
                        'name': parts[1],
                        'memory_mb': int(parts[2])
                    })
        
        return processes
    except Exception as e:
        print(f"❌ Ошибка получения GPU процессов: {e}")
        return []

def kill_gpu_processes(exclude_pids=None):
    """Завершение процессов, использующих GPU"""
    if exclude_pids is None:
        exclude_pids = []
    
    processes = get_gpu_processes()
    killed = []
    
    for proc in processes:
        pid = proc['pid']
        if pid in exclude_pids:
            continue
            
        try:
            # Проверяем, что процесс существует
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                process_name = process.name()
                
                print(f"🔪 Завершение процесса: {process_name} (PID: {pid}, GPU память: {proc['memory_mb']} MB)")
                
                # Сначала пробуем мягкое завершение
                process.terminate()
                time.sleep(2)
                
                # Если не завершился, принудительно
                if process.is_running():
                    process.kill()
                    time.sleep(1)
                
                killed.append(proc)
                
        except Exception as e:
            print(f"⚠️ Не удалось завершить процесс {pid}: {e}")
    
    return killed

def cleanup_docker():
    """Очистка Docker контейнеров и ресурсов"""
    print("🐳 Очистка Docker ресурсов...")
    
    commands = [
        "docker stop $(docker ps -aq) 2>/dev/null || true",
        "docker system prune -f",
        "docker volume prune -f",
        "docker network prune -f"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=False, capture_output=True)
        except:
            pass

def clear_cuda_cache():
    """Очистка CUDA кеша"""
    print("🗑️ Очистка CUDA кеша...")
    
    cleanup_script = """
import torch
import gc

if torch.cuda.is_available():
    # Очистка кеша всех GPU
    for i in range(torch.cuda.device_count()):
        with torch.cuda.device(i):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
    
    # Принудительная сборка мусора
    gc.collect()
    
    print(f"CUDA кеш очищен для {torch.cuda.device_count()} GPU")
else:
    print("CUDA недоступна")
"""
    
    try:
        result = subprocess.run(
            ["python", "-c", cleanup_script], 
            capture_output=True, text=True, check=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"⚠️ Ошибка очистки CUDA кеша: {e}")

def restart_wsl():
    """Перезапуск WSL (только для Windows)"""
    if os.name == 'nt':  # Windows
        print("🔄 Перезапуск WSL...")
        try:
            subprocess.run(["wsl", "--shutdown"], check=True)
            time.sleep(5)
            print("✅ WSL перезапущен")
        except Exception as e:
            print(f"⚠️ Ошибка перезапуска WSL: {e}")
    else:
        print("ℹ️ Не Windows система, пропуск перезапуска WSL")

def display_gpu_status():
    """Отображение статуса GPU"""
    print("\n📊 СТАТУС GPU")
    print("=" * 50)
    
    gpus = get_gpu_info()
    if not gpus:
        print("❌ Не удалось получить информацию о GPU")
        return
    
    for gpu in gpus:
        print(f"🎮 GPU {gpu['index']}: {gpu['name']}")
        print(f"   💾 Память: {gpu['used_mb']}/{gpu['total_mb']} MB ({gpu['free_mb']} MB свободно)")
        print(f"   📈 Утилизация: {gpu['utilization']}%")
        
        # Расчет процента использования памяти
        memory_percent = (gpu['used_mb'] / gpu['total_mb']) * 100
        print(f"   📊 Память: {memory_percent:.1f}% использовано")
        
        # Рекомендации
        if gpu['free_mb'] < 6000:  # Меньше 6GB свободно
            print(f"   ⚠️ Мало свободной памяти для dots.ocr")
        else:
            print(f"   ✅ Достаточно памяти для dots.ocr")
    
    # Процессы на GPU
    processes = get_gpu_processes()
    if processes:
        print(f"\n🔄 ПРОЦЕССЫ НА GPU ({len(processes)}):")
        for proc in processes:
            print(f"   • PID {proc['pid']}: {proc['name']} ({proc['memory_mb']} MB)")
    else:
        print("\n✅ Нет активных процессов на GPU")

def recommend_vllm_settings():
    """Рекомендации настроек vLLM"""
    gpus = get_gpu_info()
    if not gpus:
        return
    
    gpu = gpus[0]  # Первая GPU
    free_gb = gpu['free_mb'] / 1024
    total_gb = gpu['total_mb'] / 1024
    
    print(f"\n💡 РЕКОМЕНДАЦИИ ДЛЯ VLLM")
    print("=" * 30)
    
    if free_gb < 6:
        print("❌ Недостаточно памяти для dots.ocr через vLLM")
        print("🔧 Рекомендуемые действия:")
        print("   1. Очистить GPU память (этот скрипт)")
        print("   2. Использовать transformers с 8-bit квантизацией")
        print("   3. Перейти на более легкую модель")
        
    elif free_gb < 8:
        gpu_util = min(0.4, free_gb / total_gb * 0.8)
        print(f"⚠️ Ограниченная память, консервативные настройки:")
        print(f"   --gpu-memory-utilization {gpu_util:.2f}")
        print(f"   --max-model-len 1024")
        print(f"   --max-num-seqs 1")
        print(f"   --dtype bfloat16")
        
    else:
        gpu_util = min(0.7, free_gb / total_gb * 0.9)
        print(f"✅ Достаточно памяти, оптимальные настройки:")
        print(f"   --gpu-memory-utilization {gpu_util:.2f}")
        print(f"   --max-model-len 2048")
        print(f"   --max-num-seqs 4")

def main():
    """Основная функция"""
    print("🛠️ УПРАВЛЕНИЕ GPU ПАМЯТЬЮ")
    print("=" * 30)
    
    while True:
        print("\nВыберите действие:")
        print("1. 📊 Показать статус GPU")
        print("2. 🧹 Полная очистка GPU памяти")
        print("3. 🔪 Завершить GPU процессы")
        print("4. 🐳 Очистить Docker")
        print("5. 🗑️ Очистить CUDA кеш")
        print("6. 🔄 Перезапустить WSL")
        print("7. 💡 Рекомендации для vLLM")
        print("0. ❌ Выход")
        
        choice = input("\nВведите номер: ").strip()
        
        if choice == "1":
            display_gpu_status()
            
        elif choice == "2":
            print("\n🧹 ПОЛНАЯ ОЧИСТКА GPU ПАМЯТИ")
            print("=" * 35)
            
            # Завершение GPU процессов
            killed = kill_gpu_processes()
            if killed:
                print(f"✅ Завершено {len(killed)} процессов")
            
            # Очистка Docker
            cleanup_docker()
            
            # Очистка CUDA кеша
            clear_cuda_cache()
            
            time.sleep(3)
            display_gpu_status()
            
        elif choice == "3":
            processes = get_gpu_processes()
            if processes:
                print(f"\n🔪 Завершение {len(processes)} GPU процессов...")
                killed = kill_gpu_processes()
                print(f"✅ Завершено {len(killed)} процессов")
            else:
                print("✅ Нет активных GPU процессов")
                
        elif choice == "4":
            cleanup_docker()
            print("✅ Docker ресурсы очищены")
            
        elif choice == "5":
            clear_cuda_cache()
            
        elif choice == "6":
            restart_wsl()
            
        elif choice == "7":
            recommend_vllm_settings()
            
        elif choice == "0":
            break
            
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()