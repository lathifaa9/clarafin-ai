@echo off
echo Running Backend Integration Tests...
echo Make sure uvicorn backend is running (run_backend.bat) before starting this test.
python tests/test_backend.py
pause
