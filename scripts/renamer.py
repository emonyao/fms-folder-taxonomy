# scripts/renamer.py

import os
import shutil
from config import load_config
from logger import log_rename
from matcher import load_metadata, batch_match
from scanner import scan_image_paths

def slugify(text):
    """
    Convert text to lowercase and replace spaces/symbols with underscore.
    """
    return text.strip().lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def construct_filename(info_dict, version=1):
    """
    Construct standardized filename from metadata info.
    """
    merchant = slugify(info_dict.get("merchant", "unknown"))
    brand = slugify(info_dict.get("brand", "unknown"))
    product = slugify(info_dict.get("product", "unknown"))
    variation = slugify(info_dict.get("variation", "unknown"))

    base_name = f"{merchant}_{brand}_{product}_{variation}"
    if version > 1:
        base_name += f"_v{version}"
    return base_name + ".jpg"


def resolve_conflict(output_dir, filename):
    """
    Check if file exists in output_dir. If so, increment version.
    """
    name, ext = os.path.splitext(filename)
    version = 1
    candidate = filename
    while os.path.exists(os.path.join(output_dir, candidate)):
        version += 1
        candidate = f"{name}_v{version}{ext}"
    return candidate


def rename_images(dry_run=False):
    config = load_config("config.yaml")
    image_dir = config["input_folder"]
    output_dir = config["output_renamed"]
    os.makedirs(output_dir, exist_ok=True)

    # 1. Scan all image paths
    image_paths = scan_image_paths(image_dir)

    # 2. Load metadata
    meta_df = load_metadata()

    # 3. Match metadata
    matched_info = batch_match(image_paths, meta_df)

    # 4. Rename or copy files
    for info in matched_info:
        old_path = info["original_path"]

        new_name = construct_filename(info)
        # new_name = resolve_conflict(output_dir, new_name)
        # new_path = os.path.join(output_dir, new_name)
        original_dir = os.path.dirname(old_path)
        new_name = resolve_conflict(original_dir, new_name)
        new_path = os.path.join(original_dir, new_name)

        try:
            # # shutil.copy2(old_path, new_path)  # Use copy to preserve original
            # # log_rename(old_path, new_path, status="Renamed", source=info["match_source"])
            # os.rename(old_path, new_path)  # Direct rename in-place
            # log_rename(old_path, new_path, status="Renamed", source=info["match_source"])
            if dry_run:
                print(f"[DRY RUN] Would rename: {old_path} → {new_path}")
            else:
                os.rename(old_path, new_path)
                print(f" Renamed: {old_path} → {new_path}")

            log_rename(old_path, new_path, status="Renamed" if not dry_run else "DryRun", source=info["match_source"])

        except Exception as e:
            log_rename(old_path, "", status="Failed", source=str(e))
            print(f" Rename failed: {old_path} — {e}")
            
            print(f"{old_path} → {new_path}")
        


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run without renaming files")
    args = parser.parse_args()

    rename_images(dry_run=args.dry_run)
