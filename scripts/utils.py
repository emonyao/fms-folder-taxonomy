import re

def extract_color_phrase(filename: str) -> str:
    """
    Extract color phrase from filename (supports both combined forms and single color words).
    Supports -, _, /, &, space and other separators.
    """
    color_keywords = {
        "black", "grey", "gray", "white", "blue", "red", "green", "pink",
        "yellow", "purple", "beige", "brown", "orange", "silver", "gold", "khaki"
    }

    filename = filename.lower()
    filename = re.sub(r'\.(jpg|jpeg|png|webp)$', '', filename)

    # First try to extract combined colors (e.g. black-grey)
    pattern = r"[a-z]+(?:[\s/_\-&\\]+[a-z]+)+"
    candidates = re.findall(pattern, filename)

    for phrase in candidates:
        words = re.split(r"[\s/_\-&\\]+", phrase)
        if all(word in color_keywords for word in words):
            return "_".join(words).strip(" ()")

    # If no combined word, then check for single color words
    for word in re.split(r"[\s/_\-&\\]+", filename):
        if word in color_keywords:
            return word

    return ""
