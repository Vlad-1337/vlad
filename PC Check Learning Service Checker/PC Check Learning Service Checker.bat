@echo off
title PC Check Learning Service Checker
chcp 65001 >nul
color 09
mode con: cols=80 lines=30

:header
cls
echo.   ██╗   ██╗██╗      █████╗ ██████╗ 
echo.   ██║   ██║██║     ██╔══██╗██╔══██╗
echo.   ██║   ██║██║     ███████║██║  ██║
echo.   ╚██╗ ██╔╝██║     ██╔══██║██║  ██║
echo.    ╚████╔╝ ███████╗██║  ██║██████╔╝
echo.     ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═════╝ 
echo.
echo              Made By PC Check Learning
echo				https://pc-check-learning.netlify.app/
echo ------------------------------------------------------------
echo   Checking Services ...
echo ------------------------------------------------------------

powershell -NoLogo -NoProfile -Command ^
    "Get-Service | Where-Object { $_.Name -match '^(pcasvc|DPS|Diagtrack|sysmain|eventlog|sgrmbroker|CDPUserSvc_406df|appinfo|WSearch|vmicvss|vss)$' } | Format-Table -AutoSize"

echo ------------------------------------------------------------
echo Press any key to exit...
pause >nul
