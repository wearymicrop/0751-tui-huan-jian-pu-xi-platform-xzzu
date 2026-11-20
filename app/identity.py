import unicodedata


def token(value):
    """保留前导零，归一全半角、首尾空白和大小写。"""
    if not isinstance(value, str):
        raise ValueError("编码必须是字符串")
    normalized = unicodedata.normalize("NFKC", value).strip().upper()
    if len(normalized) > 80 or normalized in {"", "-", "N/A", "NULL", "未知"}:
        raise ValueError("编码缺失或过长")
    return normalized
