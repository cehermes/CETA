@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist python_embeded\python.exe (
  python_embeded\python.exe server.py
) else (
  python server.py || py server.py
)
pause
