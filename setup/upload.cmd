@echo off
rem Wird von der Windows-Aufgabenplanung alle 15 Minuten gestartet (siehe upload-job.ps1).
rem Laedt alle freigegebenen Videos hoch, deren Posting-Zeit erreicht ist.
cd /d "%~dp0.."
if not exist output mkdir output
set PYTHONUTF8=1
".venv\Scripts\python.exe" -m ki_videos hochladen --faellige >> output\upload.log 2>&1
