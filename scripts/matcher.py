
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
    Clean merchant folder name:
    - Remove all characters before and including the first underscore at the start
    - Remove the first '-' and everything after it
    """
    folder_name = folder_name.strip()
    folder_name = re.sub(r'^[^a-zA-Z]*_', '', folder_name)  # Remove prefix numbers and underscore
    folder_name = folder_name.split('-', 1)[0]              # Remove content after '-'
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
            self.image_columns = ["product_name", "product_variation_name", "variation_image", "images"]  # Two possible image fields: main image + multiple image list

            
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
                filename,                 # Original filename
                normalized,              # Normalized filename
                # "Matched" if result else "Unmatched",   # If matched, use ✓
                matched_slug or "Unmatched",    # Slugified Metadata
                "Yes" if result else "No",
                matched_column or "None"      # Matched source column name
            ])

        if matched_row:
            print(f"✅ Fast match found for {filename}")
        else:
            print(f"❌ No fast match found for {filename}")
        self.debug_log(f"✅ Fast match found for {filename}")
        return matched_row



    #20250630 update 
    def match_image(self, image_path: str, structure: str, filename_keywords: List[str], clean_path: str = "", extracted_merchant: str = "") -> Dict[str, str]:
        # Use merchant extracted from scanner, not from the parent folder of the image
        self.debug_log(f"3. match_image -  image_path {image_path}")
        self.debug_log(f"3. match_image -  structure {structure}")
        self.debug_log(f"3. match_image -  filename_keywords {filename_keywords}")
        self.debug_log(f"3. match_image -  clean_path {clean_path}")
        self.debug_log(f"3. match_image -  extracted_merchant {extracted_merchant}")

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

        # 20250701 New logic: only use path and filename, do not check metadata
        if clean_path:
            # Normalize separators
            norm_path = clean_path.replace('/', os.sep).replace('\\', os.sep)
            parts = norm_path.split(os.sep)
            print(f"[DEBUG] Path split parts: {parts}")
            self.debug_log(f"[DEBUG] Path split parts: {parts}")

            # 20250709 delete
            # Find the index of "marketing form (rcvd)"
            # try:
            #     idx = [p.lower() for p in parts].index("marketing form (rcvd)")
            #     merchant = parts[idx + 1] if len(parts) > idx + 1 else "unknown"
            #     print(f"[DEBUG] Found merchant: {merchant} (parts[{idx + 1}])")
            #     self.debug_log(f"[DEBUG] Found merchant: {merchant} (parts[{idx + 1}])")
            # except ValueError:
            #     merchant = "unknown"
            #     print(f"[DEBUG] 'marketing form (rcvd)' not found, merchant set to unknown")
            #     self.debug_log(f"[DEBUG] 'marketing form (rcvd)' not found, merchant set to unknown")
            
            if merchant != "unknown":
                # Extract the part of the path after merchant
                after_merchant_parts = parts[parts.index(merchant) + 1:]  # +1 to skip merchant
                # Skip all folders containing 'images', 'use this', or 'pre order & starbuy', and folders with only digits
                mons = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                # after_merchant_parts = [p for i, p in enumerate(after_merchant_parts)
                # if (
                #     i != len(after_merchant_parts)-1
                #     and p.strip()
                #     and p.lower() not in 'images' 
                #     and p.lower() not in 'image' 
                #     and 'use this' not in p.lower() 
                #     and 'marketing' not in p.lower() 
                #     and 'mktg' not in p.lower()
                #     and 'pre order' not in p.lower() 
                #     and 'starbuy' not in p.lower() 
                #     and 'starbuys' not in p.lower()
                #     and 'deals' not in p.lower()
                #     and p.lower() not in mons 
                #     and not p.isdigit()
                #     and not re.match(r'^\$\d+', p)               # 忽略以 $ 开头 + 数字 的字段
                #     and not re.match(r'^\d+\s*[x×]\s*\d+$', p)    # 忽略 100x200 / 100×200 的字段
                #     ) or i == len(after_merchant_parts)-1
                # ]
                after_merchant_parts = [
                    p for i, p in enumerate(after_merchant_parts)
                    if (
                        i == len(after_merchant_parts) - 1  # Keep the last filename
                        or (
                            p.strip()
                            and not any(keyword in p.lower() for keyword in [
                                'images', 'image', 'use this', 'marketing', 'mktg',
                                'pre order', 'starbuy', 'starbuys', 'deals', 'pictures',
                                'picture', 'for ops only'
                            ])
                            and not any(mon in p.lower() for mon in ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                                                                    'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])
                            and not p.isdigit()
                            and not any(re.match(pattern, p) for pattern in [
                                r'^\$\d+',              # Starts with $
                                r'^\d+\s*[x×]\s*\d+$'   # Format like 100x200
                            ])
                        )
                    )
                ]


                # 20250709 add
                # Process each part
                after_merchant_parts = [self.clean_part(p) for p in after_merchant_parts]

                # Remove actually duplicate but differently written folder names
                after_merchant_parts = self.dedup_similar_folders(after_merchant_parts)
                print(f"[DEBUG] merchant: {merchant}, after_merchant_parts: {after_merchant_parts}, filename: {filename}")
                self.debug_log(f"[DEBUG] merchant: {merchant}, after_merchant_parts: {after_merchant_parts}, filename: {filename}")
                if len(after_merchant_parts) == 1:
                    # merchant/image.jpg - Structure A
                    structure = "A"
                    result["match_source"] = "FlatImage"
                    image_base = os.path.splitext(filename)[0]
                    result["product"] = self.clean_part(image_base)
                    print(f"[DEBUG] Structure A assign: product={result['product']}")
                    self.debug_log(f"[DEBUG] Structure A assign: product={result['product']}")
                elif len(after_merchant_parts) == 2:
                    # merchant/brand_or_product/image.jpg - Structure B
                    folder_name = after_merchant_parts[0]
                    print(f"[DEBUG] Structure B folder_name: {folder_name}")
                    self.debug_log(f"[DEBUG] Structure B folder_name: {folder_name}")
                    
                    result["brand"] = self.clean_part(folder_name)
                    raw_product = os.path.splitext(filename)[0]
                    result["product"] = self.clean_part(raw_product)
                    result["match_source"] = "FromPathBrandImage"
                    print(f"[DEBUG] Structure B brand: brand={result['brand']}, product={result['product']}")
                    self.debug_log(f"[DEBUG] Structure B brand: brand={result['brand']}, product={result['product']}")

                    structure = "B"
                elif len(after_merchant_parts) == 3:
                    # merchant/brand/product/variation.jpg - Structure C
                    brand_folder = after_merchant_parts[0]
                    product_folder = after_merchant_parts[1]
                    variation_file = after_merchant_parts[2]
                    variation_name = os.path.splitext(variation_file)[0]
                    result["brand"] = self.clean_part(brand_folder)
                    result["product"] = self.clean_part(product_folder)
                    result["variation"] = self.clean_part(variation_name)
                    result["match_source"] = "FromPathBrandProductVariation"
                    print(f"[DEBUG] Structure C: brand={brand_folder}, product={product_folder}, variation={variation_name}")
                    self.debug_log(f"[DEBUG] Structure C: brand={brand_folder}, product={product_folder}, variation={variation_name}")
                elif len(after_merchant_parts) == 4:
                    # merchant/brand/product/variation_part1/variation_part2.jpg - Structure D
                    brand_folder = after_merchant_parts[0]
                    product_folder = after_merchant_parts[1]
                    variation_part1 = after_merchant_parts[2]
                    variation_part2 = os.path.splitext(after_merchant_parts[3])[0]
                    variation_name = f"{variation_part1}_{variation_part2}"
                    result["brand"] = self.clean_part(brand_folder)
                    result["product"] = self.clean_part(product_folder)
                    result["variation"] = self.clean_part(variation_name)
                    result["match_source"] = "FromPathBrandProductVariationParts"
                    print(f"[DEBUG] Structure D: brand={brand_folder}, product={product_folder}, variation={variation_name}")
                    self.debug_log(f"[DEBUG] Structure D: brand={brand_folder}, product={product_folder}, variation={variation_name}")
                else:
                    # 20250709 update
                    # structure = "Unknown"
                    # print(f"[DEBUG] Unknown structure: after_merchant_parts={after_merchant_parts}")
                    # self.debug_log(f"[DEBUG] Unknown structure: after_merchant_parts={after_merchant_parts}")
                    brand = after_merchant_parts[0]
                    result["brand"] = self.clean_part(brand)
                    raw_product = os.path.splitext(filename)[0]
                    result["product"] = self.clean_part(raw_product)
                    result["match_source"] = "FromDeepBrandStructure"
                    structure = "Special"
                    print(f"[DEBUG] Special structure: brand={brand}, product={result['product']}, full after_merchant_parts={after_merchant_parts}")
                    self.debug_log(f"[DEBUG] Special structure: brand={brand}, product={result['product']}, full after_merchant_parts={after_merchant_parts}")


        # 20250701 Clean merchant name and try to match ID
        cleaned_merchant = clean_merchant_folder_name(merchant)
        print(f"[DEBUG] Cleaned merchant: {cleaned_merchant}")
        self.debug_log(f"[DEBUG] Cleaned merchant: {cleaned_merchant}")
        result["merchant"] = cleaned_merchant  # Set to cleaned name first
        
        # Replace merchant name with ID - simplified matching logic
        matched_id = None
        matched_name = None
        best_match_score = 0
        
        for name, merchant_id in self.merchant_name_to_id.items():
            name_lower = name.lower()
            
            # Calculate match score
            match_score = 0
            
            # 1. Exact match (highest priority)
            if cleaned_merchant.lower() == name_lower:
                match_score = 100
                print(f"[DEBUG] Exact match: '{cleaned_merchant}' == '{name}'")
                self.debug_log(f"[DEBUG] Exact match: '{cleaned_merchant}' == '{name}'")
            # 2. Contains match: merchant in filepath contains merchant in metadata
            elif name_lower in cleaned_merchant.lower():
                match_score = 80
                print(f"[DEBUG] Contains match: '{name}' is in '{cleaned_merchant}'")
                self.debug_log(f"[DEBUG] Contains match: '{name}' is in '{cleaned_merchant}'")
            # 3. Contained by match: merchant in metadata contains merchant in filepath
            elif cleaned_merchant.lower() in name_lower:
                match_score = 60
                print(f"[DEBUG] Contained by match: '{cleaned_merchant}' is in '{name}'")
                self.debug_log(f"[DEBUG] Contained by match: '{cleaned_merchant}' is in '{name}'")
            
            # Update best match
            if match_score > best_match_score:
                best_match_score = match_score
                matched_id = merchant_id
                matched_name = name
                print(f"[DEBUG] New best match: '{name}' (ID: {merchant_id}) Score: {match_score}")
                self.debug_log(f"[DEBUG] New best match: '{name}' (ID: {merchant_id}) Score: {match_score}")
        
        if matched_id and best_match_score > 0:  # Use if any match
            result["merchant"] = matched_id
            print(f"🔄 Matched merchant folder '{cleaned_merchant}' to '{matched_name}' (ID: '{matched_id}') with score {best_match_score}")
            self.debug_log(f"🔄 Matched merchant folder '{cleaned_merchant}' to '{matched_name}' (ID: '{matched_id}') with score {best_match_score}")
        else:
            print(f"⚠️ No MERCHANT ID found for '{cleaned_merchant}', keeping cleaned name.")
            self.debug_log(f"⚠️ No MERCHANT ID found for '{cleaned_merchant}', keeping cleaned name.")

        # Extract color or material
        if not result["variation"]:
            variation = extract_color_phrase(filename)
            result["variation"] = variation or ""
            print(f"[DEBUG] variation extracted: {result['variation']}")
            self.debug_log(f"[DEBUG] variation extracted: {result['variation']}")

        # Confidence scoring (structure score + field score)
        # Structure score
        structure_score_map = {
            "FromPathBrandProductVariation": 2.0,
            "FromPathBrandProductVariationParts": 2.2,  # Structure D: more detailed variation info
            "FromPathBrandImage": 1.5,
            "FromPathProduct": 1.2,
            "FlatImage": 1.0,
            "FolderMerchant": 0.5,
            "NotFound": 0
        }
        structure_score = structure_score_map.get(result["match_source"], 0)
        # Field score
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
            self.debug_log(f"2. batch_match - fullpath {path}...")
            self.debug_log(f"2. batch_match - structure {structure}...")
            self.debug_log(f"2. batch_match - clean_path {clean_path}...")
            self.debug_log(f"2. batch_match - merchant {merchant}...")
            self.debug_log(f"2. batch_match - results {result}...")
        return results

    def get_structure_type(self, image_path: str) -> str:
        parts = image_path.lower().split(os.sep)
        if parts[-3] == "images":  # Structure B
            return "B"
        elif parts[-2] == "images":  # Structure A
            return "A"
        else:  # Assume not A then C (brand image)
            return "C"

    def is_brand_folder(self, folder_name: str) -> bool:
        """
        Determine if the folder name is a brand name
        """
        # Special case: folders with only digits are considered product numbers
        if folder_name.isdigit():
            return False
            
        folder_normalized = folder_name.lower().strip()
        
        for item in self.meta_list:
            brand = item.get("brand")
            # Check if brand exists and is not None
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

    # def clean_part(self, part: str) -> str:
    #     # Remove common suffix tags (case-insensitive)
    #     part = re.sub(r'\b(cs|cc|hr)\b', '', part, flags=re.IGNORECASE)
    #     
    #     # Remove parts like 100x200 or 300×400
    #     part = re.sub(r'\d+\s*[x×]\s*\d+', '', part)

    #     # Remove extra underscores, hyphens, spaces
    #     part = re.sub(r'[-_]+', ' ', part)
    #     part = part.strip()

    #     return part
    def clean_part(self, part: str) -> str:
        # Convert all connectors to spaces for easier tokenization
        part = re.sub(r'[-_]+', ' ', part)

        # Remove leading numbers. (e.g. 10., 5.)
        part = re.sub(r'^\d+\.\s*', '', part)
        part = re.sub(r'^\d+\)\s*', '', part)

        # Tokenize
        tokens = part.lower().split()

        # Remove unwanted parts
        exclude = {"cs", "cc", "hr"}
        cleaned_tokens = [
            token for token in tokens
            if token not in exclude
            and not re.match(r'^\$\d+', token)
            and not re.match(r'^\d+\s*[x×]\s*\d+$', token)
        ]

        return '_'.join(cleaned_tokens)

