import pandas as pd
import json

csv_path = "./data/MM_SG_Full_Products_Data.csv"
df = pd.read_csv(csv_path)

df = df.where(pd.notnull(df), None)

json_data = []

for _, row in df.iterrows():
    item = {
        "variation_id": row["variation_id"],
        "state": row["state"],
        "product_name": row["product_name"],
        "product_variation_name": row["product_variation_name"],
        "variation_image": row["variation_image"],
        "images": [
            row.get("image1"),
            row.get("image2"),
            row.get("image3"),
            row.get("image4")
        ],
        "merchant": {
            "id": str(row["merchant_id"]),
            "name": row["merchant_name"]
        },
        "brand": row["brand_name"]
    }
    json_data.append(item)

with open("./data/metadata.json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)