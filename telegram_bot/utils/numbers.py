def is_num(num: float | int | str, type_num: str = "int") -> bool:
    try:
        int(num) if type_num == "int" else float(num)
        return True
    except (ValueError, TypeError):
        return False
