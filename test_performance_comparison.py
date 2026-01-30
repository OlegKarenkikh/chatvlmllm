#!/usr/bin/env python3
"""
Тест сравнения производительности моделей на основе исторических данных
"""

import streamlit as st
import sys
import os

# Добавляем путь к utils
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

def test_performance_comparison():
    """Тестирование сравнения производительности"""
    
    st.title("🧪 Тест сравнения производительности моделей")
    st.caption("Проверка работы анализатора исторических данных")
    
    try:
        from utils.performance_analyzer import PerformanceAnalyzer
        
        # Загрузка данных
        with st.spinner("Загрузка исторических результатов..."):
            analyzer = PerformanceAnalyzer()
            comparison_df = analyzer.get_model_comparison_data()
            stats = analyzer.get_summary_statistics()
        
        # Проверка результатов
        st.subheader("📊 Результаты анализа")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Общая статистика:**")
            st.json(stats)
        
        with col2:
            st.markdown("**📋 Найденные модели:**")
            if not comparison_df.empty:
                st.write(f"Всего моделей: {len(comparison_df)}")
                st.write("Модели:")
                for model in comparison_df["Модель"].tolist():
                    st.write(f"• {model}")
            else:
                st.warning("Нет данных для отображения")
        
        # Таблица сравнения
        if not comparison_df.empty:
            st.subheader("📋 Таблица сравнения")
            
            # Цветовое кодирование
            def color_status(val):
                if "✅" in str(val):
                    return 'background-color: #d4edda'
                elif "⚠️" in str(val):
                    return 'background-color: #fff3cd'
                elif "❌" in str(val):
                    return 'background-color: #f8d7da'
                return ''
            
            styled_df = comparison_df.style.applymap(color_status, subset=['Статус'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Детальный анализ
            st.subheader("🔍 Детальный анализ")
            
            selected_model = st.selectbox(
                "Выберите модель:",
                comparison_df["Модель"].tolist()
            )
            
            if selected_model:
                details = analyzer.get_model_details(selected_model)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 Детали модели:**")
                    st.json(details)
                
                with col2:
                    st.markdown("**📈 Тренды:**")
                    trends = analyzer.get_performance_trends(selected_model)
                    st.json(trends)
        
        else:
            st.warning("📋 Нет исторических данных для сравнения")
            st.info("Запустите тесты для получения данных")
        
        # Информация о файлах
        st.subheader("📁 Найденные файлы с результатами")
        
        import glob
        result_files = []
        patterns = [
            "benchmark_results_*.json",
            "*_test_results*.json", 
            "final_working_models.json",
            "working_models_config.json"
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            result_files.extend(files)
        
        if result_files:
            st.success(f"Найдено {len(result_files)} файлов с результатами:")
            for file in result_files:
                st.write(f"• {file}")
        else:
            st.warning("Файлы с результатами не найдены")
            st.info("Запустите бенчмарки для создания данных")
    
    except ImportError as e:
        st.error(f"Ошибка импорта: {e}")
        st.code("pip install pandas")
    
    except Exception as e:
        st.error(f"Ошибка: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    # Инструкции
    st.divider()
    st.subheader("📝 Инструкции")
    
    st.markdown("""
    **Для получения данных о производительности:**
    
    1. **Запустите бенчмарк:**
       ```bash
       python benchmark_dots_ocr.py
       ```
    
    2. **Протестируйте модели:**
       ```bash
       python test_working_models_only.py
       ```
    
    3. **Проверьте результаты:**
       ```bash
       python utils/performance_analyzer.py
       ```
    
    **Файлы с результатами:**
    - `benchmark_results_*.json` - результаты бенчмарков
    - `final_working_models.json` - статус моделей
    - `*_test_results*.json` - результаты тестов
    """)

def main():
    """Главная функция"""
    
    st.set_page_config(
        page_title="Тест сравнения производительности",
        page_icon="🧪",
        layout="wide"
    )
    
    test_performance_comparison()

if __name__ == "__main__":
    main()