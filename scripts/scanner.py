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
        Remove all "Images", "USE THIS" and "Pre Order & Starbuy" folders from the path, and remove consecutive duplicate folder names
        """
        norm_path = path.replace('/', os.sep).replace('\\', os.sep)
        parts = norm_path.split(os.sep)
        # First remove target folders
        filtered_parts = [part for part in parts if part.lower() not in ("images", "use this", "pre order & starbuy")]
        # Then remove consecutive duplicate folder names
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
                continue  # Only process folders named 'Marketing Form (Rcvd)'

            for merchant_folder in dirnames:  # Enter each merchant folder
                merchant_path = os.path.join(dirpath, merchant_folder)
                for root, _, files in os.walk(merchant_path):  # Recursively scan images under each merchant folder
                    for f in files:
                        if f.lower().endswith(self.extensions):
                            full_path = os.path.join(root, f)

                            # 20250709 add
                            # Find the index of 'Marketing Form (Rcvd)' and take the part after it
                            normalized_path = os.path.normpath(full_path)  # Normalize path
                            path_parts = normalized_path.split(os.sep)

                            # Locate 'Marketing Form (Rcvd)' and start from its next level
                            relative_parts = []
                            for i, part in enumerate(path_parts):
                                if part.lower() == "marketing form (rcvd)":
                                    relative_parts = path_parts[i + 1:]
                                    break
                            
                            # 20250709 change
                            # Remove all "Images" folders from the path
                            # clean_path = self.remove_images_folders(full_path)
                            clean_path = self.remove_images_folders(os.path.join(*relative_parts))
                            
                            # 20250709 change
                            # Path relative to Marketing Form (Rcvd)
                            # rel_to_marketing = os.path.relpath(clean_path, dirpath)
                            # parts = rel_to_marketing.split(os.sep)
                            parts = clean_path.split(os.sep)
                            
                            # Extract merchant (the first folder)
                            merchant = parts[0] if len(parts) > 0 else "unknown"
                            
                            # Determine structure based on remaining path length
                            remaining_parts = parts[1:] if len(parts) > 1 else []
                            
                            if len(remaining_parts) == 1:
                                # merchant/image.jpg
                                structure = "A"
                            elif len(remaining_parts) == 2:
                                # merchant/brand/image.jpg or merchant/product/image.jpg
                                # Need to further determine if it's brand or product
                                # Temporarily mark as B, further processing in matcher
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
