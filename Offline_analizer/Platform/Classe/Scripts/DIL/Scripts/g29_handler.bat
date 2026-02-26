@echo off
start "g29_handler" X:\Tools\venv\Scripts\python.exe %~dp0\g29_handler_com_ethernet.py debug_mode_off %* rt_rack
if ERRORLEVEL 1 goto ERROR
:ERROR
