@echo off
rem Double-click launcher for the JLS RAG+CAG Streamlit prototype.
title JLS RAG+CAG Prototype
cd /d "%~dp0.."
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch_jls.ps1" %*
