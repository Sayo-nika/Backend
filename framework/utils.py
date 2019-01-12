def try_int(num: int, fallback: int):
    try:
        return int(num)
    except ValueError:
        return fallback
