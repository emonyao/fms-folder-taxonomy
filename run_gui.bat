@echo off
chcp 65001 >nul
echo FMS Folder Taxonomy - 图像重命名工具
echo ========================================

REM 激活 conda 环境
call conda activate fms-ai

REM 检查 Python 版本
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 启动GUI
python run_gui.py

pause 