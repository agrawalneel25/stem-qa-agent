import re


def slugify(text: str) -> str:
    return re.sub(r"\s+", "-", text.strip())

