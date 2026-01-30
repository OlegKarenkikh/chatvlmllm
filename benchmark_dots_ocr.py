#!/usr/bin/env python3
"""
Комплексный бенчмарк производительности и точности dots.ocr через vLLM
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
from dots_ocr_client import DotsOCRClient
import statistics

class OCRBenchmark:
    def __init__(self):
        self.client = DotsOCRClient()
        self.results = []
        self.test_documents_dir = Path("test_documents")
        
    def run_benchmark(self):
        """Запуск полного бенчмарка"""
        print("🚀 ЗАПУСК КОМПЛЕКСНОГО БЕНЧМАРКА DOTS.OCR")
        print("=" * 60)
        print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Проверка доступности сервера
        if not self.client.health_check():
            print("❌ Сервер недоступен!")
            return
        
        print("✅ Сервер доступен, начинаем тестирование...")
        print()
        
        # Получение списка тестовых документов
        test_files = list(self.test_documents_dir.glob("*.png"))
        if not test_files:
            print("❌ Тестовые документы не найдены!")
            print("💡 Запустите: python create_test_documents.py")
            return
        
        print(f"📁 Найдено {len(test_files)} тестовых документов")
        print()
        
        # Тестирование каждого документа
        for i, test_file in enumerate(sorted(test_files), 1):
            print(f"🔄 Тест {i}/{len(test_files)}: {test_file.name}")
            self.test_document(test_file)
            print()
        
        # Анализ результатов
        self.analyze_results()
        
        # Сохранение отчета
        self.save_report()
        
        print("✅ Бенчмарк завершен!")
    
    def test_document(self, file_path: Path):
        """Тестирование одного документа"""
        
        # Разные типы промптов для тестирования
        prompts = [
            "Extract all text from this image",
            "Transcribe all text content from this document",
            "Read and extract all visible text from this image",
            "Convert this image to text format"
        ]
        
        document_results = {
            "file": file_path.name,
            "file_size_kb": file_path.stat().st_size / 1024,
            "tests": []
        }
        
        for prompt_idx, prompt in enumerate(prompts):
            print(f"   Промпт {prompt_idx + 1}/4: {prompt[:30]}...")
            
            # Измерение времени
            start_time = time.time()
            
            # Выполнение OCR (учитываем ограничение модели в 1024 токена)
            result = self.client.process_image(str(file_path), prompt, max_tokens=800)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Анализ результата
            test_result = {
                "prompt": prompt,
                "processing_time": round(processing_time, 2),
                "success": result["success"],
                "text_length": len(result.get("text", "")) if result["success"] else 0,
                "word_count": len(result.get("text", "").split()) if result["success"] else 0,
                "error": result.get("error") if not result["success"] else None
            }
            
            if result["success"]:
                # Дополнительный анализ текста
                text = result["text"]
                test_result.update({
                    "has_numbers": any(char.isdigit() for char in text),
                    "has_cyrillic": any('\u0400' <= char <= '\u04FF' for char in text),
                    "has_latin": any(char.isascii() and char.isalpha() for char in text),
                    "line_count": len([line for line in text.split('\n') if line.strip()]),
                    "avg_word_length": round(sum(len(word) for word in text.split()) / len(text.split()), 2) if text.split() else 0
                })
                
                print(f"      ✅ Успех: {test_result['word_count']} слов за {processing_time:.1f}с")
            else:
                print(f"      ❌ Ошибка: {result.get('error', 'Unknown error')}")
            
            document_results["tests"].append(test_result)
            
            # Небольшая пауза между запросами
            time.sleep(1)
        
        self.results.append(document_results)
    
    def analyze_results(self):
        """Анализ результатов бенчмарка"""
        print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("=" * 30)
        
        # Общая статистика
        total_tests = sum(len(doc["tests"]) for doc in self.results)
        successful_tests = sum(sum(1 for test in doc["tests"] if test["success"]) for doc in self.results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Всего тестов: {total_tests}")
        print(f"Успешных: {successful_tests}")
        print(f"Процент успеха: {success_rate:.1f}%")
        print()
        
        # Статистика по времени
        processing_times = []
        word_counts = []
        
        for doc in self.results:
            for test in doc["tests"]:
                if test["success"]:
                    processing_times.append(test["processing_time"])
                    word_counts.append(test["word_count"])
        
        if processing_times:
            print("⏱️ ПРОИЗВОДИТЕЛЬНОСТЬ:")
            print(f"   Среднее время: {statistics.mean(processing_times):.1f}с")
            print(f"   Медианное время: {statistics.median(processing_times):.1f}с")
            print(f"   Минимальное время: {min(processing_times):.1f}с")
            print(f"   Максимальное время: {max(processing_times):.1f}с")
            print()
            
            print("📝 ОБЪЕМ ТЕКСТА:")
            print(f"   Среднее кол-во слов: {statistics.mean(word_counts):.0f}")
            print(f"   Медианное кол-во слов: {statistics.median(word_counts):.0f}")
            print(f"   Минимум слов: {min(word_counts)}")
            print(f"   Максимум слов: {max(word_counts)}")
            print()
            
            # Скорость обработки (слов в секунду)
            speeds = [wc / pt for wc, pt in zip(word_counts, processing_times) if pt > 0]
            if speeds:
                print("🚀 СКОРОСТЬ ОБРАБОТКИ:")
                print(f"   Средняя скорость: {statistics.mean(speeds):.1f} слов/сек")
                print(f"   Максимальная скорость: {max(speeds):.1f} слов/сек")
                print()
        
        # Анализ по типам документов
        print("📋 АНАЛИЗ ПО ТИПАМ ДОКУМЕНТОВ:")
        for doc in self.results:
            successful_doc_tests = [test for test in doc["tests"] if test["success"]]
            if successful_doc_tests:
                avg_time = statistics.mean([test["processing_time"] for test in successful_doc_tests])
                avg_words = statistics.mean([test["word_count"] for test in successful_doc_tests])
                success_rate_doc = len(successful_doc_tests) / len(doc["tests"]) * 100
                
                print(f"   {doc['file'][:20]:20} | {success_rate_doc:5.1f}% | {avg_time:5.1f}с | {avg_words:5.0f} слов")
        
        print()
        
        # Анализ качества распознавания
        print("🎯 КАЧЕСТВО РАСПОЗНАВАНИЯ:")
        cyrillic_docs = sum(1 for doc in self.results for test in doc["tests"] 
                           if test["success"] and test.get("has_cyrillic", False))
        latin_docs = sum(1 for doc in self.results for test in doc["tests"] 
                        if test["success"] and test.get("has_latin", False))
        number_docs = sum(1 for doc in self.results for test in doc["tests"] 
                         if test["success"] and test.get("has_numbers", False))
        
        print(f"   Документы с кириллицей: {cyrillic_docs}")
        print(f"   Документы с латиницей: {latin_docs}")
        print(f"   Документы с числами: {number_docs}")
    
    def save_report(self):
        """Сохранение подробного отчета"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Подробные результаты в JSON
        detailed_report = {
            "timestamp": datetime.now().isoformat(),
            "server_url": self.client.base_url,
            "model": self.client.model_name,
            "total_documents": len(self.results),
            "results": self.results
        }
        
        json_file = f"benchmark_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)
        
        # Краткий отчет в текстовом формате
        summary_file = f"benchmark_summary_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("ОТЧЕТ О БЕНЧМАРКЕ DOTS.OCR\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Модель: {self.client.model_name}\n")
            f.write(f"Сервер: {self.client.base_url}\n\n")
            
            # Статистика
            total_tests = sum(len(doc["tests"]) for doc in self.results)
            successful_tests = sum(sum(1 for test in doc["tests"] if test["success"]) for doc in self.results)
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            
            f.write(f"Всего тестов: {total_tests}\n")
            f.write(f"Успешных: {successful_tests}\n")
            f.write(f"Процент успеха: {success_rate:.1f}%\n\n")
            
            # Производительность
            processing_times = [test["processing_time"] for doc in self.results 
                              for test in doc["tests"] if test["success"]]
            if processing_times:
                f.write(f"Среднее время обработки: {statistics.mean(processing_times):.1f}с\n")
                f.write(f"Медианное время: {statistics.median(processing_times):.1f}с\n")
                f.write(f"Диапазон времени: {min(processing_times):.1f}с - {max(processing_times):.1f}с\n\n")
        
        print(f"📄 Подробный отчет сохранен: {json_file}")
        print(f"📄 Краткий отчет сохранен: {summary_file}")

def main():
    """Основная функция"""
    benchmark = OCRBenchmark()
    benchmark.run_benchmark()

if __name__ == "__main__":
    main()