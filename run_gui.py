#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FMS Folder Taxonomy - GUI启动脚本
"""

import sys
import os

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

def main():
    """启动GUI"""
    try:
        from gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖包")
        input("按回车键退出...")
    except Exception as e:
        print(f"启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main() 