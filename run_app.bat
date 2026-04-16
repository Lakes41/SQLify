@echo off
cd /d "%~dp0"
call SQLify\Scripts\activate.bat
python -m streamlit run src/sqlify/app.py
