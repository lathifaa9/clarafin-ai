@echo off
echo Starting Clarafin backend server...
python -m uvicorn clarafin.backend.app.main:app --reload
pause
