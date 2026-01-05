def build_search_cache_key(name: str, limit: int, offset: int) -> str:
    return f"search:organization:{name.lower()}:{limit}:{offset}"
