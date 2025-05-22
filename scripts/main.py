# scripts/main.py
from scanner import scan_image_paths
from matcher import match_metadata
from renamer import rename_file
from logger import log_rename
from config import load_config

def main():
    config = load_config("config.yaml")
    image_paths = scan_image_paths(config["input_folder"])

    for img_path in image_paths:
        metadata = match_metadata(img_path, config)
        new_name, status = rename_file(img_path, metadata, config)
        log_rename(img_path, new_name, status, config)

if __name__ == "__main__":
    main()