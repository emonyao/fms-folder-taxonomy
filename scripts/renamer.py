# scripts/renamer.py

import os
import shutil
from typing import Dict
from config import load_config
from logger import RenameLogger
from matcher import ImageMatcher
from scanner import ImageScanner



class ImageRenamer:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.image_dir = self.config["input_folder"]
        self.output_dir = self.config["output_renamed"]
        os.makedirs(self.output_dir, exist_ok=True)

        self.logger = RenameLogger()
        # self.scanner = ImageScanner(self.config)1
        self.scanner = ImageScanner(config_path)

        self.matcher = ImageMatcher()


    def slugify(self, text: str) -> str:
        return text.strip().lower().replace(" ", "_").replace("/", "_").replace("\\", "_")

    def construct_filename(self, info_dict: Dict, version: int = 1) -> str:
        merchant = self.slugify(info_dict.get("merchant", "unknown"))
        brand = self.slugify(info_dict.get("brand", "unknown"))
        product = self.slugify(info_dict.get("product", "unknown"))
        variation = self.slugify(info_dict.get("variation", "unknown"))

        base_name = f"{merchant}_{brand}_{product}_{variation}"
        if version > 1:
            base_name += f"_v{version}"
        return base_name + ".jpg"

    def resolve_conflict(self, output_dir: str, filename: str) -> str:
        name, ext = os.path.splitext(filename)
        version = 1
        candidate = filename
        while os.path.exists(os.path.join(output_dir, candidate)):
            version += 1
            candidate = f"{name}_v{version}{ext}"
        return candidate

    def rename_images(self, dry_run: bool = False):
        image_paths = self.scanner.scan_image_paths()
        self.logger.write_image_list(image_paths)

        matched_info = self.matcher.batch_match(image_paths)

        for info in matched_info:
            old_path = info["original_path"]
            original_dir = os.path.dirname(old_path)
            parent_folder = os.path.basename(os.path.dirname(old_path)).upper()
            group_key = parent_folder if parent_folder in ["PO", "SB"] else ""
            
            variation_counters = {} 

            count = variation_counters.get(group_key, 0) + 1
            variation_counters[group_key] = count

            if group_key in ["PO", "SB"]:
                info["vatiation"] = f"_{group_key}_{count}"
            else:
                info["variation"] = str(count)
            new_name = self.construct_filename(info)
            new_name = self.resolve_conflict(original_dir, new_name)
            new_path = os.path.join(original_dir, new_name)

            try:
                if dry_run:
                    print(f"[DRY RUN] Would rename: {old_path} → {new_path}")
                else:
                    os.rename(old_path, new_path)
                    print(f" Renamed: {old_path} → {new_path}")

                self.logger.log_rename(old_path, new_path, status="Renamed" if not dry_run else "DryRun", source=info["match_source"])
            except Exception as e:
                log_rename(old_path, "", status="Failed", source=str(e))
                print(f" Rename failed: {old_path} — {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run without renaming files")
    args = parser.parse_args()

    renamer = ImageRenamer()
    renamer.rename_images(dry_run=args.dry_run)
