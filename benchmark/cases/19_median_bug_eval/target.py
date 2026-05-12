def median(values: list[int]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    return float(ordered[middle])

