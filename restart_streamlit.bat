@echo off
echo ========================================
echo Перезапуск Streamlit приложения
echo ========================================
echo.

echo Останавливаем текущие процессы Streamlit...
taskkill /F /IM streamlit.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Запускаем Streamlit приложение...
start "ChatVLMLLM Streamlit" cmd /k "streamlit run app.py"

echo.
echo ========================================
echo Streamlit перезапущен!
echo Откройте браузер: http://localhost:8501
echo ========================================
pause
