@echo off
cd /d "%~dp0"
call SQLify\Scripts\activate.bat
python -m pip install -r requirements.txt > pip_out.txt 2>&1
python verify.py > verify_out.txt 2>&1
echo Done.
