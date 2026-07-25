@echo off
setlocal
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 -m venv .venv
) else (
  python -m venv .venv
)
if errorlevel 1 (
  echo Python 3.10 or later is required to create the backend environment.
  exit /b 1
)
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
echo Setup complete. Run run_backend.bat to start the API.
