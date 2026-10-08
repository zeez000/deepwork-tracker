@echo off
setlocal
cd /d "%~dp0"

if not exist "env\Scripts\python.exe" (
    echo ERROR: Run setupdev.bat first.
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies are missing. Run setupdev.bat first.
    exit /b 1
)

"env\Scripts\python.exe" -m alembic upgrade head
if errorlevel 1 (
    echo ERROR: Database migration failed.
    exit /b 1
)

start "Deep Work Backend" /D "%CD%" cmd /k "env\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000"
start "Deep Work Frontend" /D "%CD%\frontend" cmd /k "npm run dev -- --port 5173 --strictPort"

echo.
echo Application servers launched in separate windows.
echo Frontend: http://localhost:5173
echo API docs: http://127.0.0.1:8000/docs
echo Wait until both windows report that their servers are ready.
exit /b 0