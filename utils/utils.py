def to_bool(v):
    if isinstance(v, str):
        return v.lower() in {"yes", "true", "t", "1"}
    else:
        return bool(v)