# scripts/scanner.py

import os
from typing import List, Tuple
from config import load_config
from logger import RenameLogger

class ImageScanner:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.input_folder: str = self.config.get("input_folder", "images/")
        self.extensions: Tuple[str] = (".jpg", ".jpeg", ".png")
        self.logger = RenameLogger()

    def debug_log(self, msg: str):
        with open("output/renamer_debug_log.txt", "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")
            
    def remove_images_folders(self, path: str) -> str:
        """
        从路径中移除所有的 "Images"、"USE THIS" 和 "Pre Order & Starbuy" 文件夹，并去除连续重复的文件夹名
        """
        norm_path = path.replace('/', os.sep).replace('\\', os.sep)
        parts = norm_path.split(os.sep)
        # 先移除目标文件夹
        filtered_parts = [part for part in parts if part.lower() not in ("images", "use this", "pre order & starbuy")]
        # 再去除连续重复的文件夹名
        deduped_parts = []
        for part in filtered_parts:
            if not deduped_parts or deduped_parts[-1].lower() != part.lower():
                deduped_parts.append(part)
        return os.sep.join(deduped_parts)

    def scan_image_paths(self) -> List[Tuple[str, str, str, str]]:
        """
        Recursively scan for image files in the given directory.
        Returns: List of tuples (full_path, structure, clean_path, merchant)
        """
        
        image_paths = []

        for dirpath, dirnames, filenames in os.walk(self.input_folder):
            if os.path.basename(dirpath).lower() != "marketing form (rcvd)":
                continue  # 只处理名为 'Marketing Form (Rcvd)' 的文件夹

            for merchant_folder in dirnames:  # 进入每个 merchant 文件夹
                merchant_path = os.path.join(dirpath, merchant_folder)
                for root, _, files in os.walk(merchant_path):  # 递归扫描每个 merchant 文件夹下的图像
                    for f in files:
                        if f.lower().endswith(self.extensions):
                            full_path = os.path.join(root, f)

                            # 20250709 add
                            # 找到 'Marketing Form (Rcvd)' 的索引，并截取之后的部分
                            normalized_path = os.path.normpath(full_path)  # 标准化路径
                            path_parts = normalized_path.split(os.sep)

                            # 定位 'Marketing Form (Rcvd)' 并从其下一级开始
                            relative_parts = []
                            for i, part in enumerate(path_parts):
                                if part.lower() == "marketing form (rcvd)":
                                    relative_parts = path_parts[i + 1:]
                                    break
                            
                            # 20250709 change
                            # 移除所有 "Images" 文件夹后的路径
                            # clean_path = self.remove_images_folders(full_path)
                            clean_path = self.remove_images_folders(os.path.join(*relative_parts))
                            
                            # 20250709 change
                            # 相对于 Marketing Form (Rcvd) 的路径
                            # rel_to_marketing = os.path.relpath(clean_path, dirpath)
                            # parts = rel_to_marketing.split(os.sep)
                            parts = clean_path.split(os.sep)
                            
                            # 提取 merchant（第一个文件夹）
                            merchant = parts[0] if len(parts) > 0 else "unknown"
                            
                            # 根据剩余路径长度判断结构
                            remaining_parts = parts[1:] if len(parts) > 1 else []
                            
                            if len(remaining_parts) == 1:
                                # merchant/image.jpg
                                structure = "A"
                            elif len(remaining_parts) == 2:
                                # merchant/brand/image.jpg 或 merchant/product/image.jpg
                                # 这里需要进一步判断是 brand 还是 product
                                # 暂时标记为 B，在 matcher 中进一步处理
                                structure = "B"
                            else:
                                structure = "Unknown"
                            self.debug_log(f"[1. CLEAN PATH AND PARTS - merchant]: {merchant}")
                            self.debug_log(f"[1. CLEAN PATH AND PARTS - remaining_parts]: {remaining_parts}")
                            self.debug_log(f"[1. CLEAN PATH AND PARTS - structure]: {structure}")
                            self.debug_log(f"[1. CLEAN PATH AND PARTS - fullpath]: {full_path}")
                            self.debug_log(f"[1. CLEAN PATH AND PARTS - cleanpath]: {clean_path}")
                            image_paths.append((full_path, structure, clean_path, merchant))

        return image_paths

    def export_image_list(self, output_path: str = "output/image_list.csv"):
        """
        Scan and write image list to CSV with original filenames.
        """
        paths = self.scan_image_paths()
        print(f"Found {len(paths)} image(s) in {self.input_folder}")
        # write_image_list_csv(paths, output_path)
        logger = RenameLogger()
        logger.write_image_list(paths)

        print(f"Image list saved to: {output_path }")

if __name__ == "__main__":
    scanner = ImageScanner() 
    scanner.export_image_list()
