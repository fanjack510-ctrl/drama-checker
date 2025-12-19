@echo off
chcp 65001 >nul
echo ========================================
echo   剧情短视频体检器 - 后端服务启动
echo ========================================
echo.

cd /d %~dp0

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)
python --version
echo.

echo [2/3] 检查并安装依赖...
if not exist "venv" (
    echo 正在创建虚拟环境，请稍候（可能需要1-2分钟）...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        echo.
        echo 提示：如果虚拟环境创建失败，可以尝试：
        echo 1. 检查 Python 是否已正确安装
        echo 2. 检查是否有足够的磁盘空间
        echo 3. 或者直接使用系统 Python（不推荐）
        echo.
        pause
        exit /b 1
    )
    echo [✓] 虚拟环境创建完成
) else (
    echo [✓] 虚拟环境已存在
)
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 无法激活虚拟环境
    pause
    exit /b 1
)
echo 正在升级 pip...
pip install --upgrade pip >nul 2>&1
echo 正在安装依赖包（可能需要几分钟）...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [✓] 依赖安装完成
echo.

echo [3/3] 启动服务...
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

