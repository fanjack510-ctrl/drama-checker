#!/bin/bash

echo "========================================"
echo "  剧情短视频体检器 - 后端服务启动"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo "[1/3] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python，请先安装 Python 3.8+"
    exit 1
fi
python3 --version
echo ""

echo "[2/3] 检查并安装依赖..."
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 依赖安装失败"
    exit 1
fi
echo "依赖安装完成"
echo ""

echo "[3/3] 启动服务..."
echo ""
echo "服务地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "健康检查: http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

python run.py

