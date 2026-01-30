#!/usr/bin/env python3
"""
Очистка кеша Streamlit и принудительное обновление адаптеров
"""

import os
import shutil
import tempfile
import sys

def clear_streamlit_cache():
    """Очистка всех кешей Streamlit"""
    
    print("🧹 Очистка кеша Streamlit...")
    
    # Пути к кешам Streamlit
    cache_paths = [
        os.path.expanduser("~/.streamlit"),
        os.path.join(tempfile.gettempdir(), "streamlit"),
        ".streamlit",
        "__pycache__",
    ]
    
    # Очистка кешей
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                if os.path.isdir(cache_path):
                    shutil.rmtree(cache_path)
                    print(f"✅ Удален кеш: {cache_path}")
                else:
                    os.remove(cache_path)
                    print(f"✅ Удален файл: {cache_path}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить {cache_path}: {e}")
    
    # Очистка Python кешей
    print("\n🐍 Очистка Python кешей...")
    
    # Удаление .pyc файлов
    for root, dirs, files in os.walk("."):
        # Пропускаем .git и другие системные папки
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.streamlit']
        
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"✅ Удален .pyc: {pyc_path}")
                except Exception as e:
                    print(f"⚠️ Не удалось удалить {pyc_path}: {e}")
        
        # Удаление __pycache__ папок
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"✅ Удален __pycache__: {pycache_path}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить {pycache_path}: {e}")
    
    print("\n✅ Очистка кеша завершена!")
    print("💡 Теперь перезапустите Streamlit приложение")

if __name__ == "__main__":
    clear_streamlit_cache()