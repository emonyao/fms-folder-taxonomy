import re

def extract_color_phrase(filename: str) -> str:
    """
    从文件名中提取颜色短语（既支持组合形式，也支持单个颜色词）。
    支持 -, _, /, &, 空格等分隔符。
    """
    color_keywords = {
        "black", "grey", "gray", "white", "blue", "red", "green", "pink",
        "yellow", "purple", "beige", "brown", "orange", "silver", "gold", "khaki"
    }

    filename = filename.lower()
    filename = re.sub(r'\.(jpg|jpeg|png|webp)$', '', filename)

    # 先尝试提取组合颜色（如 black-grey）
    pattern = r"[a-z]+(?:[\s/_\-&\\]+[a-z]+)+"
    candidates = re.findall(pattern, filename)

    for phrase in candidates:
        words = re.split(r"[\s/_\-&\\]+", phrase)
        if all(word in color_keywords for word in words):
            return "_".join(words).strip(" ()")

    # 如果没有组合词，再检查是否有单独颜色词
    for word in re.split(r"[\s/_\-&\\]+", filename):
        if word in color_keywords:
            return word

    return ""
