@echo off
title PC Check Learning Windows Original Install Date 
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
echo             https://pc-check-learning.netlify.app/
echo ------------------------------------------------------------
echo   Checking Windows Original Install Date ...
echo ------------------------------------------------------------

:: Use PowerShell to get the install date cleanly
powershell -NoLogo -NoProfile -Command ^
    "(Get-CimInstance Win32_OperatingSystem).InstallDate | Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"

echo ------------------------------------------------------------
echo Press any key to exit...
pause >nul
