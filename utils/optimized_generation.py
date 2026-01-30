"""
ОПТИМИЗИРОВАННЫЕ ПАРАМЕТРЫ ГЕНЕРАЦИИ ДЛЯ УСТРАНЕНИЯ CUDA ПРОБЛЕМ
"""

import torch

# Оптимизированные параметры для каждой модели
OPTIMIZED_GENERATION_PARAMS = {
    "qwen_vl_2b": {
        "max_new_tokens": 512,
        "do_sample": False,
        "temperature": 0.1,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
        "pad_token_id": None,  # Будет установлен автоматически
        "use_cache": True,
        "output_attentions": False,
        "output_hidden_states": False
    },
    
    "qwen3_vl_2b": {
        "max_new_tokens": 1024,
        "do_sample": False,
        "temperature": 0.1,
        "top_p": 0.9,
        "repetition_penalty": 1.05,
        "pad_token_id": 151645,  # Специфично для Qwen3-VL
        "use_cache": True,
        "output_attentions": False,
        "output_hidden_states": False
    },
    
    "dots_ocr": {
        "max_new_tokens": 2048,
        "do_sample": False,
        "temperature": 0.1,
        "top_p": 0.95,
        "repetition_penalty": 1.0,
        "pad_token_id": None,
        "use_cache": True,
        "output_attentions": False,
        "output_hidden_states": False
    }
}

def get_optimized_params(model_name: str) -> dict:
    """Получаем оптимизированные параметры для модели."""
    return OPTIMIZED_GENERATION_PARAMS.get(model_name, OPTIMIZED_GENERATION_PARAMS["qwen3_vl_2b"])

def apply_cuda_optimizations():
    """Применяем CUDA оптимизации."""
    if torch.cuda.is_available():
        # Оптимизации для стабильности
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        
        # Очистка кеша
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        
        return True
    return False
