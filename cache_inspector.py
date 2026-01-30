#!/usr/bin/env python3
"""
Детальная инспекция кеша HuggingFace для проверки готовности моделей к vLLM
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

class CacheInspector:
    def __init__(self):
        self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        self.required_files = {
            "essential": [
                "config.json",
                "tokenizer.json",
                "tokenizer_config.json"
            ],
            "model_files": [
                "model.safetensors",
                "pytorch_model.bin",
                "model.safetensors.index.json",
                "pytorch_model.bin.index.json"
            ],
            "optional": [
                "generation_config.json",
                "preprocessor_config.json",
                "processor_config.json",
                "special_tokens_map.json",
                "vocab.json",
                "merges.txt",
                "added_tokens.json"
            ]
        }
    
    def get_model_cache_path(self, model_name: str) -> Path:
        """Получение пути к кешу модели"""
        cache_name = f"models--{model_name.replace('/', '--')}"
        return self.cache_dir / cache_name
    
    def get_latest_snapshot(self, model_path: Path) -> Path:
        """Получение последнего снапшота модели"""
        snapshots_dir = model_path / "snapshots"
        if not snapshots_dir.exists():
            return None
        
        snapshot_dirs = [d for d in snapshots_dir.iterdir() if d.is_dir()]
        if not snapshot_dirs:
            return None
        
        # Возвращаем самый новый снапшот
        return max(snapshot_dirs, key=lambda x: x.stat().st_mtime)
    
    def check_model_files(self, model_name: str) -> Dict[str, Any]:
        """Детальная проверка файлов модели"""
        model_path = self.get_model_cache_path(model_name)
        
        result = {
            "model_name": model_name,
            "cache_exists": model_path.exists(),
            "cache_path": str(model_path),
            "total_size_mb": 0,
            "files_found": {},
            "missing_files": [],
            "issues": [],
            "readiness_score": 0,
            "vllm_ready": False
        }
        
        if not model_path.exists():
            result["issues"].append("Model cache directory not found")
            return result
        
        # Получение последнего снапшота
        latest_snapshot = self.get_latest_snapshot(model_path)
        if not latest_snapshot:
            result["issues"].append("No snapshots found")
            return result
        
        result["snapshot_path"] = str(latest_snapshot)
        
        # Подсчет общего размера
        total_size = 0
        for root, dirs, files in os.walk(model_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        
        result["total_size_mb"] = round(total_size / (1024**2), 2)
        
        # Проверка обязательных файлов
        essential_found = 0
        for file_name in self.required_files["essential"]:
            file_path = latest_snapshot / file_name
            if file_path.exists():
                result["files_found"][file_name] = {
                    "exists": True,
                    "size_kb": round(file_path.stat().st_size / 1024, 2)
                }
                essential_found += 1
            else:
                result["missing_files"].append(file_name)
                result["files_found"][file_name] = {"exists": False}
        
        # Проверка файлов модели (нужен хотя бы один)
        model_file_found = False
        for file_name in self.required_files["model_files"]:
            file_path = latest_snapshot / file_name
            if file_path.exists():
                result["files_found"][file_name] = {
                    "exists": True,
                    "size_mb": round(file_path.stat().st_size / (1024**2), 2)
                }
                model_file_found = True
            else:
                result["files_found"][file_name] = {"exists": False}
        
        if not model_file_found:
            result["issues"].append("No model weight files found")
        
        # Проверка дополнительных файлов
        for file_name in self.required_files["optional"]:
            file_path = latest_snapshot / file_name
            if file_path.exists():
                result["files_found"][file_name] = {
                    "exists": True,
                    "size_kb": round(file_path.stat().st_size / 1024, 2)
                }
        
        # Специальная проверка для vision моделей
        vision_files = [
            "preprocessor_config.json",
            "processor_config.json"
        ]
        
        vision_file_found = any(
            (latest_snapshot / f).exists() for f in vision_files
        )
        
        if vision_file_found:
            result["model_type"] = "vision"
        else:
            result["model_type"] = "text"
        
        # Расчет готовности
        readiness_score = 0
        
        # Обязательные файлы (60% от общей оценки)
        readiness_score += (essential_found / len(self.required_files["essential"])) * 60
        
        # Файлы модели (40% от общей оценки)
        if model_file_found:
            readiness_score += 40
        
        result["readiness_score"] = round(readiness_score, 1)
        result["vllm_ready"] = readiness_score >= 90 and result["total_size_mb"] > 0.1
        
        # Дополнительные проверки
        if result["total_size_mb"] < 0.1:
            result["issues"].append("Model size too small - likely incomplete download")
        
        if essential_found < len(self.required_files["essential"]):
            result["issues"].append(f"Missing {len(self.required_files['essential']) - essential_found} essential files")
        
        return result
    
    def inspect_all_models(self) -> Dict[str, Any]:
        """Инспекция всех моделей в кеше"""
        print("🔍 ДЕТАЛЬНАЯ ИНСПЕКЦИЯ КЕША HUGGINGFACE")
        print("=" * 50)
        
        if not self.cache_dir.exists():
            print("❌ Директория кеша HuggingFace не найдена!")
            return {}
        
        # Получение всех моделей в кеше
        model_dirs = [d for d in self.cache_dir.iterdir() 
                     if d.is_dir() and d.name.startswith('models--')]
        
        print(f"📁 Найдено {len(model_dirs)} моделей в кеше")
        print(f"📂 Путь к кешу: {self.cache_dir}")
        
        results = {}
        total_size_gb = 0
        ready_models = 0
        incomplete_models = 0
        
        for model_dir in model_dirs:
            model_name = model_dir.name.replace('models--', '').replace('--', '/')
            print(f"\n🔍 Проверка: {model_name}")
            
            result = self.check_model_files(model_name)
            results[model_name] = result
            
            total_size_gb += result["total_size_mb"] / 1024
            
            if result["vllm_ready"]:
                ready_models += 1
                print(f"   ✅ Готова к vLLM ({result['readiness_score']}%, {result['total_size_mb']} МБ)")
            else:
                incomplete_models += 1
                print(f"   ❌ Не готова ({result['readiness_score']}%, {result['total_size_mb']} МБ)")
                if result["issues"]:
                    for issue in result["issues"]:
                        print(f"      ⚠️ {issue}")
        
        # Сводка
        print(f"\n📊 СВОДКА ИНСПЕКЦИИ")
        print("=" * 25)
        print(f"Всего моделей: {len(results)}")
        print(f"Готовы к vLLM: {ready_models}")
        print(f"Не готовы: {incomplete_models}")
        print(f"Общий размер кеша: {total_size_gb:.2f} ГБ")
        
        return results
    
    def create_detailed_report(self, results: Dict[str, Any]):
        """Создание детального отчета"""
        report = {
            "inspection_timestamp": __import__('time').strftime("%Y-%m-%d %H:%M:%S"),
            "cache_path": str(self.cache_dir),
            "summary": {
                "total_models": len(results),
                "ready_models": sum(1 for r in results.values() if r["vllm_ready"]),
                "incomplete_models": sum(1 for r in results.values() if not r["vllm_ready"]),
                "total_size_gb": round(sum(r["total_size_mb"] for r in results.values()) / 1024, 2)
            },
            "models": results
        }
        
        # Сохранение JSON отчета
        with open('cache_inspection_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Создание текстового отчета
        with open('cache_inspection_report.txt', 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ О ИНСПЕКЦИИ КЕША HUGGINGFACE\n")
            f.write("=" * 40 + "\n")
            f.write(f"Дата: {report['inspection_timestamp']}\n")
            f.write(f"Путь к кешу: {report['cache_path']}\n\n")
            
            f.write("СВОДКА:\n")
            f.write("-" * 10 + "\n")
            f.write(f"Всего моделей: {report['summary']['total_models']}\n")
            f.write(f"Готовы к vLLM: {report['summary']['ready_models']}\n")
            f.write(f"Не готовы: {report['summary']['incomplete_models']}\n")
            f.write(f"Общий размер: {report['summary']['total_size_gb']} ГБ\n\n")
            
            # Готовые модели
            ready_models = [name for name, result in results.items() if result["vllm_ready"]]
            if ready_models:
                f.write("✅ ГОТОВЫЕ К vLLM МОДЕЛИ:\n")
                f.write("-" * 30 + "\n")
                for model_name in ready_models:
                    result = results[model_name]
                    f.write(f"• {model_name}\n")
                    f.write(f"  Размер: {result['total_size_mb']} МБ\n")
                    f.write(f"  Готовность: {result['readiness_score']}%\n")
                    f.write(f"  Тип: {result.get('model_type', 'unknown')}\n\n")
            
            # Проблемные модели
            incomplete_models = [name for name, result in results.items() if not result["vllm_ready"]]
            if incomplete_models:
                f.write("❌ ПРОБЛЕМНЫЕ МОДЕЛИ:\n")
                f.write("-" * 25 + "\n")
                for model_name in incomplete_models:
                    result = results[model_name]
                    f.write(f"• {model_name}\n")
                    f.write(f"  Размер: {result['total_size_mb']} МБ\n")
                    f.write(f"  Готовность: {result['readiness_score']}%\n")
                    if result["issues"]:
                        f.write("  Проблемы:\n")
                        for issue in result["issues"]:
                            f.write(f"    - {issue}\n")
                    f.write("\n")
        
        print(f"\n💾 Отчеты сохранены:")
        print(f"   📄 cache_inspection_report.json")
        print(f"   📄 cache_inspection_report.txt")
    
    def get_vllm_ready_models(self, results: Dict[str, Any]) -> List[str]:
        """Получение списка моделей, готовых к vLLM"""
        return [name for name, result in results.items() if result["vllm_ready"]]
    
    def get_incomplete_models(self, results: Dict[str, Any]) -> List[str]:
        """Получение списка неполных моделей"""
        return [name for name, result in results.items() if not result["vllm_ready"]]
    
    def suggest_cleanup(self, results: Dict[str, Any]):
        """Предложения по очистке кеша"""
        print(f"\n🧹 ПРЕДЛОЖЕНИЯ ПО ОЧИСТКЕ")
        print("=" * 30)
        
        # Модели с нулевым размером
        zero_size_models = [name for name, result in results.items() 
                           if result["total_size_mb"] < 0.1]
        
        if zero_size_models:
            print(f"🗑️ Модели с нулевым размером (можно удалить):")
            for model_name in zero_size_models:
                print(f"   • {model_name}")
        
        # Модели с низкой готовностью
        low_readiness_models = [name for name, result in results.items() 
                               if result["readiness_score"] < 50 and result["total_size_mb"] > 0.1]
        
        if low_readiness_models:
            print(f"\n⚠️ Модели с низкой готовностью (требуют довагрузки):")
            for model_name in low_readiness_models:
                result = results[model_name]
                print(f"   • {model_name} ({result['readiness_score']}%)")
        
        # Подсчет места для освобождения
        cleanup_size = sum(results[name]["total_size_mb"] for name in zero_size_models)
        if cleanup_size > 0:
            print(f"\n💾 Можно освободить: {cleanup_size:.2f} МБ")

def main():
    """Основная функция"""
    inspector = CacheInspector()
    
    # Запуск инспекции
    results = inspector.inspect_all_models()
    
    if results:
        # Создание отчетов
        inspector.create_detailed_report(results)
        
        # Предложения по очистке
        inspector.suggest_cleanup(results)
        
        # Список готовых моделей
        ready_models = inspector.get_vllm_ready_models(results)
        if ready_models:
            print(f"\n🎯 МОДЕЛИ ГОТОВЫЕ К ТЕСТИРОВАНИЮ vLLM:")
            for model_name in ready_models:
                result = results[model_name]
                print(f"   ✅ {model_name} ({result['total_size_mb']} МБ)")
        
        print(f"\n✅ Инспекция завершена!")
    else:
        print(f"\n❌ Инспекция не выполнена")

if __name__ == "__main__":
    main()