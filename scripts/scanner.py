# scripts/scanner.py

import os
import csv
from config import load_config

def scan_image_paths(root, extensions=(".jpg", ".jpeg", ".png")):
    """
    Recursively scan for image files in the given directory.
    
    Parameters:
        root (str): Root directory to scan.
        extensions (tuple): Valid image file extensions.

    Returns:
        List[str]: List of image file paths.
    """
    image_paths = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.lower().endswith(extensions):
                image_paths.append(os.path.join(dirpath, f))
    return image_paths

if __name__ == "__main__":
    config = load_config("config.yaml") # 加载配置
    image_dir = config["input_folder"]
    print(f"Scanning images from: {image_dir}")

    paths = scan_image_paths(image_dir)
    print(f"Found {len(paths)} image(s):")

    with open("output/image_list.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Index", "Image Path"])
        for i, path in enumerate(paths, 1):
            writer.writerow([i, path])
            
    for path in paths:
        print(path)
