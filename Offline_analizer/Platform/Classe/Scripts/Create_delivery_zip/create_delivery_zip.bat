@echo off
cd "%~dp0"
X:\Tools\venv\Scripts\python.exe -W ignore create_delivery_zip.py %*
pause