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

        self.logger = RenameLogger(self.config)
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

    import difflib

    def dedup_similar_substrings(self, name: str) -> str:
        from difflib import SequenceMatcher

        def normalize(s):
            return s.replace(" ", "").replace("_", "").replace("-", "").lower()

        parts = name.split('_')
        result = []
        seen = []

        for p in parts:
            key = normalize(p)
            if not key:
                continue

            is_similar = False
            for s in seen:
                ratio = SequenceMatcher(None, key, s).ratio()
                if ratio > 0.8:  # If similarity is above 80%, consider as duplicate
                    is_similar = True
                    break

            if not is_similar:
                seen.append(key)
                result.append(p)

        return '_'.join(result)


    def construct_filename(self, info_dict: Dict, version: int = 1) -> str:
        merchant = self.clean_text_keep_space(info_dict.get("merchant", "unknown"))
        brand = self.clean_text_keep_space(info_dict.get("brand", "unknown"))
        product = self.clean_text_keep_space(info_dict.get("product", "unknown"))
        variation = self.clean_text_keep_space(info_dict.get("variation", ""))
        original_filename = info_dict.get("filename", "")

        # Remove merchant, only use brand, product, variation
        parts = []
        if brand and brand != merchant:
            parts.append(brand)
        if product:
            parts.append(product)
        if variation:
            parts.append(variation)

        # Check if all parts are digits
        parts_str = "_".join(parts)
        if parts and parts_str.replace('_', '').isdigit():
            # Only contains digits, return original filename (without merchant)
            ext = os.path.splitext(original_filename)[1] or ".jpg"
            base = os.path.splitext(original_filename)[0]
            return f"{base}{ext}"

        base_name = "_".join(filter(None, parts))
        # Finally, remove duplicate substrings with equivalent content
        base_name = self.dedup_similar_substrings(base_name)
        
        if version > 1:
            # Only append number when variation already has content
            if variation:
                base_name += f"_{version}"
            else:
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
            print("[RENAME DEBUG]", info)
            self.debug_log(f"[RENAME DEBUG]: {info}")

            old_path = info["original_path"]
            original_dir = os.path.dirname(old_path)
            parent_folder = os.path.basename(original_dir).upper()

            group_key = parent_folder if parent_folder in ["PO", "SB"] else ""
            merchant = self.slugify(info.get("merchant", "unknown"))
            brand = self.slugify(info.get("brand", "unknown"))
            # Optimize product field handling logic
            if info["match_source"] == "FromProduct" and info.get("product_from_folder"):
                product = self.slugify(info["product_from_folder"])
            elif info.get("product"):
                product = self.slugify(info["product"])
            else:
                product = "unknown"
            variation = self.slugify(info.get("variation", ""))

            # Only when merchant, brand, product, variation (and variation is not empty) are all equal, count
            if variation:
                name_key = f"{merchant}_{brand}_{product}_{variation}"
            else:
                name_key = f"{merchant}_{brand}_{product}"
            counter_key = (name_key, group_key)

            count = variation_counters.get(counter_key, 0) + 1
            variation_counters[counter_key] = count

            # Only auto-generate when variation is empty
            if not info.get("variation"):
                variation_parts = []
                color_or_material = extract_color_phrase(info["filename"])
                product_text = info.get("product", "").lower()
                if color_or_material and color_or_material not in product_text:
                    variation_parts.append(color_or_material)
                if count > 1:
                    variation_parts.append(str(count))
                if group_key in ["PO", "SB"]:
                    variation_parts.append(group_key.lower())
                info["variation"] = "_".join(variation_parts)
            # Otherwise, keep the variation assigned by matcher, do not overwrite

            # Only when variation is not empty and there is a name conflict, append number after variation
            version = 1
            if variation and count > 1:
                info["variation"] = f"{variation}_{count}"
                version = 1  # No longer add _vN in construct_filename
            else:
                version = count if count > 1 else 1

            new_name = self.construct_filename(info, version=version)
            new_path = os.path.join(original_dir, new_name)

            print("[RENAME NEW NAME]", new_name)
            self.debug_log(f"[RENAME NEW NAME]: {new_name}")

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

    def debug_log(self, msg: str):
        with open("output/renamer_debug_log.txt", "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run without renaming files")
    args = parser.parse_args()

    renamer = ImageRenamer()
    renamer.rename_images(dry_run=args.dry_run)
