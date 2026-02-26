@echo off
start "vGETK_Automation_Server" /MIN X:\Tools\venv\Scripts\python.exe -3.10 %~dp0\vgetk_rpyc_server.py %*
