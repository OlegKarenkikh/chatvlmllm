#!/usr/bin/env python3
'''
CUDA Recovery Script - Экстренное восстановление GPU состояния
'''

import torch
import gc
import os
import time

def emergency_cuda_recovery():
    '''Экстренное восстановление CUDA'''
    
    print("🚨 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ CUDA...")
    
    try:
        # 1. Принудительная очистка всех CUDA кешей
        if torch.cuda.is_available():
            print("🔄 Очистка CUDA кешей...")
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            torch.cuda.ipc_collect()
            
            # Сброс всех CUDA контекстов
            for i in range(torch.cuda.device_count()):
                with torch.cuda.device(i):
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
        
        # 2. Принудительная сборка мусора
        print("🗑️ Принудительная сборка мусора...")
        for _ in range(3):
            gc.collect()
            time.sleep(0.5)
        
        # 3. Установка переменных окружения для отладки
        print("🔧 Установка отладочных переменных...")
        os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
        os.environ['TORCH_USE_CUDA_DSA'] = '1'
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
        
        # 4. Проверка состояния GPU
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            print(f"✅ Обнаружено GPU устройств: {device_count}")
            
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                memory_allocated = torch.cuda.memory_allocated(i) / 1024**3
                memory_reserved = torch.cuda.memory_reserved(i) / 1024**3
                memory_total = props.total_memory / 1024**3
                
                print(f"GPU {i}: {props.name}")
                print(f"  Память: {memory_allocated:.2f}GB выделено, {memory_reserved:.2f}GB зарезервировано, {memory_total:.2f}GB всего")
                
                # Попытка создать тестовый тензор
                try:
                    test_tensor = torch.randn(100, 100, device=f'cuda:{i}')
                    del test_tensor
                    torch.cuda.empty_cache()
                    print(f"  ✅ GPU {i} работает корректно")
                except Exception as e:
                    print(f"  ❌ GPU {i} ошибка: {e}")
        
        print("✅ Восстановление CUDA завершено")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка восстановления CUDA: {e}")
        return False

if __name__ == "__main__":
    emergency_cuda_recovery()
