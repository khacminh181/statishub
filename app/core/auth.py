# app/core/auth.py
from fastapi import Header, HTTPException, Depends
from app.core.redis import redis_client

VALID_API_KEYS = {"demo-key-123"}

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
# def verify_api_key(x_api_key: str = Header(...)):
#     # 1. Try redis
#     cache_key = f"apikey:{x_api_key}"
#     cached = redis_client.get(cache_key)

#     if cached:
#         return eval(cached)

#     # 2. DB
#     res = (
#         supabase
#         .table("api_keys")
#         .select("*")
#         .eq("api_key", x_api_key)
#         .eq("is_active", True)
#         .single()
#         .execute()
#     )

#     if not res.data:
#         raise HTTPException(401, "Invalid API Key")

#     redis_client.setex(cache_key, 300, str(res.data))  # cache 5 phút
#     # return res.data    


def verify_api_key(x_api_key: str = Header(...)):
    redis_key = f"apikey:{x_api_key}"
    data = redis_client.hgetall(redis_key)

    if not data or data.get("is_active") != "1":
        raise HTTPException(401, "Invalid API Key")

    return {
        "id": int(data["id"]),
        "api_key": x_api_key,
        "client_name": data["client_name"],
        "credits": int(data["credits"])
    }