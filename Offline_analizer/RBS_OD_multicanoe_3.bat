@echo off
start "" "%CANoe_InstallDir%CANoe64.exe" /f "%~dp0RBS_OD_master_3.cfg" /m Start_CANoe_master /c 192.168.51.5:2809
start "" "%CANoe_InstallDir%CANoe64.exe" /f "%~dp0RBS_OD_slave1_3.cfg" /m Start_CANoe_slave1 /c 192.168.51.6:2809
pause