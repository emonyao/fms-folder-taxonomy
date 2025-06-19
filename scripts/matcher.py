# scripts/matcher.py

import os
import csv
import pandas as pd
import re
import json
from datetime import datetime
from typing import List, Dict, Optional
from utils import extract_color_phrase

class ImageMatcher:
    def __init__(self, metadata_path: str = "data/metadata.json"):
        self.metadata_path = metadata_path
        # 20250616 update: csv -> json
        # self.meta_df = pd.read_csv(metadata_path)
        # self.image_columns = ["IMAGE 1", "IMAGE 2", "IMAGE 3", "IMAGE 4", "PROD VARIATION IMAGE"]
        # with open(metadata_path, "r", encoding="utf-8") as f:
        #     self.meta_list = json.load(f)  # List[Dict]
        with open(metadata_path, "r", encoding="utf-8-sig") as f:
            print(f"✅ Reading file: {metadata_path}")
            content = f.read()
            # print("🔍 Content starts with:", content[:50])  # debug output first 50 characters
            
            
            self.meta_list = json.loads(content)
            self.image_columns = ["product_name", "product_variation_name", "variation_image", "images"]  # 两种可能图字段：主图 + 多图列表

            # 20250618 add: change list to dict
            self.filename_to_meta = {}
            for item in self.meta_list:
                for col in self.image_columns:
                    images = item.get(col)
                    if isinstance(images, str):
                        # 20250619 change
                        # self.filename_to_meta[images.strip().lower()] = item
                        normalized_key = self.normalize_filename(images)
                        self.filename_to_meta[normalized_key] = item
                    elif isinstance(images, list):
                        for img in images:
                            # self.filename_to_meta[str(img).strip().lower()] = item
                            normalized_key = self.normalize_filename(img)
                            self.filename_to_meta[normalized_key] = item


        self.merchant_name_to_id = {}
        for item in self.meta_list:
            merchant = item.get("merchant", {})
            if isinstance(merchant, dict):
                name = merchant.get("name", "").strip()
                mid = merchant.get("id", "").strip()
                if name and mid:
                    self.merchant_name_to_id[name] = mid

        # 20250606 add 
        # self.brand_lookup = {} # brand -> merchant
        # self.brand_df = pd.read_csv("data/merchant_brand_list.csv")
        # df = pd.read_csv("data/merchant_brand_list.csv")
        # for _, row in df.iterrows():
        #     brand = row["BRAND"].strip().lower()
        #     merchant = row["MERCHANT"].strip()
        #     self.brand_lookup[brand] = merchant

        # 20250619 add brand -> merchant -> product, *-*
        self.brand_merchant_product_map = {}
        for item in self.meta_list:
            # brand = item.get("brand","").strip().lower()
            # merichant = item.get("merchant",{}).get("name","").strip()
            # product = item.get("variation_image","").strip().lower()
            raw_brand = item.get("brand", "")
            raw_merchant = item.get("merchant", {}).get("name", "")
            raw_product = item.get("product_name", "")

            brand = raw_brand.strip().lower() if isinstance(raw_brand, str) else ""
            merchant = raw_merchant.strip() if isinstance(raw_merchant, str) else ""
            product = raw_product.strip().lower() if isinstance(raw_product, str) else ""

            if brand and merchant and product:
                self.brand_merchant_product_map.setdefault(brand, []).append({
                    "merchant": merchant,
                    "product": product,
                    "row": item
                })

        # 20250605 add output slugified name for testing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
        base_dir = os.path.abspath(os.path.dirname(__file__))
        debug_dir = os.path.join(base_dir, "..", "tests")
        os.makedirs(debug_dir, exist_ok=True)
        self.debug_log_path = os.path.join(debug_dir, f"match_debug_log_{timestamp}.csv")

        # self.debug_log_path = "tests/match_debug_log.csv"
        # os.makedirs(os.path.dirname(self.debug_log_path),exist_ok=True)
        with open(self.debug_log_path, "w", encoding="utf-8",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Image Filename", "Slugified Image", "Slugified Metadata", "Matched", "Metadata Column"])

        # 在 __init__ 中添加
        # self.merchant_name_to_id = {}
        # if "MERCHANT" in self.meta_df.columns and "MERCHANT ID" in self.meta_df.columns:
        #     for _, row in self.meta_df.iterrows():
        #         name = row["MERCHANT"].strip()
        #         mid = row["MERCHANT ID"]
        #         if name and mid:
        #             self.merchant_name_to_id[name] = mid

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


    # 20250618 change list to dict
    # def find_row_by_filename(self, filename: str) -> Optional[Dict]:
    #     """
    #     Try to find a row where the filename appears in any IMAGE column.

    #     Returns:
    #         row (pd.Series) if match found, else None
    #     """
    #     # filename_clean = filename.strip().lower()
    #     filename_clean = self.normalize_filename(filename)

    #     matched = False

    #     print(f"\n🔍 Trying to match image: {filename_clean}")

    #     # 20250616 update
    #     # for col in self.image_columns:
    #     #     if col in self.meta_df.columns:
    #     #         col_series = self.meta_df[col].astype(str)

    #     #         for i, cell in enumerate(col_series):
    #     #             cell_clean = self.normalize_filename(cell)

    #     #             is_match = filename_clean == cell_clean
    #     #             matched = matched or is_match
    #     for item in self.meta_list:
    #         for col in self.image_columns:
    #             images = item.get(col)
    #             if not images:
    #                 continue
    #             # 兼容 "variation_image": str 和 "images": List[str]
    #             if isinstance(images, str):
    #                 images = [images]
    #             for img in images:
    #                 img_clean = self.normalize_filename(str(img))
    #                 is_match = filename_clean == img_clean
    #                 matched = matched or is_match


    #                 with open(self.debug_log_path, "a", encoding="utf-8",newline='') as f:
    #                     writer = csv.writer(f)
    #                     writer.writerow([
    #                         filename, filename_clean, img_clean,
    #                         "Yes" if is_match else "No", col
    #                     ])

    #                 print(f"Comparing image='{filename_clean}' vs metadata='{img_clean}'")
    #                 if is_match:
    #                     print(f"✅ Match found in column '{col}': {img}")
    #                     return item
    #     print("❌ No match found in metadata.")
    #     return None
    def find_row_by_filename(self, filename: str) -> Optional[Dict]:
        normalized = self.normalize_filename(filename)
        result = self.filename_to_meta.get(normalized)
        matched_row = None
        matched_slug = ""
        matched_column = ""

        # 20250619 add and change
        # for key, row in self.filename_to_meta.items():
        #     if normalized == key:
        #         # matched = True
        #         matched_slug = key
        #         break
        # 遍历 meta_list 而不是 filename_to_meta，这样才能记录字段来源
        for item in self.meta_list:
            for col in self.image_columns:
                values = item.get(col)
                if not values:
                    continue
                if isinstance(values, str):
                    values = [values]
                for val in values:
                    if self.normalize_filename(val) == normalized:
                        matched_row = item
                        matched_slug = self.normalize_filename(val)
                        matched_column = col
                        break
                if matched_row:
                    break
            if matched_row:
                break

        with open(self.debug_log_path, "a", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                filename,                 # 原始文件名
                normalized,              # 标准化后的文件名
                # "Matched" if result else "Unmatched",   # 如果匹配到了，用 ✓ 表示
                matched_slug or "Unmatched",    # Slugified Metadata
                "Yes" if result else "No",
                matched_column or "None"      # 匹配来源字段名
            ])

        if matched_row:
            print(f"✅ Fast match found for {filename}")
        else:
            print(f"❌ No fast match found for {filename}")
        return matched_row




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
            # 20250616 update
            # result["merchant"] = row.get("MERCHANT", "")
            # result["brand"] = row.get("BRAND", "")
            # result["product"] = row.get("PRODUCT NAME", "")
            # result["variation"] = row.get("PROD VARIATION NAME", "")
            # result["match_source"] = "Metadata"
            result["merchant"] = row.get("merchant", {}).get("name", "")
            result["brand"] = row.get("brand", "")
            # result["product"] = row.get("variation_image", "")
            # 20250619 change: get variation from the filename itself 
            # result["variation"] = row.get("product_variation_name", "")
            # 提取颜色或材质
            color_or_material = extract_color_phrase(filename)

            # 暂时不加编号，也不加 po/sb，这部分后续由 rename_images 控制更清晰
            # result["variation"] = color_or_material if color_or_material else ""
            # 先尝试从 filename 中提取颜色或材质（如 grey, black, khaki 等）
            color_or_material = extract_color_phrase(filename)

            # 初始化 variation 为空
            variation_parts = []

            # 加入颜色词（如果有）
            if color_or_material:
                variation_parts.append(color_or_material)

            # 加入编号（在 rename_images 中根据计数器动态生成，1 不显示，2 开始才显示）
            # 例如这里不加，留给后续 rename_images 方法处理

            # 加入分组信息（PO 或 SB），也留给 rename_images 添加 `_po`, `_sb`

            # 把拼接好的 variation_parts 合并为字符串
            result["variation"] = "_".join(variation_parts)
            # result["match_source"] = "Metadata"
            # 如果是 bundle 图，不使用 metadata 中的 product name，保留原始文件名
            if "bundle" in filename.lower():
                result["product"] = os.path.splitext(filename)[0]
                result["match_source"] = "BundleFilename"
            else:
                result["product"] = row.get("product_name", "")
                result["match_source"] = "Metadata"

        else:
            print(f"⚠️ No match found for {filename} in metadata")

            # 20250606 add
            filename_clean = filename.lower()
            base_name = os.path.splitext(filename)[0].lower()

            # 20250620: 如果包含 "bundle"，直接根据 brand 获取 merchant
            if "bundle" in filename_clean:
                for brand, entries in self.brand_merchant_product_map.items():
                    if brand in filename_clean:
                        result["brand"] = brand
                        result["merchant"] = entries[0]["merchant"]  # 取第一个 merchant，默认用第一个
                        result["product"] = base_name
                        result["match_source"] = "BundleByBrand"
                        print(f"Bundle match: brand={result['brand']} -> merchant={result['merchant']}")
                        break

            else:
                best_match_row = None
                best_score = 0

            # 20250616 delete
            # for _, row in self.brand_df.iterrows():
            #     brand = row["BRAND"].strip().lower()
            #     merchant = row["MERCHANT"].strip()
            #     product = row.get("PRODUCT NAME","").strip().lower()

            #     if brand in filename_clean:
            #         score = 0
            #         base_words = base_name.split()
            #         product_words = product.split()
            #         for i in range(min(len(base_words), len(product_words))):
            #             if base_words[i] == product_words[i]:
            #                 score += 1
            #             else:
            #                 break
                    
            #         if score > best_score:
            #             best_score = score
            #             best_match_row = row
            
            # 20250619 add get merchant from merchant -> brand -> product
                for brand, entries in self.brand_merchant_product_map.items():
                    if brand in filename_clean:
                        for entry in entries:
                            product_name = entry["product"]
                            product_words = product_name.lower().split()
                            filename_words = base_name.split()

                            # fuzzy match by leading word overlap
                            score = 0
                            for i in range(min(len(product_words), len(filename_words))):
                                if product_words[i] == filename_words[i]:
                                    score += 1
                                else:
                                    break
                            if score > best_score:
                                best_score = score
                                best_match_row = entry

            # 20250619 update
                if best_match_row is not None:
                    row = best_match_row["row"]
                    result["brand"] = best_match_row["row"]["brand"]
                    result["merchant"] = best_match_row["merchant"]
                    # result["product"] = best_match_row.get("PRODUCT NAME","")
                    result["product"] = base_name
                    result["match_source"] = "BrandFallback+Product"

                    print(f"✅ Best fallback match: brand={result['brand']}, product={result['product']}, merchant={result['merchant']}")
                else:
                    print("❌ No suitable fallback row found.")

            # for brand in self.brand_lookup:
            #     pattern = rf'\b{re.escape(brand)}\b'
            #     if re.search(pattern, filename_clean):

            #     # if brand in filename_clean:
            #         result["brand"] = brand
            #         result["merchant"] = self.brand_lookup[brand]
            #         result["product"] = os.path.splitext(filename)[0]
            #         result["match_source"] = "BrandFallback"
            #         print(f"✅ Brand fallback match: {brand} -> {self.brand_lookup[brand]}")
            #         break
        
        # 20250606 add: preserve color information
        if not result["variation"]:
            result["variation"] = extract_color_phrase(filename) or ""

        # ✅ 替换 merchant name 为 merchant ID（仅限找到对应 ID 的情况）
        original_merchant = result["merchant"]
        if original_merchant in self.merchant_name_to_id:
            result["merchant"] = self.merchant_name_to_id[original_merchant]
            print(f"🔄 Replaced merchant name '{original_merchant}' with ID '{result['merchant']}'")
        else:
            print(f"⚠️ No MERCHANT ID found for '{original_merchant}', keeping original name.")

        print(f"DEBUG: Matching {filename}...")
        return result


    def batch_match(self, image_paths: List[str]) -> List[Dict]:
        """
        Match a list of image paths to metadata.

        Returns:
            List[Dict]
        """
        return [self.match_image(path) for path in image_paths]
