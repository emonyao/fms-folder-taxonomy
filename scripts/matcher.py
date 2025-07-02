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

        self.debug_file_path = "output/debug_log.txt"

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
        self.debug_log(f"✅ Fast match found for {filename}")
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

        # 20250701 新逻辑：只用路径和文件名，不查 metadata
        if clean_path:
            # 统一分隔符
            norm_path = clean_path.replace('/', os.sep).replace('\\', os.sep)
            parts = norm_path.split(os.sep)
            print(f"[DEBUG] 路径分割 parts: {parts}")
            self.debug_log(f"[DEBUG] 路径分割 parts: {parts}")
            # 找到 "marketing form (rcvd)" 的索引
            try:
                idx = [p.lower() for p in parts].index("marketing form (rcvd)")
                merchant = parts[idx + 1] if len(parts) > idx + 1 else "unknown"
                print(f"[DEBUG] 找到 merchant: {merchant} (parts[{idx + 1}])")
                self.debug_log(f"[DEBUG] 找到 merchant: {merchant} (parts[{idx + 1}])")
            except ValueError:
                merchant = "unknown"
                print(f"[DEBUG] 未找到 'marketing form (rcvd)'，merchant 设为 unknown")
                self.debug_log(f"[DEBUG] 未找到 'marketing form (rcvd)'，merchant 设为 unknown")
            
            if merchant != "unknown":
                # 提取 merchant 之后的路径部分
                after_merchant_parts = parts[parts.index(merchant) + 1:]  # +1 跳过 merchant
                # 跳过所有包含 'images'、'use this' 或 'pre order & starbuy' 的文件夹和纯数字文件夹
                after_merchant_parts = [p for p in after_merchant_parts if 'images' not in p.lower() and 'use this' not in p.lower() and 'pre order & starbuy' not in p.lower() and not p.isdigit()]
                # 去除实际重复但写法不同的文件夹名
                after_merchant_parts = self.dedup_similar_folders(after_merchant_parts)
                print(f"[DEBUG] merchant: {merchant}, after_merchant_parts: {after_merchant_parts}, filename: {filename}")
                self.debug_log(f"[DEBUG] merchant: {merchant}, after_merchant_parts: {after_merchant_parts}, filename: {filename}")
                if len(after_merchant_parts) == 1:
                    # merchant/image.jpg - 结构 A
                    structure = "A"
                    result["match_source"] = "FlatImage"
                    image_base = os.path.splitext(filename)[0]
                    result["product"] = image_base
                    print(f"[DEBUG] 结构A赋值: product={result['product']}")
                    self.debug_log(f"[DEBUG] 结构A赋值: product={result['product']}")
                elif len(after_merchant_parts) == 2:
                    # merchant/brand_or_product/image.jpg - 结构 B
                    folder_name = after_merchant_parts[0]
                    print(f"[DEBUG] 结构B folder_name: {folder_name}")
                    self.debug_log(f"[DEBUG] 结构B folder_name: {folder_name}")
                    
                    result["brand"] = folder_name
                    result["product"] = os.path.splitext(filename)[0]
                    result["match_source"] = "FromPathBrandImage"
                    print(f"[DEBUG] 结构B品牌: brand={result['brand']}, product={result['product']}")
                    self.debug_log(f"[DEBUG] 结构B品牌: brand={result['brand']}, product={result['product']}")

                    structure = "B"
                elif len(after_merchant_parts) == 3:
                    # merchant/brand/product/variation.jpg - 结构C
                    brand_folder = after_merchant_parts[0]
                    product_folder = after_merchant_parts[1]
                    variation_file = after_merchant_parts[2]
                    variation_name = os.path.splitext(variation_file)[0]
                    result["brand"] = brand_folder
                    result["product"] = product_folder
                    result["variation"] = variation_name
                    result["match_source"] = "FromPathBrandProductVariation"
                    print(f"[DEBUG] 结构C: brand={brand_folder}, product={product_folder}, variation={variation_name}")
                    self.debug_log(f"[DEBUG] 结构C: brand={brand_folder}, product={product_folder}, variation={variation_name}")
                elif len(after_merchant_parts) == 4:
                    # merchant/brand/product/variation_part1/variation_part2.jpg - 结构D
                    brand_folder = after_merchant_parts[0]
                    product_folder = after_merchant_parts[1]
                    variation_part1 = after_merchant_parts[2]
                    variation_part2 = os.path.splitext(after_merchant_parts[3])[0]
                    variation_name = f"{variation_part1}_{variation_part2}"
                    result["brand"] = brand_folder
                    result["product"] = product_folder
                    result["variation"] = variation_name
                    result["match_source"] = "FromPathBrandProductVariationParts"
                    print(f"[DEBUG] 结构D: brand={brand_folder}, product={product_folder}, variation={variation_name}")
                    self.debug_log(f"[DEBUG] 结构D: brand={brand_folder}, product={product_folder}, variation={variation_name}")
                else:
                    structure = "Unknown"
                    print(f"[DEBUG] 结构未知: after_merchant_parts={after_merchant_parts}")
                    self.debug_log(f"[DEBUG] 结构未知: after_merchant_parts={after_merchant_parts}")

        # 20250701 清理 merchant name 并尝试匹配 ID
        cleaned_merchant = clean_merchant_folder_name(merchant)
        print(f"[DEBUG] 清理后 merchant: {cleaned_merchant}")
        self.debug_log(f"[DEBUG] 清理后 merchant: {cleaned_merchant}")
        result["merchant"] = cleaned_merchant  # 先设置为清理后的名称
        
        # 替换 merchant name 为 ID - 简化的匹配逻辑
        matched_id = None
        matched_name = None
        best_match_score = 0
        
        for name, merchant_id in self.merchant_name_to_id.items():
            name_lower = name.lower()
            
            # 计算匹配分数
            match_score = 0
            
            # 1. 完全匹配（最高优先级）
            if cleaned_merchant.lower() == name_lower:
                match_score = 100
                print(f"[DEBUG] 完全匹配: '{cleaned_merchant}' == '{name}'")
                self.debug_log(f"[DEBUG] 完全匹配: '{cleaned_merchant}' == '{name}'")
            # 2. 包含匹配：filepath中的merchant包含metadata中的merchant
            elif name_lower in cleaned_merchant.lower():
                match_score = 80
                print(f"[DEBUG] 包含匹配: '{name}' 包含在 '{cleaned_merchant}' 中")
                self.debug_log(f"[DEBUG] 包含匹配: '{name}' 包含在 '{cleaned_merchant}' 中")
            # 3. 被包含匹配：metadata中的merchant包含filepath中的merchant
            elif cleaned_merchant.lower() in name_lower:
                match_score = 60
                print(f"[DEBUG] 被包含匹配: '{cleaned_merchant}' 包含在 '{name}' 中")
                self.debug_log(f"[DEBUG] 被包含匹配: '{cleaned_merchant}' 包含在 '{name}' 中")
            
            # 更新最佳匹配
            if match_score > best_match_score:
                best_match_score = match_score
                matched_id = merchant_id
                matched_name = name
                print(f"[DEBUG] 新最佳匹配: '{name}' (ID: {merchant_id}) 分数: {match_score}")
                self.debug_log(f"[DEBUG] 新最佳匹配: '{name}' (ID: {merchant_id}) 分数: {match_score}")
        
        if matched_id and best_match_score > 0:  # 只要有匹配就使用
            result["merchant"] = matched_id
            print(f"🔄 Matched merchant folder '{cleaned_merchant}' to '{matched_name}' (ID: '{matched_id}') with score {best_match_score}")
            self.debug_log(f"🔄 Matched merchant folder '{cleaned_merchant}' to '{matched_name}' (ID: '{matched_id}') with score {best_match_score}")
        else:
            print(f"⚠️ No MERCHANT ID found for '{cleaned_merchant}', keeping cleaned name.")
            self.debug_log(f"⚠️ No MERCHANT ID found for '{cleaned_merchant}', keeping cleaned name.")

        # 提取颜色或材质
        if not result["variation"]:
            variation = extract_color_phrase(filename)
            result["variation"] = variation or ""
            print(f"[DEBUG] variation 提取: {result['variation']}")
            self.debug_log(f"[DEBUG] variation 提取: {result['variation']}")

        # 置信度分级（结构分+字段分）
        # 结构分
        structure_score_map = {
            "FromPathBrandProductVariation": 2.0,
            "FromPathBrandProductVariationParts": 2.2,  # 结构D：更详细的variation信息
            "FromPathBrandImage": 1.5,
            "FromPathProduct": 1.2,
            "FlatImage": 1.0,
            "FolderMerchant": 0.5,
            "NotFound": 0
        }
        structure_score = structure_score_map.get(result["match_source"], 0)
        # 字段分
        field_score = 0
        if result.get("merchant"): field_score += 0.5
        if result.get("brand"): field_score += 0.8
        if result.get("product"): field_score += 1.0
        if result.get("variation"): field_score += 0.7
        score = round(structure_score + field_score, 2)
        result["confidence_score"] = score
        if score >= 3.0:
            result["confidence_level"] = "High"
        elif score >= 2.0:
            result["confidence_level"] = "Medium"
        elif score > 0:
            result["confidence_level"] = "Low"
        else:
            result["confidence_level"] = "None"

        print(f"[DEBUG] Final result: {result}")
        self.debug_log(f"[DEBUG] Final result: {result}")
        print(f"DEBUG: Matching {filename}...")
        self.debug_log(f"DEBUG: Matching {filename}...")

        print("[RENAME DEBUG]", result)

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

    def is_brand_folder(self, folder_name: str) -> bool:
        """
        判断文件夹名是否为品牌名
        """
        # 特殊情况：数字文件夹直接认为是产品编号
        if folder_name.isdigit():
            return False
            
        folder_normalized = folder_name.lower().strip()
        
        for item in self.meta_list:
            brand = item.get("brand")
            # 检查 brand 是否存在且不为 None
            if brand and isinstance(brand, str):
                brand_normalized = brand.lower().strip()
                if (folder_normalized == brand_normalized or 
                    brand_normalized in folder_normalized or 
                    folder_normalized in brand_normalized):
                    return True
        return False

    def dedup_similar_folders(self, parts):
        seen = set()
        result = []
        for p in parts:
            key = p.replace(" ", "").lower()
            if key not in seen:
                seen.add(key)
                result.append(p)
        return result

    def debug_log(self, msg: str):
        with open(self.debug_file_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
