@echo off
chcp 65001 >nul
title D07-E NASA IMERG Downloader
where python >nul 2>nul
if errorlevel 1 (
 echo ERROR: Python is not installed or not in PATH.
 pause
 exit /b 1
)
python "%~dp0D07E_download_IMERG_144.py"
pause
