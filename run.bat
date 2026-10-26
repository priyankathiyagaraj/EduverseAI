@echo off
title EduVerse AI - Smart College Recommendation System
cd /d "%~dp0"
echo =======================================================
echo          Starting EduVerse AI Application...
echo =======================================================
call venv\Scripts\activate.bat
python run.py
pause
