#!/usr/bin/env python3
"""
Анализатор производительности моделей на основе исторических результатов
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd

class PerformanceAnalyzer:
    """Класс для анализа производительности моделей на основе исторических данных"""
    
    def __init__(self, results_dir: str = "."):
        self.results_dir = results_dir
        self.historical_data = {}
        self.load_historical_results()
    
    def load_historical_results(self) -> None:
        """Загрузка всех исторических результатов тестирования"""
        
        # Паттерны файлов с результатами
        result_patterns = [
            "benchmark_results_*.json",
            "*_test_results*.json", 
            "final_working_models.json",
            "working_models_config.json",
            "dots_ocr_*_results.json",
            "official_prompts_*_results.json",
            "vllm_*_test_*.json"
        ]
        
        for pattern in result_patterns:
            files = glob.glob(os.path.join(self.results_dir, pattern))
            for file_path in files:
                try:
                    self._load_result_file(file_path)
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки {file_path}: {e}")
    
    def _load_result_file(self, file_path: str) -> None:
        """Загрузка отдельного файла с результатами"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        file_name = os.path.basename(file_path)
        
        # Определение типа результатов по имени файла
        if "benchmark_results" in file_name:
            self._process_benchmark_results(data, file_name)
        elif "working_models" in file_name:
            self._process_working_models(data, file_name)
        elif "test_results" in file_name:
            self._process_test_results(data, file_name)
        else:
            # Общая обработка
            self.historical_data[file_name] = data
    
    def _process_benchmark_results(self, data: Dict, source: str) -> None:
        """Обработка результатов бенчмарков"""
        
        model_name = data.get("model", "unknown")
        timestamp = data.get("timestamp", "")
        
        if model_name not in self.historical_data:
            self.historical_data[model_name] = {
                "benchmarks": [],
                "performance_metrics": {},
                "last_updated": timestamp
            }
        
        # Анализ результатов
        total_tests = 0
        successful_tests = 0
        total_time = 0
        avg_processing_time = 0
        
        for result in data.get("results", []):
            for test in result.get("tests", []):
                total_tests += 1
                if test.get("success", False):
                    successful_tests += 1
                    total_time += test.get("processing_time", 0)
        
        if successful_tests > 0:
            avg_processing_time = total_time / successful_tests
        
        benchmark_summary = {
            "timestamp": timestamp,
            "source": source,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "avg_processing_time": avg_processing_time,
            "total_documents": data.get("total_documents", 0)
        }
        
        self.historical_data[model_name]["benchmarks"].append(benchmark_summary)
        
        # Обновление метрик производительности
        self.historical_data[model_name]["performance_metrics"].update({
            "latest_success_rate": benchmark_summary["success_rate"],
            "latest_avg_time": avg_processing_time,
            "total_tests_run": total_tests
        })
    
    def _process_working_models(self, data: Dict, source: str) -> None:
        """Обработка данных о рабочих моделях"""
        
        for model_name, model_info in data.items():
            if isinstance(model_info, dict):
                if model_name not in self.historical_data:
                    self.historical_data[model_name] = {
                        "benchmarks": [],
                        "performance_metrics": {},
                        "status_info": {}
                    }
                
                # Извлечение информации о статусе
                status_info = {
                    "status": model_info.get("status", "unknown"),
                    "last_tested": model_info.get("last_tested", ""),
                    "source": source
                }
                
                # Извлечение результатов тестов
                test_results = model_info.get("test_results", {})
                if test_results:
                    status_info.update({
                        "text_test_success": test_results.get("text_test_success", False),
                        "vision_test_success": test_results.get("vision_test_success", False),
                        "inference_time": test_results.get("inference_time", 0),
                        "load_time": test_results.get("load_time", 0)
                    })
                
                self.historical_data[model_name]["status_info"] = status_info
    
    def _process_test_results(self, data: Dict, source: str) -> None:
        """Обработка общих результатов тестирования"""
        
        timestamp = data.get("timestamp", "")
        test_results = data.get("test_results", [])
        
        if isinstance(test_results, list):
            for result in test_results:
                model_name = result.get("model", "unknown")
                
                if model_name not in self.historical_data:
                    self.historical_data[model_name] = {
                        "benchmarks": [],
                        "performance_metrics": {},
                        "test_history": []
                    }
                
                test_summary = {
                    "timestamp": timestamp,
                    "source": source,
                    "success": result.get("success", False),
                    "processing_time": result.get("processing_time", 0),
                    "tokens_used": result.get("tokens_used", 0)
                }
                
                self.historical_data[model_name]["test_history"].append(test_summary)
    
    def get_model_comparison_data(self) -> pd.DataFrame:
        """Получение данных для сравнения моделей"""
        
        comparison_data = []
        
        for model_name, model_data in self.historical_data.items():
            # Пропускаем файлы, которые не являются моделями
            if not isinstance(model_data, dict) or "benchmarks" not in model_data:
                continue
            
            # Базовая информация о модели
            row = {
                "Модель": model_name,
                "Статус": "❓ Неизвестно",
                "Успешность (%)": 0,
                "Среднее время (с)": 0,
                "Всего тестов": 0,
                "Последнее тестирование": "Нет данных"
            }
            
            # Информация из бенчмарков
            benchmarks = model_data.get("benchmarks", [])
            if benchmarks:
                latest_benchmark = benchmarks[-1]  # Последний бенчмарк
                row.update({
                    "Успешность (%)": round(latest_benchmark.get("success_rate", 0), 1),
                    "Среднее время (с)": round(latest_benchmark.get("avg_processing_time", 0), 3),
                    "Всего тестов": latest_benchmark.get("total_tests", 0),
                    "Последнее тестирование": latest_benchmark.get("timestamp", "").split("T")[0]
                })
            
            # Информация о статусе
            status_info = model_data.get("status_info", {})
            if status_info:
                status = status_info.get("status", "unknown")
                if status == "tested_working":
                    row["Статус"] = "✅ Работает"
                elif status == "partially_working":
                    row["Статус"] = "⚠️ Частично"
                elif status == "not_working":
                    row["Статус"] = "❌ Не работает"
                
                if status_info.get("last_tested"):
                    row["Последнее тестирование"] = status_info["last_tested"].split(" ")[0]
            
            # Определение статуса по успешности
            if row["Успешность (%)"] >= 90:
                row["Статус"] = "✅ Отлично"
            elif row["Успешность (%)"] >= 70:
                row["Статус"] = "⚠️ Хорошо"
            elif row["Успешность (%)"] > 0:
                row["Статус"] = "⚠️ Частично"
            
            comparison_data.append(row)
        
        # Создание DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Сортировка по успешности
        if not df.empty:
            df = df.sort_values("Успешность (%)", ascending=False)
        
        return df
    
    def get_model_details(self, model_name: str) -> Dict[str, Any]:
        """Получение детальной информации о модели"""
        
        if model_name not in self.historical_data:
            return {"error": f"Модель {model_name} не найдена в исторических данных"}
        
        model_data = self.historical_data[model_name]
        
        details = {
            "model_name": model_name,
            "benchmarks_count": len(model_data.get("benchmarks", [])),
            "test_history_count": len(model_data.get("test_history", [])),
            "performance_metrics": model_data.get("performance_metrics", {}),
            "status_info": model_data.get("status_info", {}),
            "recent_benchmarks": model_data.get("benchmarks", [])[-3:],  # Последние 3
            "recent_tests": model_data.get("test_history", [])[-5:]  # Последние 5
        }
        
        return details
    
    def get_performance_trends(self, model_name: str) -> Dict[str, List]:
        """Получение трендов производительности модели"""
        
        if model_name not in self.historical_data:
            return {"error": f"Модель {model_name} не найдена"}
        
        model_data = self.historical_data[model_name]
        benchmarks = model_data.get("benchmarks", [])
        
        trends = {
            "timestamps": [],
            "success_rates": [],
            "processing_times": [],
            "test_counts": []
        }
        
        for benchmark in benchmarks:
            trends["timestamps"].append(benchmark.get("timestamp", ""))
            trends["success_rates"].append(benchmark.get("success_rate", 0))
            trends["processing_times"].append(benchmark.get("avg_processing_time", 0))
            trends["test_counts"].append(benchmark.get("total_tests", 0))
        
        return trends
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Получение общей статистики по всем моделям"""
        
        total_models = len([k for k, v in self.historical_data.items() 
                           if isinstance(v, dict) and "benchmarks" in v])
        
        working_models = 0
        total_tests = 0
        avg_success_rate = 0
        
        success_rates = []
        
        for model_name, model_data in self.historical_data.items():
            if not isinstance(model_data, dict) or "benchmarks" not in model_data:
                continue
            
            benchmarks = model_data.get("benchmarks", [])
            if benchmarks:
                latest = benchmarks[-1]
                success_rate = latest.get("success_rate", 0)
                success_rates.append(success_rate)
                total_tests += latest.get("total_tests", 0)
                
                if success_rate > 50:  # Считаем рабочей если успешность > 50%
                    working_models += 1
        
        if success_rates:
            avg_success_rate = sum(success_rates) / len(success_rates)
        
        return {
            "total_models": total_models,
            "working_models": working_models,
            "total_tests_run": total_tests,
            "average_success_rate": round(avg_success_rate, 1),
            "models_with_data": len(success_rates)
        }

def test_performance_analyzer():
    """Тестирование анализатора производительности"""
    
    print("🧪 ТЕСТИРОВАНИЕ АНАЛИЗАТОРА ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 50)
    
    analyzer = PerformanceAnalyzer()
    
    # Общая статистика
    stats = analyzer.get_summary_statistics()
    print(f"\n📊 Общая статистика:")
    print(f"   Всего моделей с данными: {stats['total_models']}")
    print(f"   Рабочих моделей: {stats['working_models']}")
    print(f"   Всего тестов проведено: {stats['total_tests_run']}")
    print(f"   Средняя успешность: {stats['average_success_rate']}%")
    
    # Сравнительная таблица
    comparison_df = analyzer.get_model_comparison_data()
    print(f"\n📋 Сравнительная таблица ({len(comparison_df)} моделей):")
    if not comparison_df.empty:
        print(comparison_df.to_string(index=False))
    else:
        print("   Нет данных для сравнения")
    
    # Детали по первой модели
    if not comparison_df.empty:
        first_model = comparison_df.iloc[0]["Модель"]
        details = analyzer.get_model_details(first_model)
        print(f"\n🔍 Детали модели '{first_model}':")
        print(f"   Бенчмарков: {details['benchmarks_count']}")
        print(f"   Тестов в истории: {details['test_history_count']}")
    
    print("\n✅ Тестирование завершено")

if __name__ == "__main__":
    test_performance_analyzer()