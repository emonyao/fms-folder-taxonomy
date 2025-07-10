#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FMS Folder Taxonomy - 依赖安装脚本
"""

import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{package} 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("FMS Folder Taxonomy - 依赖安装工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        input("按回车键退出...")
        return
    
    # 升级pip
    print("正在升级pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("pip升级成功")
    except subprocess.CalledProcessError:
        print("pip升级失败，继续安装其他包...")
    
    # 需要安装的包
    packages = [
        "numpy>=2.0.2",
        "pandas>=2.2.3",
        "PyYAML",
        "Pillow>=9.0.0",
        "opencv-python>=4.5.0",
        "scikit-learn>=1.0.0",
        "pyinstaller>=5.0"
    ]
    
    # 可选包（AI相关）
    optional_packages = [
        "torch>=1.9.0",
        "transformers>=4.20.0"
    ]
    
    print("\n正在安装必需依赖...")
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n必需依赖安装完成: {success_count}/{len(packages)}")
    
    # 询问是否安装AI相关依赖
    print("\n是否安装AI相关依赖？(y/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['y', 'yes', '是']:
        print("\n正在安装AI相关依赖...")
        ai_success_count = 0
        for package in optional_packages:
            if install_package(package):
                ai_success_count += 1
        print(f"AI依赖安装完成: {ai_success_count}/{len(optional_packages)}")
    
    print("\n" + "=" * 50)
    print("依赖安装完成！")
    print("=" * 50)
    print("现在可以运行以下命令启动GUI:")
    print("  python run_gui.py")
    print("或者双击 run_gui.bat")
    print("\n要打包成exe文件，请运行:")
    print("  python build_exe.py")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 