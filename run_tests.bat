@echo off
echo Running Backend Integration Tests...
echo Make sure the backend is running on http://127.0.0.1:8001 (run_backend.bat) before starting this test.
if not exist ".venv\Scripts\python.exe" (
  echo Backend environment is missing. Run setup_backend.bat first.
  pause
  exit /b 1
)
set BASE_URL=http://127.0.0.1:8001
.venv\Scripts\python.exe tests\test_backend.py
pause
