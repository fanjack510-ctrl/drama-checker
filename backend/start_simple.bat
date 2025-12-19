@echo off
chcp 65001 >nul
echo ========================================
echo   剧情短视频体检器 - 后端服务启动（简化版）
echo   不使用虚拟环境，直接使用系统 Python
echo ========================================
echo.

cd /d %~dp0

echo [1/2] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
python --version
echo.

echo [2/2] 安装依赖...
pip install -q --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [✓] 依赖安装完成
echo.

echo 启动服务...
echo.
echo 服务地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python run.py

pause

