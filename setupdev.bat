@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python must be installed and available on PATH.
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js and npm must be installed.
    exit /b 1
)

where java >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java must be installed and available on PATH.
    exit /b 1
)

if not exist "env\Scripts\python.exe" (
    python -m venv env
    if errorlevel 1 goto failed
)

echo Installing Python dependencies...
"env\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed

echo Installing SDK generator...
call npm ci
if errorlevel 1 goto failed

echo Installing frontend dependencies...
call npm --prefix frontend ci
if errorlevel 1 goto failed

echo Applying database migrations...
"env\Scripts\python.exe" -m alembic upgrade head
if errorlevel 1 goto failed

echo Loading demo sessions...
"env\Scripts\python.exe" load_seed.py
if errorlevel 1 goto failed

echo Exporting OpenAPI specification...
"env\Scripts\python.exe" export_openapi.py
if errorlevel 1 goto failed

echo Generating Python SDK...
call npx openapi-generator-cli generate -i openapi.json -g python -o sdk --additional-properties=packageName=deepwork_sdk,projectName=deepwork-sdk,packageVersion=1.0.0
if errorlevel 1 goto failed

echo Installing generated SDK...
"env\Scripts\python.exe" -m pip install -e sdk
if errorlevel 1 goto failed

echo Running backend tests...
"env\Scripts\python.exe" -m pytest tests -q
if errorlevel 1 goto failed

echo Building frontend...
call npm --prefix frontend run build
if errorlevel 1 goto failed

echo.
echo Development setup completed successfully.
exit /b 0

:failed
echo.
echo ERROR: Setup failed. Check the error message above.
exit /b 1