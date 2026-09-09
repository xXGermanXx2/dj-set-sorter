@echo off
cd /d "%~dp0"
python dj_set_sorter.py
if errorlevel 1 pause
