#!/usr/bin/env python3
"""
Генерация полной конфигурации vLLM для всех кешированных моделей
"""

import json
import os
from pathlib import Path

def generate_full_config():
    """Генерация полной конфигурации для всех моделей"""
    
    # Базовая конфигурация для всех найденных моделей
    models_config = {
        # OCR модели (высший приоритет)
        "rednote-hilab/dots.ocr": {
            "model_name": "rednote-hilab/dots.ocr",
            "container_name": "dots-ocr-fixed",
            "port": 8000,
            "size_gb": 5.67,
            "category": "ocr",
            "vllm_params": {
                "max_model_len": 1024,
                "gpu_memory_utilization": 0.85,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": [],
            "priority": 1,
            "status": "tested_working"
        },
        
        "deepseek-ai/deepseek-ocr": {
            "model_name": "deepseek-ai/deepseek-ocr",
            "container_name": "deepseek-ocr-vllm",
            "port": 8001,
            "size_gb": 0.01,
            "category": "ocr",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.6,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": ["Very small size - may be incomplete"],
            "priority": 2,
            "status": "needs_testing"
        },
        
        "stepfun-ai/GOT-OCR-2.0-hf": {
            "model_name": "stepfun-ai/GOT-OCR-2.0-hf",
            "container_name": "got-ocr-2-0-hf-vllm",
            "port": 8002,
            "size_gb": 1.06,
            "category": "ocr",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.7,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": ["May require additional dependencies"],
            "priority": 2,
            "status": "needs_testing"
        },
        
        "stepfun-ai/GOT-OCR2_0": {
            "model_name": "stepfun-ai/GOT-OCR2_0",
            "container_name": "stepfun-got-ocr2-0-vllm",
            "port": 8003,
            "size_gb": 1.34,
            "category": "ocr",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.7,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": ["Requires verovio package"],
            "priority": 2,
            "status": "known_incompatible"
        },
        
        "ucaslcl/GOT-OCR2_0": {
            "model_name": "ucaslcl/GOT-OCR2_0",
            "container_name": "ucaslcl-got-ocr2-0-vllm",
            "port": 8004,
            "size_gb": 2.67,
            "category": "ocr",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.7,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": ["Requires verovio package"],
            "priority": 2,
            "status": "known_incompatible"
        },
        
        # VLM модели (средний приоритет)
        "Qwen/Qwen3-VL-2B-Instruct": {
            "model_name": "Qwen/Qwen3-VL-2B-Instruct",
            "container_name": "qwen3-vl-2b-instruct-vllm",
            "port": 8010,
            "size_gb": 3.97,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.7,
                "trust_remote_code": True,
                "enforce_eager": False
            },
            "issues": [],
            "priority": 3,
            "status": "tested_working"
        },
        
        "Qwen/Qwen2-VL-2B-Instruct": {
            "model_name": "Qwen/Qwen2-VL-2B-Instruct",
            "container_name": "qwen2-vl-2b-instruct-vllm",
            "port": 8011,
            "size_gb": 4.13,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 4096,
                "gpu_memory_utilization": 0.7,
                "trust_remote_code": True,
                "enforce_eager": False
            },
            "issues": [],
            "priority": 3,
            "status": "needs_testing"
        },
        
        "Qwen/Qwen2.5-VL-7B-Instruct": {
            "model_name": "Qwen/Qwen2.5-VL-7B-Instruct",
            "container_name": "qwen2-5-vl-7b-instruct-vllm",
            "port": 8012,
            "size_gb": 0.66,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 4096,
                "gpu_memory_utilization": 0.7,
                "trust_remote_code": True,
                "enforce_eager": False
            },
            "issues": ["Small size - may be incomplete"],
            "priority": 3,
            "status": "needs_testing"
        },
        
        "Qwen/Qwen2-VL-7B-Instruct": {
            "model_name": "Qwen/Qwen2-VL-7B-Instruct",
            "container_name": "qwen2-vl-7b-instruct-vllm",
            "port": 8013,
            "size_gb": 7.61,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 4096,
                "gpu_memory_utilization": 0.6,
                "trust_remote_code": True,
                "enforce_eager": False
            },
            "issues": ["Large model - high memory usage"],
            "priority": 4,
            "status": "needs_testing"
        },
        
        "microsoft/Phi-3.5-vision-instruct": {
            "model_name": "microsoft/Phi-3.5-vision-instruct",
            "container_name": "phi-3-5-vision-instruct-vllm",
            "port": 8014,
            "size_gb": 7.73,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 4096,
                "gpu_memory_utilization": 0.6,
                "trust_remote_code": True,
                "enforce_eager": False
            },
            "issues": ["Large model - high memory usage"],
            "priority": 4,
            "status": "needs_testing"
        },
        
        "datalab-to/chandra": {
            "model_name": "datalab-to/chandra",
            "container_name": "datalab-chandra-vllm",
            "port": 8015,
            "size_gb": 0.42,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.6,
                "trust_remote_code": True,
                "enforce_eager": False
            },
            "issues": [],
            "priority": 3,
            "status": "needs_testing"
        },
        
        # Экспериментальные модели (низкий приоритет)
        "deepseek-ai/deepseek-vl-1.3b-chat": {
            "model_name": "deepseek-ai/deepseek-vl-1.3b-chat",
            "container_name": "deepseek-vl-1-3b-chat-vllm",
            "port": 8020,
            "size_gb": 0.0,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.5,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": ["Zero size - likely incomplete download"],
            "priority": 5,
            "status": "likely_broken"
        },
        
        "h2oai/h2ovl-mississippi-2b": {
            "model_name": "h2oai/h2ovl-mississippi-2b",
            "container_name": "h2ovl-mississippi-2b-vllm",
            "port": 8021,
            "size_gb": 4.01,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.6,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": ["Custom architecture - may not be supported"],
            "priority": 5,
            "status": "needs_testing"
        },
        
        "h2oai/h2ovl-mississippi-800m": {
            "model_name": "h2oai/h2ovl-mississippi-800m",
            "container_name": "h2ovl-mississippi-800m-vllm",
            "port": 8022,
            "size_gb": 1.54,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.5,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": ["Custom architecture - may not be supported"],
            "priority": 5,
            "status": "needs_testing"
        },
        
        "vikhyatk/moondream2": {
            "model_name": "vikhyatk/moondream2",
            "container_name": "moondream2-vllm",
            "port": 8023,
            "size_gb": 3.59,
            "category": "vlm",
            "vllm_params": {
                "max_model_len": 2048,
                "gpu_memory_utilization": 0.6,
                "trust_remote_code": True,
                "enforce_eager": True
            },
            "issues": ["Custom architecture - may not be supported"],
            "priority": 5,
            "status": "needs_testing"
        }
    }
    
    # Сохранение конфигурации
    with open('full_vllm_models_config.json', 'w', encoding='utf-8') as f:
        json.dump(models_config, f, ensure_ascii=False, indent=2)
    
    # Создание сводки
    summary = {
        "total_models": len(models_config),
        "by_category": {},
        "by_status": {},
        "by_priority": {},
        "total_size_gb": 0
    }
    
    for model_name, config in models_config.items():
        # По категориям
        category = config["category"]
        if category not in summary["by_category"]:
            summary["by_category"][category] = 0
        summary["by_category"][category] += 1
        
        # По статусу
        status = config["status"]
        if status not in summary["by_status"]:
            summary["by_status"][status] = 0
        summary["by_status"][status] += 1
        
        # По приоритету
        priority = config["priority"]
        if priority not in summary["by_priority"]:
            summary["by_priority"][priority] = 0
        summary["by_priority"][priority] += 1
        
        # Общий размер
        summary["total_size_gb"] += config["size_gb"]
    
    summary["total_size_gb"] = round(summary["total_size_gb"], 2)
    
    with open('full_vllm_models_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("📊 ПОЛНАЯ КОНФИГУРАЦИЯ vLLM СОЗДАНА")
    print("=" * 40)
    print(f"Всего моделей: {summary['total_models']}")
    print(f"Общий размер: {summary['total_size_gb']} ГБ")
    print()
    
    print("📂 По категориям:")
    for category, count in summary["by_category"].items():
        print(f"   {category}: {count} моделей")
    
    print()
    print("🔍 По статусу:")
    for status, count in summary["by_status"].items():
        print(f"   {status}: {count} моделей")
    
    print()
    print("⭐ По приоритету:")
    for priority in sorted(summary["by_priority"].keys()):
        count = summary["by_priority"][priority]
        print(f"   Приоритет {priority}: {count} моделей")
    
    print()
    print("💾 Файлы созданы:")
    print("   • full_vllm_models_config.json - полная конфигурация")
    print("   • full_vllm_models_summary.json - сводка")
    
    return models_config, summary

if __name__ == "__main__":
    generate_full_config()