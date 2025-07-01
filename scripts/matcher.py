# scripts/matcher.py

import os
import csv
import pandas as pd
import re
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from utils import extract_color_phrase

def clean_merchant_folder_name(folder_name: str) -> str:
    """
    清洗 merchant 文件夹名：
    - 去掉开头的下划线及之前的所有字符
    - 去掉第一个 '-' 及之后的内容
    """
    folder_name = folder_name.strip()
    folder_name = re.sub(r'^[^a-zA-Z]*_', '', folder_name)  # 删除前缀数字与下划线
    folder_name = folder_name.split('-', 1)[0]              # 去掉 '-' 后的内容
    return folder_name.strip()

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

        # 20250619 add brand -> merchant -> product, *-*
        self.brand_merchant_product_map = {}
        for item in self.meta_list:
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

        # 20250630 add
        self.brand_keywords = {brand: set(brand.lower().split()) for brand in self.brand_merchant_product_map}


        # 20250605 add output slugified name for testing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
        base_dir = os.path.abspath(os.path.dirname(__file__))
        debug_dir = os.path.join(base_dir, "..", "tests")
        os.makedirs(debug_dir, exist_ok=True)
        self.debug_log_path = os.path.join(debug_dir, f"match_debug_log_{timestamp}.csv")


        with open(self.debug_log_path, "w", encoding="utf-8",newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Image Filename", "Slugified Image", "Slugified Metadata", "Matched", "Metadata Column"])


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

    def find_row_by_filename(self, filename: str) -> Optional[Dict]:
        normalized = self.normalize_filename(filename)
        result = self.filename_to_meta.get(normalized)
        matched_row = None
        matched_slug = ""
        matched_column = ""


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



    #20250630 update 
    def match_image(self, image_path: str, structure: str, filename_keywords: List[str], clean_path: str = "", extracted_merchant: str = "") -> Dict[str, str]:
        # 使用从 scanner 提取的 merchant，而不是从图片的上一级文件夹
        merchant = extracted_merchant if extracted_merchant else "unknown"
        
        filename = os.path.basename(image_path)
        base_name = os.path.splitext(filename)[0].lower()
        
        result = {
            "original_path": image_path,
            "filename": filename,
            "merchant": merchant,
            "brand": "",
            "product": "",
            "variation": "",
            "match_source": "FolderMerchant"
        }

        # 根据 clean_path 进一步判断结构类型
        if clean_path:
            # 相对于 Marketing Form (Rcvd) 的路径
            rel_parts = clean_path.split(os.sep)
            # 找到 Marketing Form (Rcvd) 的位置
            marketing_index = -1
            for i, part in enumerate(rel_parts):
                if part.lower() == "marketing form (rcvd)":
                    marketing_index = i
                    break
            
            if marketing_index >= 0:
                # 提取 merchant 之后的路径部分
                after_merchant_parts = rel_parts[marketing_index + 2:]  # +2 跳过 Marketing Form (Rcvd) 和 merchant
                
                if len(after_merchant_parts) == 1:
                    # merchant/image.jpg - 结构 A
                    structure = "A"
                    result["match_source"] = "FlatImage"
                elif len(after_merchant_parts) == 2:
                    # merchant/brand_or_product/image.jpg - 结构 B
                    folder_name = after_merchant_parts[0]
                    result["product_from_folder"] = folder_name
                    result["match_source"] = "FromProduct"
                    structure = "B"
                else:
                    structure = "Unknown"

        # 20250701 新逻辑：只用路径和文件名，不查 metadata
        if structure in ["A", "B"]:
            # merchant/image.jpg 或 merchant/brand/image.jpg
            # 用 merchant + image name（去掉扩展名）命名
            image_base = os.path.splitext(filename)[0]
            result["product"] = image_base
            result["match_source"] = "FromPathImageName"
        elif structure == "C":
            # merchant/product/1.jpg
            # 用 merchant + product 文件夹名命名
            if clean_path:
                rel_parts = clean_path.split(os.sep)
                marketing_index = -1
                for i, part in enumerate(rel_parts):
                    if part.lower() == "marketing form (rcvd)":
                        marketing_index = i
                        break
                if marketing_index >= 0:
                    merchant = rel_parts[marketing_index + 1] if len(rel_parts) > marketing_index + 1 else "unknown"
                    product = rel_parts[marketing_index + 2] if len(rel_parts) > marketing_index + 2 else "unknown"
                    result["merchant"] = merchant
                    result["product"] = product
                    result["match_source"] = "FromPathMerchantProduct"

        # 提取颜色或材质
        if not result["variation"]:
            variation = extract_color_phrase(filename)
            result["variation"] = variation or ""

        # 替换 merchant name 为 ID
        matched_id = None
        for name, merchant_id in self.merchant_name_to_id.items():
            if merchant.lower() in name.lower():
                matched_id = merchant_id
                break
        if matched_id:
            result["merchant"] = matched_id
            print(f"🔄 Matched merchant folder '{merchant}' to ID '{matched_id}'")
        else:
            print(f"⚠️ No MERCHANT ID found for '{merchant}', keeping original name.")

        # 置信度分级
        score_map = {
            "Metadata": 3,
            "BrandFromFilename": 2.5,
            "ProductFromFilename": 2,
            "BrandFallback+Product": 2,
            "BundleFilename": 2,
            "BundleByBrand": 1.5,
            "NotFound": 1
        }
        result["confidence_score"] = score_map.get(result["match_source"], 0)
        if result["confidence_score"] >= 2.5:
            result["confidence_level"] = "High"
        elif result["confidence_score"] >= 1.5:
            result["confidence_level"] = "Medium"
        else:
            result["confidence_level"] = "Low"

        print(f"DEBUG: Matching {filename}...")

        return result



    def batch_match(self, image_path_tuples: List[Tuple[str, str, str, str]]) -> List[Dict[str, str]]:
        """
        Match a list of image paths to metadata.
        
        Args:
            image_path_tuples: List of tuples (full_path, structure, clean_path, merchant)

        Returns:
            List[Dict]
        """
        results = []
        for path, structure, clean_path, merchant in image_path_tuples:
            filename = os.path.basename(path)
            base_name = os.path.splitext(filename)[0].lower()
            filename_keywords = base_name.split()

            result = self.match_image(path, structure, filename_keywords, clean_path, merchant)
            results.append(result)
        return results

    def get_structure_type(self, image_path: str) -> str:
        parts = image_path.lower().split(os.sep)
        if parts[-3] == "images":  # 结构 B
            return "B"
        elif parts[-2] == "images":  # 结构 A
            return "A"
        else:  # 假设不是 A 就是 C（品牌图）
            return "C"
