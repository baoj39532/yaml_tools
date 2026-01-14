"""
打包脚本
使用PyInstaller将应用程序打包成可执行文件
"""

import os
import sys
import subprocess

# 设置UTF-8编码，解决Windows控制台中文显示问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def build_exe():
    """构建可执行文件"""
    print("开始打包应用程序...")
    
    # 检测操作系统
    import platform
    is_windows = platform.system() == 'Windows'
    is_mac = platform.system() == 'Darwin'
    
    # PyInstaller参数
    args = [
        sys.executable,  # 使用当前Python解释器
        '-m',
        'PyInstaller',
        '--name=K8s_YAML管理工具',
        '--onefile',  # 打包成单个文件
        '--windowed',  # GUI程序（不显示控制台）
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不确认覆盖
        # 添加数据文件（如果有）
        # '--add-data=resources;resources',
        # 设置图标（如果有）
        # '--icon=resources/icon.ico',
        'main.py'
    ]
    
    # 执行打包
    try:
        print(f"使用Python: {sys.executable}")
        print(f"操作系统: {platform.system()}")
        print("正在打包，请稍候...\n")
        
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n打包完成！")
        
        if is_mac:
            print("可执行文件位置: dist/K8s_YAML管理工具 或 dist/K8s_YAML管理工具.app")
        elif is_windows:
            print("可执行文件位置: dist/K8s_YAML管理工具.exe")
        else:
            print("可执行文件位置: dist/K8s_YAML管理工具")
            
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        print(e.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build_exe()
