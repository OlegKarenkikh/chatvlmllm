"""
СИСТЕМА ВОССТАНОВЛЕНИЯ ПОСЛЕ CUDA ОШИБОК
"""

import torch
import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

class CUDARecoveryManager:
    """Менеджер восстановления после CUDA ошибок."""
    
    def __init__(self):
        self.cuda_error_count = 0
        self.max_cuda_errors = 3
        self.recovery_delay = 2.0
        
    def is_cuda_error(self, error: Exception) -> bool:
        """Проверяем, является ли ошибка CUDA ошибкой."""
        error_str = str(error).lower()
        cuda_error_indicators = [
            'cuda error',
            'device-side assert',
            'cudaerrorassert',
            'cuda runtime error',
            'out of memory',
            'cuda out of memory'
        ]
        
        return any(indicator in error_str for indicator in cuda_error_indicators)
    
    def recover_from_cuda_error(self) -> bool:
        """Восстанавливаемся после CUDA ошибки."""
        try:
            logger.warning(f"🔄 Попытка восстановления CUDA (попытка {self.cuda_error_count + 1}/{self.max_cuda_errors})")
            
            if torch.cuda.is_available():
                # Очищаем все CUDA кеши
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                
                # Ждем немного
                time.sleep(self.recovery_delay)
                
                # Тестируем CUDA
                test_tensor = torch.randn(10, 10, device='cuda')
                result = test_tensor @ test_tensor.T
                result.cpu()
                
                logger.info("✅ CUDA восстановлена успешно")
                self.cuda_error_count = 0
                return True
            else:
                logger.warning("⚠️ CUDA недоступна")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка восстановления CUDA: {e}")
            self.cuda_error_count += 1
            return False
    
    def safe_cuda_call(self, func: Callable, *args, **kwargs) -> Any:
        """Безопасный вызов функции с CUDA восстановлением."""
        for attempt in range(self.max_cuda_errors + 1):
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                if self.is_cuda_error(e) and attempt < self.max_cuda_errors:
                    logger.warning(f"⚠️ CUDA ошибка: {e}")
                    
                    if self.recover_from_cuda_error():
                        continue
                    else:
                        # Если восстановление не удалось, пробуем CPU режим
                        logger.warning("🔄 Переключаемся на CPU режим")
                        kwargs['device'] = 'cpu'
                        kwargs['force_cpu'] = True
                        continue
                else:
                    raise e
        
        raise RuntimeError(f"Не удалось выполнить операцию после {self.max_cuda_errors} попыток")

# Глобальный менеджер восстановления
cuda_recovery_manager = CUDARecoveryManager()
