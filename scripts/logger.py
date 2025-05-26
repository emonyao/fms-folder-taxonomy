# scripts/logger.py

import os
import csv
from datetime import datetime

# === Image list output ===
def write_image_list_csv(image_paths, output_path="output/image_list.csv"):
    """
    Write a list of image paths to a CSV file with filename extraction.

    Parameters:
        image_paths (List[str]): List of full image paths
        output_path (str): Path to save CSV
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Index", "Original Path", "Original Filename", "New Path", "New Filename"])
        for idx, full_path in enumerate(image_paths, 1):
            filename = os.path.basename(full_path)
            writer.writerow([idx, full_path, filename, "", ""])


# === Rename logging ===

# Generate unique backup log filename with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
backup_log_path = f"output/rename_log_{timestamp}.csv"
main_log_path = "output/rename_log.csv"

# Header writing flags
header_written = {
    "main": os.path.exists(main_log_path) and os.stat(main_log_path).st_size > 0,
    "backup": False
}

def log_rename(old_path, new_path, status="Renamed", source="Metadata"):
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

    row = [time_str, old_path, filename, new_path, new_filename, status, source]

    # Append to main log
    with open(main_log_path, "a", newline='', encoding="utf-8") as f_main:
        writer = csv.writer(f_main)
        if not header_written["main"]:
            writer.writerow(["Time", "Original Path", "Original Filename", 
                             "New Path", "New Filename", "Status", "Source"])
            header_written["main"] = True
        writer.writerow(row)

    # Write to backup log
    with open(backup_log_path, "a", newline='', encoding="utf-8") as f_backup:
        writer = csv.writer(f_backup)
        if not header_written["backup"]:
            writer.writerow(["Time", "Original Path", "Original Filename", 
                             "New Path", "New Filename", "Status", "Source"])
            header_written["backup"] = True
        writer.writerow(row)
