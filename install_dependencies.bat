@echo off
chcp 65001 >nul
echo FMS Folder Taxonomy - 依赖安装工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 正在安装依赖包...
python install_dependencies.py

if errorlevel 1 (
    echo.
    echo 依赖安装失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo 依赖安装完成！
echo 现在可以运行 run_gui.bat 启动程序
pause 