@echo off
title Vlad's Multi Tool
chcp 65001 >nul
color 09
mode con: cols=60 lines=20

:menu
cls
echo.			██╗   ██╗██╗      █████╗ ██████╗ 
echo.			██║   ██║██║     ██╔══██╗██╔══██╗
echo.			██║   ██║██║     ███████║██║  ██║
echo.			╚██╗ ██╔╝██║     ██╔══██║██║  ██║
echo.			 ╚████╔╝ ███████╗██║  ██║██████╔╝
echo.			  ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═════╝ 
echo.
echo ------------------------------------------------------------
echo   [1]  Open WinPrefetchView
echo   [2]  Open SrumECmd
echo   [3]  Open SystemInformer
echo   [4]  Open MFTECmd
echo   [5]  Open TimelineExplorer
echo ------------------------------------------------------------
echo.
set /p choice=   Select an option (1-5):

if "%choice%"=="1" goto WinPrefetchView
if "%choice%"=="2" goto SrumECmd
if "%choice%"=="3" goto SystemInformer
if "%choice%"=="4" goto MFTECmd
if "%choice%"=="5" goto TimelineExplorer

echo Invalid choice. Please try again.
pause
goto menu

:winprefetchview
start "" "https://www.nirsoft.net/utils/winprefetchview-x64.zip"
goto menu

:srumecmd
start "" "https://download.ericzimmermanstools.com/SrumECmd.zip"
goto menu

:systeminformer
start "" "https://github.com/winsiderss/si-builds/releases/download/3.2.25215.2022/systeminformer-3.2.25215.2022-canary-setup.exe"
goto menu

:mftecmd
start "" "https://download.ericzimmermanstools.com/MFTECmd.zip"
goto menu

:timelineexplorer
start "" "https://download.ericzimmermanstools.com/net9/TimelineExplorer.zip"
goto menu
