:loop
taskkill /IM setup64.exe
IF %ERRORLEVEL% EQU 0 EXIT
TIMEOUT 1
GOTO :loop