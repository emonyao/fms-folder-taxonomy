#!/usr/bin/env python3
# test_new_logic.py

import os
import sys
sys.path.append('scripts')

from scanner import ImageScanner
from matcher import ImageMatcher
from renamer import ImageRenamer

def test_path_processing():
    """测试新的路径处理逻辑"""
    
    # 模拟一些测试路径
    test_paths = [
        "images/1. Jan MM Fair/1. Jan MM Fair/Marketing Form (Rcvd)/0_MMR FS/The Toy Factory Images/MMR_The-Toy-Factory_-Wet-Wipes-Lid-(Pack-of-2).jpg",
        "images/1. Jan MM Fair/1. Jan MM Fair/Marketing Form (Rcvd)/0_MMR FS/Images/Product A/image1.jpg",
        "images/1. Jan MM Fair/1. Jan MM Fair/Marketing Form (Rcvd)/0_MMR FS/Images/Brand X/image2.jpg",
        "images/1. Jan MM Fair/1. Jan MM Fair/Marketing Form (Rcvd)/0_MMR FS/Images/Product B/1.jpg",
    ]
    
    scanner = ImageScanner()
    matcher = ImageMatcher()
    renamer = ImageRenamer()
    
    print("=== 测试 remove_images_folders 函数 ===")
    for path in test_paths:
        clean_path = scanner.remove_images_folders(path)
        print(f"原始路径: {path}")
        print(f"清理后:   {clean_path}")
        print("-" * 80)
    
    print("\n=== 测试路径结构分析 ===")
    for path in test_paths:
        clean_path = scanner.remove_images_folders(path)
        
        # 模拟 scanner 的逻辑
        rel_parts = clean_path.split(os.sep)
        marketing_index = -1
        for i, part in enumerate(rel_parts):
            if part.lower() == "marketing form (rcvd)":
                marketing_index = i
                break
        
        if marketing_index >= 0:
            merchant = rel_parts[marketing_index + 1] if len(rel_parts) > marketing_index + 1 else "unknown"
            after_merchant_parts = rel_parts[marketing_index + 2:]
            
            print(f"原始路径: {path}")
            print(f"清理后:   {clean_path}")
            print(f"Merchant: {merchant}")
            print(f"剩余部分: {after_merchant_parts}")
            
            if len(after_merchant_parts) == 1:
                print(f"结构: A (merchant/image.jpg)")
            elif len(after_merchant_parts) == 2:
                print(f"结构: B (merchant/folder/image.jpg)")
            else:
                print(f"结构: Unknown")
            print("-" * 80)

    print("\n=== 测试重命名结果输出（自动推断） ===")
    for path in test_paths:
        clean_path = scanner.remove_images_folders(path)
        rel_parts = clean_path.split(os.sep)
        marketing_index = -1
        for i, part in enumerate(rel_parts):
            if part.lower() == "marketing form (rcvd)":
                marketing_index = i
                break
        if marketing_index >= 0:
            merchant = rel_parts[marketing_index + 1] if len(rel_parts) > marketing_index + 1 else "unknown"
            after_merchant_parts = rel_parts[marketing_index + 2:]
            structure = "B" if len(after_merchant_parts) == 2 else "A"
            filename = os.path.basename(path)
            base_name = os.path.splitext(filename)[0].lower()
            filename_keywords = base_name.split()
            # 用 matcher 自动推断 info
            info = matcher.match_image(path, structure, filename_keywords, clean_path, merchant)
            new_name = renamer.construct_filename(info)
            print(f"原始路径: {path}")
            print(f"重命名后: {new_name}")
            print(f"info: {info}")
            print("-" * 80)

if __name__ == "__main__":
    test_path_processing()