@echo off
REM Windows批处理脚本 - 用于打包应用程序

echo ====================================
echo K8s YAML管理工具 - 打包脚本
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
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

echo.
echo 开始打包应用程序...
echo.

pyinstaller --name=K8s_YAML管理工具 --onefile --windowed --clean --noconfirm main.py

if errorlevel 1 (
    echo.
    echo 打包失败！请检查错误信息。
    pause
    exit /b 1
) else (
    echo.
    echo ====================================
    echo 打包成功！
    echo ====================================
    echo.
    echo 可执行文件位置: dist\K8s_YAML管理工具.exe
    echo.
    echo 您可以将该文件复制到任何Windows电脑上运行，无需安装Python环境。
    echo.
)

pause
