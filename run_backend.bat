@echo off
echo Starting SME Financial Document Intelligence Agent Backend...
echo Database will initialize automatically on startup.
if not exist ".venv\Scripts\python.exe" (
  echo Backend environment is missing. Run setup_backend.bat first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8001
pause
