"""
一键启动脚本 - 跨平台版本
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python():
    """检查 Python 版本"""
    if sys.version_info < (3, 8):
        print("[错误] 需要 Python 3.8 或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"[✓] Python 版本: {sys.version.split()[0]}")
    return True

def setup_venv():
    """设置虚拟环境"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("[2/3] 正在创建虚拟环境，请稍候（可能需要1-2分钟）...")
        try:
            # 显示进度
            import time
            process = subprocess.Popen(
                [sys.executable, "-m", "venv", "venv"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待完成，最多等待120秒
            try:
                stdout, stderr = process.communicate(timeout=120)
                if process.returncode != 0:
                    print(f"[错误] 虚拟环境创建失败: {stderr}")
                    print("\n提示：如果虚拟环境创建失败，可以尝试：")
                    print("1. 检查 Python 是否已正确安装")
                    print("2. 检查是否有足够的磁盘空间")
                    print("3. 或者直接使用系统 Python（不推荐）")
                    sys.exit(1)
            except subprocess.TimeoutExpired:
                process.kill()
                print("[错误] 虚拟环境创建超时（超过2分钟）")
                sys.exit(1)
            
            print("[✓] 虚拟环境创建完成")
        except Exception as e:
            print(f"[错误] 虚拟环境创建失败: {e}")
            sys.exit(1)
    else:
        print("[✓] 虚拟环境已存在")
    
    # 确定激活脚本路径
    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    return python_path, pip_path

def install_dependencies(pip_path):
    """安装依赖"""
    print("[3/4] 安装依赖...")
    try:
        print("  正在升级 pip...")
        subprocess.run([str(pip_path), "install", "-q", "--upgrade", "pip"], check=True)
        print("  正在安装依赖包（可能需要几分钟）...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("[✓] 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[错误] 依赖安装失败: {e}")
        return False

def start_server(python_path):
    """启动服务器"""
    print("[4/4] 启动服务...")
    print()
    print("=" * 50)
    print("服务地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/health")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 50)
    print()
    
    # 切换到 backend 目录
    os.chdir(Path(__file__).parent)
    
    # 启动 uvicorn
    subprocess.run([
        str(python_path), "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

def main():
    """主函数"""
    print("=" * 50)
    print("  剧情短视频体检器 - 后端服务启动")
    print("=" * 50)
    print()
    
    # 检查 Python
    if not check_python():
        sys.exit(1)
    
    # 切换到脚本所在目录
    os.chdir(Path(__file__).parent)
    
    # 设置虚拟环境
    python_path, pip_path = setup_venv()
    
    # 安装依赖
    if not install_dependencies(pip_path):
        sys.exit(1)
    
    # 启动服务
    try:
        start_server(python_path)
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n[错误] 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

