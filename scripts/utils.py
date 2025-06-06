import re

def extract_color_phrase(filename: str) -> str:
    """
    从文件名中提取颜色短语（保留组合形式，不只取一个颜色词）。
    """
    # 定义颜色基本词
    color_keywords = [
        "black", "grey", "gray", "white", "blue", "red", "green", "pink",
        "yellow", "purple", "beige", "brown", "orange", "silver", "gold"
    ]
    
    # 构建颜色组合正则（匹配带连接符的组合颜色）
    # 匹配如 Black-Grey, Black/Grey, Black & Grey, (Black Grey) 等形式
    pattern = r"([a-z]+[\s/_\-&\\]*[a-z]+)"

    # 小写化整个文件名方便匹配
    lowered = filename.lower()

    matches = re.findall(pattern, lowered)

    for phrase in matches:
        words = re.split(r"[\s/_\-&\\]+", phrase)
        if all(word in color_keywords for word in words if word):
            return phrase.strip(" ()")  # 去掉外围括号或空格

    return ""
