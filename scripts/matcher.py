# scripts/matcher.py

import os
import pandas as pd

# Columns that may contain image filenames
IMAGE_COLUMNS = ["IMAGE 1", "IMAGE 2", "IMAGE 3", "IMAGE 4", "PROD VARIATION IMAGE"]

def load_metadata(metadata_path="data/image_metadata.csv"):
    """
    Load metadata CSV into a DataFrame.
    """
    return pd.read_csv(metadata_path)


def find_row_by_filename(filename, meta_df):
    """
    Try to find a row where the filename appears in any IMAGE column.

    Returns:
        row (pd.Series) if match found, else None
    """
    filename_clean = filename.strip().lower()
    print(f"\n🔍 Trying to match image: {filename_clean}")

    for col in IMAGE_COLUMNS:
        if col in meta_df.columns:
            
            col_series = meta_df[col].astype(str).str.strip().str.lower()
            # col_series = meta_df[col].astype(str)
            print(f"📌 Checking column: {col}")
            print("    Top 5 values in this column:")
            print(col_series.head(5).to_list())  # 打印前 5 行，调试用

            match = meta_df[meta_df[col] == filename]
            if not match.empty:
                print(f"✅ Match found in column: {col}")
                return match.iloc[0]
    print("❌ No match found in any column.\n")
    return None


def match_image(image_path, meta_df):
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

    row = find_row_by_filename(filename, meta_df)
    if row is not None:
        result["merchant"] = row.get("MERCHANT", "")
        result["brand"] = row.get("BRAND", "")
        result["product"] = row.get("PRODUCT NAME", "")
        result["variation"] = row.get("PROD VARIATION NAME", "")
        result["match_source"] = "Metadata"

    print(f"DEBUG: Matching {filename}...")

    # test
    row = find_row_by_filename(filename, meta_df)
    if row is not None:
        ...
    else:
        print(f"⚠️ No match found for {filename}")

    return result


def batch_match(image_paths, meta_df):
    """
    Match a list of image paths to metadata.

    Returns:
        List[Dict]
    """
    return [match_image(path, meta_df) for path in image_paths]
