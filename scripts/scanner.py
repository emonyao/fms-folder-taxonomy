# scripts/scanner.py

import os
from config import load_config
from logger import write_image_list_csv

def scan_image_paths(root, extensions=(".jpg", ".jpeg", ".png")):
    """
    Recursively scan for image files in the given directory.
    """
    image_paths = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.lower().endswith(extensions):
                image_paths.append(os.path.join(dirpath, f))
    return image_paths

if __name__ == "__main__":
    config = load_config("config.yaml")
    image_dir = config["input_folder"]

    print(f"Scanning images from: {image_dir}")
    paths = scan_image_paths(image_dir)
    print(f"Found {len(paths)} image(s)")

    write_image_list_csv(paths)  # call logger.py and write to csv
    print("Image list saved to: output/image_list.csv")
