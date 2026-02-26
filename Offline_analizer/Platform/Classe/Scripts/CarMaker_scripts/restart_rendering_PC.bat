@echo off
setlocal enableextensions
net use \\192.168.1.15\admin$ /user:Administrator ""
Shutdown /m \\192.168.1.15 /r /f