@echo off
REM ============================================================
REM  企业文档知识库问答系统 — 一键安装启动脚本 (Windows)
REM  双击运行 或 在命令行执行: setup.bat
REM ============================================================

echo ============================================
echo   企业文档知识库问答系统 — 一键安装
echo ============================================
echo.

REM 1. Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Please install Python 3.11+ first
    echo   https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python found

REM 2. Install dependencies
echo.
echo [INFO] Installing Python dependencies...
cd phase-a-scratch
pip install -r requirements.txt -q
cd ..
echo [OK] Dependencies installed

REM 3. Configure API Key
if not exist "phase-a-scratch\backend\.env" (
    echo.
    echo [INFO] Creating .env from template...
    copy phase-a-scratch\backend\.env.example phase-a-scratch\backend\.env
    echo.
    echo [WARN] Please edit phase-a-scratch\backend\.env to add your API Key:
    echo   DASHSCOPE_API_KEY=sk-your-key
    echo.
    echo   Free registration: https://dashscope.aliyun.com
    echo.
    pause
) else (
    echo [OK] .env already exists
)

REM 4. Import documents
echo.
echo [INFO] Importing test documents...
cd phase-a-scratch\backend
python ingest_all.py
cd ..\..

REM 5. Start
echo.
echo ============================================
echo   Starting server...
echo   Visit: http://localhost:8000
echo   API docs: http://localhost:8000/docs
echo   Press Ctrl+C to stop
echo ============================================
cd phase-a-scratch\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause
