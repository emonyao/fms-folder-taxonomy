#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FMS Folder Taxonomy - EXE打包脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller安装失败: {e}")
        return False

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('scripts', 'scripts'),
        ('data', 'data'),
        ('ai_models', 'ai_models'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'yaml',
        'pandas',
        'numpy',
        'PIL',
        'cv2',
        'sklearn',
        'torch',
        'transformers',
        'difflib',
        'queue',
        'threading',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FMS_Folder_Taxonomy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('FMS_Folder_Taxonomy.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("spec文件创建成功")

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    # 检查是否存在spec文件
    if not os.path.exists('FMS_Folder_Taxonomy.spec'):
        create_spec_file()
    
    try:
        # 使用PyInstaller构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "FMS_Folder_Taxonomy.spec"]
        subprocess.check_call(cmd)
        
        print("exe文件构建成功！")
        print("输出位置: dist/FMS_Folder_Taxonomy.exe")
        
        # 创建发布包
        create_release_package()
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False
    
    return True

def create_release_package():
    """创建发布包"""
    print("创建发布包...")
    
    release_dir = "release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    
    os.makedirs(release_dir)
    
    # 复制exe文件
    exe_source = "dist/FMS_Folder_Taxonomy.exe"
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, release_dir)
    
    # 复制必要的文件夹
    folders_to_copy = ['images', 'data', 'ai_models', 'assets']
    for folder in folders_to_copy:
        if os.path.exists(folder):
            shutil.copytree(folder, os.path.join(release_dir, folder))
    
    # 创建输出目录
    os.makedirs(os.path.join(release_dir, 'output'), exist_ok=True)
    
    # 创建README文件
    readme_content = """# FMS Folder Taxonomy - 图像重命名工具

## 使用说明

1. 双击运行 `FMS_Folder_Taxonomy.exe`
2. 在"主操作"选项卡中设置输入和输出目录
3. 点击"扫描图像"查看找到的图像文件
4. 点击"预览重命名"查看重命名效果
5. 点击"开始重命名"执行重命名操作
6. 在"配置"选项卡中可以调整各种设置
7. 在"日志"选项卡中查看操作日志

## 目录结构

- `images/` - 输入图像目录
- `output/` - 输出目录
  - `renamed/` - 重命名后的图像
  - `dnu/` - 未发布的图像
  - `review/` - 需要审核的图像
- `data/` - 数据文件
- `ai_models/` - AI模型文件
- `assets/` - 资源文件

## 注意事项

- 首次运行前请确保输入目录中有图像文件
- 建议先使用"预览重命名"功能查看效果
- 重命名操作不可逆，请谨慎操作
- 如遇问题请查看日志文件

## 技术支持

如有问题请联系技术支持。
"""
    
    with open(os.path.join(release_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"发布包创建成功: {release_dir}/")

def main():
    """主函数"""
    print("=" * 50)
    print("FMS Folder Taxonomy - EXE打包工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return
    
    # 检查必要文件
    required_files = ['gui.py', 'config.yaml', 'scripts/']
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 缺少必要文件 {file}")
            return
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return
    
    # 构建exe
    if build_exe():
        print("\n" + "=" * 50)
        print("打包完成！")
        print("=" * 50)
        print("发布包位置: release/")
        print("exe文件位置: dist/FMS_Folder_Taxonomy.exe")
    else:
        print("\n打包失败，请检查错误信息")

if __name__ == "__main__":
    main() 