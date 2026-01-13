@echo off
REM Windows批处理脚本 - 用于运行应用程序（开发模式）

echo ====================================
echo K8s YAML管理工具 - 运行脚本
echo ====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.9或更高版本
    pause
    exit /b 1
)

echo 正在检查依赖...
pip show PyQt5 >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
)

echo.
echo 启动应用程序...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo 程序异常退出！
    pause
)
