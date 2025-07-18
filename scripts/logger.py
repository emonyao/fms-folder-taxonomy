# scripts/logger.py

import os
import csv
from datetime import datetime
from typing import List, Tuple


class RenameLogger:
    def __init__(self, config=None):
        from datetime import datetime
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        if config is None:
            # fallback 路径
            log_dir = "output"
            main_log = os.path.join(log_dir, "rename_log.csv")
            backup_log = os.path.join(log_dir, f"rename_log_{self.timestamp}.csv")
        else:
            log_dir = os.path.dirname(config.get("log_file", "output/rename_log.csv"))
            main_log = config.get("log_file", "output/rename_log.csv")
            backup_log = os.path.join(log_dir, f"rename_log_{self.timestamp}.csv")
        self.main_log_path = main_log
        self.backup_log_path = backup_log
        self.header_written = {
            "main": os.path.exists(self.main_log_path) and os.stat(self.main_log_path).st_size > 0,
            "backup": False
        }

    def write_image_list(self, image_paths: List[Tuple[str, str, str, str]], output_path: str = "Z:\Baby Fairs 2025\output\image_list.csv") -> None:
        """
        Write a list of image paths to a CSV file with filename extraction.

        Parameters:
            image_paths (List[Tuple]): List of tuples (full_path, structure, clean_path, merchant)
            output_path (str): Path to save CSV
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Index", "Original Path", "Original Filename", "Structure", "Clean Path", "Merchant"])
            for idx, (full_path, structure, clean_path, merchant) in enumerate(image_paths, 1):
                filename = os.path.basename(full_path)
                writer.writerow([idx, full_path, filename, structure, clean_path, merchant])

    def log_rename(self, old_path: str, new_path: str, status: str = "Renamed", source: str = "Metadata",confidence=None,level=None) -> None:
        """
        Log a single rename operation to both the main log and the backup log.

        Parameters:
            old_path (str): Original file path before renaming
            new_path (str): New file path after renaming
            status (str): Status of the operation (e.g. 'Renamed', 'Skipped', 'Failed')
            source (str): Source of the rename logic (e.g. 'Metadata', 'AI', 'Manual')
        """
        filename = os.path.basename(old_path)
        new_filename = os.path.basename(new_path)
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [time_str, old_path, filename, new_filename, status, source, confidence, level]

        # Append to main log
        os.makedirs(os.path.dirname(self.main_log_path), exist_ok=True)
        with open(self.main_log_path, "a", newline='', encoding="utf-8") as f_main:
            writer = csv.writer(f_main)
            if not self.header_written["main"]:
                writer.writerow(["Time", "Original Path", "Original Filename",
                                  "New Filename", "Status", "Source", "Score", "Confidence Level"])
                self.header_written["main"] = True
            writer.writerow(row)

        # Write to backup log
        with open(self.backup_log_path, "a", newline='', encoding="utf-8") as f_backup:
            writer = csv.writer(f_backup)
            if not self.header_written["backup"]:
                writer.writerow(["Time", "Original Path", "Original Filename",
                                  "New Filename", "Status", "Source", "Score", "Confidence Level"])
                self.header_written["backup"] = True
            writer.writerow(row)