import re

def extract_color_phrase(filename: str) -> str:
    """
    从文件名中提取颜色短语（保留组合形式，不只取一个颜色词）。
    支持常见分隔符，如 -, _, /, &, 空格等。
    """
    color_keywords = {
        "black", "grey", "gray", "white", "blue", "red", "green", "pink",
        "yellow", "purple", "beige", "brown", "orange", "silver", "gold"
    }

    # 将文件名小写，移除扩展名
    filename = filename.lower()
    filename = re.sub(r'\.(jpg|jpeg|png|webp)$', '', filename)

    # 查找所有可能的词组（例如 black-white, black_white, black&white）
    pattern = r"[a-z]+(?:[\s/_\-&\\]+[a-z]+)+"
    candidates = re.findall(pattern, filename)

    for phrase in candidates:
        # 分割成单个词，验证是否全部为颜色词
        words = re.split(r"[\s/_\-&\\]+", phrase)
        if all(word in color_keywords for word in words):
            return phrase.strip(" ()")

    return ""
