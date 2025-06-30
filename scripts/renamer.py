# scripts/renamer.py

import os
import csv
import re
import shutil
from typing import Dict
from config import load_config
from logger import RenameLogger
from matcher import ImageMatcher
from scanner import ImageScanner
from utils import extract_color_phrase



class ImageRenamer:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.image_dir = self.config["input_folder"]
        self.output_dir = self.config["output_renamed"]
        os.makedirs(self.output_dir, exist_ok=True)

        self.logger = RenameLogger()
        # self.scanner = ImageScanner(self.config)
        self.scanner = ImageScanner(config_path)

        self.matcher = ImageMatcher()

        



    def slugify(self, text: str) -> str:
        text = str(text)
        return text.strip().lower().replace(" ", "_").replace("/", "_").replace("\\", "_")

    def clean_text_keep_space(self, text: str) -> str:
        """
        Lowercase and remove slashes but keep internal spaces.
        """
        text = str(text)
        return text.strip().lower().replace("/", "_").replace("\\", "_")

    def construct_filename(self, info_dict: Dict, version: int = 1) -> str:
        merchant = self.clean_text_keep_space(info_dict.get("merchant", "unknown"))
        brand = self.clean_text_keep_space(info_dict.get("brand", "unknown"))
        product = self.clean_text_keep_space(info_dict.get("product", "unknown"))
        variation = self.clean_text_keep_space(info_dict.get("variation", "unknown"))

        # base_name = f"{merchant}_{brand}_{product}_{variation}"
        parts = [merchant]
        if brand and brand != merchant:
            parts.append(brand)
        if product:
            parts.append(product)
        if variation:
            parts.append(variation)

        base_name = "_".join(filter(None, parts))
        
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
        variation_counters = {} 
        image_paths = self.scanner.scan_image_paths()
        self.logger.write_image_list(image_paths)

        matched_info = self.matcher.batch_match(image_paths)

        for info in matched_info:
            # 20250627 add
            if info["match_source"] == "FromBrand":
                print(f"🟡 Skipping brand image: {info['original_path']}")
                continue

            old_path = info["original_path"]
            original_dir = os.path.dirname(old_path)
            parent_folder = os.path.basename(original_dir).upper()

            group_key = parent_folder if parent_folder in ["PO", "SB"] else ""
            
            merchant = self.slugify(info.get("merchant", "unknown"))
            brand = self.slugify(info.get("brand", "unknown"))
            # 20250627 using product name from folder first
            # product = self.slugify(info.get("product", "unknown"))
            if info["match_source"] == "FromProduct" and info.get("product_from_folder"):
                product = self.slugify(info["product_from_folder"])
            else:
                product = self.slugify(info.get("product", "unknown"))


            name_key = f"{merchant}_{brand}_{product}"
            counter_key = (name_key, group_key)

            count = variation_counters.get(counter_key, 0) + 1
            variation_counters[counter_key] = count

            # 20250619 change variation logic
            # if group_key in ["PO", "SB"]:
            #     info["variation"] = f"_{group_key.lower()}_{count}"
            # else:
            #     info["variation"] = str(count)
            variation_parts = []
            
            # 颜色提取，防止重复加入
            color_or_material = extract_color_phrase(info["filename"])
            product_text = info.get("product", "").lower()

            # 颜色只在 product 中不存在时加入
            if color_or_material and color_or_material not in product_text:
                variation_parts.append(color_or_material)

            if count > 1:
                variation_parts.append(str(count))
            if group_key in ["PO", "SB"]:
                variation_parts.append(group_key.lower())
                
            info["variation"] = "_".join(variation_parts)

            if info["match_source"] == "NotFound":
                # keep original filename
                original_base = os.path.splitext(info["filename"])[0]
                info["product"] = original_base  # keep original filename as product name


            new_name = self.construct_filename(info)
            new_name = self.resolve_conflict(original_dir, new_name)
            new_path = os.path.join(original_dir, new_name)

            try:
                if dry_run:
                    print(f"[DRY RUN] Would rename: {old_path} → {new_path}")
                else:
                    os.rename(old_path, new_path)
                    print(f" Renamed: {old_path} → {new_path}")

                self.logger.log_rename(old_path, new_path, status="Renamed" if not dry_run else "DryRun", source=info["match_source"], confidence=info.get("confidence_score", ""), level=info.get("confidence_level", ""))
            except Exception as e:
                self.logger.log_rename(old_path, "", status="Failed", source=str(e),confidence=info.get("confidence_score", ""), level=info.get("confidence_level", ""))
                print(f" Rename failed: {old_path} — {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run without renaming files")
    args = parser.parse_args()

    renamer = ImageRenamer()
    renamer.rename_images(dry_run=args.dry_run)
