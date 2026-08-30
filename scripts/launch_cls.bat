@echo off
setlocal
title CLS RAG+CAG Prototype
cd /d "%~dp0.."
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch_cls.ps1" %*
if errorlevel 1 pause
endlocal
