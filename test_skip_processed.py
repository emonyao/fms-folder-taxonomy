#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试跳过已处理图片的功能
"""

import os
import sys
sys.path.append('scripts')

from scripts.scanner import ImageScanner

def test_skip_processed():
    """测试跳过已处理图片的功能"""
    print("开始测试跳过已处理图片的功能...")
    
    # 创建扫描器实例
    scanner = ImageScanner()
    
    # 测试检查已处理图片的方法
    print("\n1. 测试 is_image_processed 方法:")
    
    # 创建一个测试图片路径
    test_image_path = "images/1. Jan MM Fair/Marketing Form (Rcvd)/0_MMR FS/The Toy Factory Images/MMR_The-Toy-Factory_-Wet-Wipes-Lid-(Pack-of-2).jpg"
    
    # 检查这个图片是否已经被处理过
    is_processed = scanner.is_image_processed(test_image_path)
    print(f"图片路径: {test_image_path}")
    print(f"是否已处理: {is_processed}")
    
    # 测试扫描功能
    print("\n2. 测试 scan_image_paths 方法:")
    try:
        image_paths = scanner.scan_image_paths()
        print(f"扫描到的图片数量: {len(image_paths)}")
        
        if image_paths:
            print("前5个图片路径:")
            for i, (full_path, structure, clean_path, merchant) in enumerate(image_paths[:5]):
                print(f"  {i+1}. {full_path}")
                print(f"     Structure: {structure}, Merchant: {merchant}")
        else:
            print("没有扫描到图片")
            
    except Exception as e:
        print(f"扫描过程中出现错误: {e}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_skip_processed() 