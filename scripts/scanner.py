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
        # for dirpath, _, filenames in os.walk(self.input_folder):
        #     for f in filenames:
        #         if f.lower().endswith(self.extensions):
        #             image_paths.append(os.path.join(dirpath, f))
        for dirpath, dirnames, filenames in os.walk(self.input_folder):
            if os.path.basename(dirpath).lower() != "images for ops":
                continue  # Skip folders that are not 'Images for Ops'

            for root, _, files in os.walk(dirpath):  # scan within Images for Ops and its subdirs
                for f in files:
                    if f.lower().endswith(self.extensions):
                        image_paths.append(os.path.join(root, f))
        
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
    # config = load_config("config.yaml")
    # image_dir = config["input_folder"]

    # print(f"Scanning images from: {image_dir}")
    # paths = scan_image_paths(image_dir)
    # print(f"Found {len(paths)} image(s)")

    # write_image_list_csv(paths)  # call logger.py and write to csv
    # print("Image list saved to: output/image_list.csv")
    scanner = ImageScanner() 
    scanner.export_image_list()
