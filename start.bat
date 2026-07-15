@echo off
REM Credit-Scraper 微服务启动脚本
REM 用法: 双击运行或在命令行中执行 start.bat

cd /d "%~dp0"

chcp 65001 >nul

echo ============================================================
echo    Credit-Scraper 网页爬取微服务
echo ============================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] 虚拟环境不存在，请先运行: python -m venv .venv
    echo         然后安装依赖: .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo [INFO] 检查依赖...
.venv\Scripts\python.exe -c "import fastapi, uvicorn, pydantic, playwright, bs4, markdownify" 2>nul
if errorlevel 1 (
    echo [INFO] 安装依赖中...
    .venv\Scripts\python.exe -m pip install fastapi uvicorn pydantic playwright beautifulsoup4 markdownify -q
)

echo [INFO] 启动服务...
.venv\Scripts\python.exe main.py

pause
