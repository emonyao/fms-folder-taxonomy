# scripts/matcher.py

import os
import csv
import pandas as pd
import re
from typing import List, Dict, Optional

class ImageMatcher:
    def __init__(self, metadata_path: str = "data/image_metadata.csv"):
        self.metadata_path = metadata_path
        self.meta_df = pd.read_csv(metadata_path)
        self.image_columns = ["IMAGE 1", "IMAGE 2", "IMAGE 3", "IMAGE 4", "PROD VARIATION IMAGE"]

        # 20250605 add output slugified name for testing
        self.debug_log_path = "tests/match_debug_log.csv"
        os.makedirs(os.path.dirname(self.debug_log_path),exist_ok=True)
        with open(self.debug_log_path, "w", encoding="utf-8",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Image Filename", "Slugified Image", "Slugified Metadata", "Matched", "Metadata Column"])


# Columns that may contain image filenames
# IMAGE_COLUMNS = ["IMAGE 1", "IMAGE 2", "IMAGE 3", "IMAGE 4", "PROD VARIATION IMAGE"]

# def load_metadata(metadata_path="data/image_metadata.csv"):
#     """
#     Load metadata CSV into a DataFrame.
#     """
#     return pd.read_csv(metadata_path)

    def normalize_filename(self, name: str) -> str:
        """
        Normalize filenames for comparison:
        - lowercase
        - remove special chars (_ - () whitespace)
        - remove common suffixes (_PO, _SB, etc.)
        - strip file extensions
        """
        name = name.lower()
        name = re.sub(r'[\s_\-()]+', '', name)      # remove spaces, _, -, ()
        name = re.sub(r'_po|_sb+', '', name)       # remove suffixes like _PO or _SB
        name = os.path.splitext(name)[0]            # remove file extension
        return name


    def find_row_by_filename(self, filename: str) -> Optional[pd.Series]:
        """
        Try to find a row where the filename appears in any IMAGE column.

        Returns:
            row (pd.Series) if match found, else None
        """
        # filename_clean = filename.strip().lower()
        filename_clean = self.normalize_filename(filename)

        matched = False

        print(f"\n🔍 Trying to match image: {filename_clean}")

        for col in self.image_columns:
            if col in self.meta_df.columns:
                col_series = self.meta_df[col].astype(str)

                for i, cell in enumerate(col_series):
                    cell_clean = self.normalize_filename(cell)

                    is_match = filename_clean == cell_clean
                    matched = matched or is_match

                    with open(self.debug_log_path, "a", encoding="utf-8",newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            filename, filename_clean, cell_clean,
                            "Yes" if is_match else "No", col
                        ])

                    print(f"Comparing image='{filename_clean}' vs metadata='{cell_clean}'")
                    if is_match:
                        print(f"✅ Match found in column '{col}': {cell}")
                        return self.meta_df.iloc[i]
        print("❌ No match found in any column.")
        return None


    def match_image(self, image_path: str) -> Dict[str, str]:
        """
        Match an image to metadata and extract naming info.

        Returns:
            Dict[str, str]
        """
        filename = os.path.basename(image_path)
        result = {
            "original_path": image_path,
            "filename": filename,
            "merchant": "",
            "brand": "",
            "product": "",
            "variation": "",
            "match_source": "NotFound"
        }

        row = self.find_row_by_filename(filename)
        if row is not None:
            result["merchant"] = row.get("MERCHANT", "")
            result["brand"] = row.get("BRAND", "")
            result["product"] = row.get("PRODUCT NAME", "")
            result["variation"] = row.get("PROD VARIATION NAME", "")
            result["match_source"] = "Metadata"
        else:
            print(f"⚠️ No match found for {filename}")

        print(f"DEBUG: Matching {filename}...")
        return result


    def batch_match(self, image_paths: List[str]) -> List[Dict]:
        """
        Match a list of image paths to metadata.

        Returns:
            List[Dict]
        """
        return [self.match_image(path) for path in image_paths]
