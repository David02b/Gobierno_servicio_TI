@echo off
REM Abre el Dashboard Estrategico de TI en el navegador.
cd /d "%~dp0"
python -m streamlit run app.py
if errorlevel 1 "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -m streamlit run app.py
pause
