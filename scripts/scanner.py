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
 
    # def scan_image_paths(root, extensions=(".jpg", ".jpeg", ".png")):
    def scan_image_paths(self) -> List[str]:

        """
        Recursively scan for image files in the given directory.
        """
        
        image_paths = []

        # 20250623 change input folder
        # for dirpath, dirnames, filenames in os.walk(self.input_folder):
        #     if os.path.basename(dirpath).lower() != "images for ops":
        #         continue  # Skip folders that are not 'Images for Ops'

        #     for root, _, files in os.walk(dirpath):  # scan within Images for Ops and its subdirs
        #         for f in files:
        #             if f.lower().endswith(self.extensions):
        #                 image_paths.append(os.path.join(root, f))
        
        for dirpath, dirnames, filenames in os.walk(self.input_folder):
            if os.path.basename(dirpath).lower() != "marketing form (rcvd)":
                continue  # 只处理名为 'Marketing Form (Rcvd)' 的文件夹

            for merchant_folder in dirnames:  # 进入每个 merchant 文件夹
                merchant_path = os.path.join(dirpath, merchant_folder)
                for root, _, files in os.walk(merchant_path):  # 递归扫描每个 merchant 文件夹下的图像
                    for f in files:
                        if f.lower().endswith(self.extensions):
                            full_path = os.path.join(root, f)
                            # 20250627 add 3 types of filepath
                            # image_paths.append(full_path)  
                            rel = os.path.relpath(full_path, merchant_path)
                            parts = rel.split(os.sep)

                            if len(parts) == 2:
                                structure = "A"  # merchant/Images/image.jpg
                            elif len(parts) == 3:
                                structure = "B"  # merchant/Images/Product/image.jpg
                            elif len(parts) == 4:
                                structure = "C"  # merchant/Images/Brand/image.jpg
                            else:
                                structure = "Unknown"

                            image_paths.append((full_path, structure))


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
