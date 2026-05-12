import re


def parse_ints(text: str) -> list[int]:
    return [int(match) for match in re.findall(r"-?\d+", text)]

