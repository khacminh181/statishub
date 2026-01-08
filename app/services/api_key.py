import uuid
from datetime import datetime
from typing import List, Dict
from app.core.redis import redis_client
from app.services.rate_limit import get_api_rate_limit

API_KEY_TTL = 60 * 60 * 24 * 30  # 30 ngày


def create_api_key(client_name: str, credits: int = 1000) -> Dict:
    api_key = f"sk_{uuid.uuid4().hex}"
    redis_key = f"apikey:{api_key}"

    data = {
        "id": redis_client.incr("apikey:id"),
        "api_key": api_key,
        "client_name": client_name,
        "credits": credits,
        "is_active": 1,
        "created_at": datetime.utcnow().isoformat(),
    }

    redis_client.hset(redis_key, mapping=data)
    redis_client.expire(redis_key, API_KEY_TTL)

    return data


def revoke_api_key(api_key: str):
    redis_key = f"apikey:{api_key}"
    if not redis_client.exists(redis_key):
        return False

    redis_client.hset(redis_key, "is_active", 0)
    return True


def add_credit(api_key: str, amount: int):
    redis_key = f"apikey:{api_key}"
    if not redis_client.exists(redis_key):
        return None

    return redis_client.hincrby(redis_key, "credits", amount)


def get_api_key(api_key: str):
    data = redis_client.hgetall(f"apikey:{api_key}")
    return data or None


# def list_api_keys(limit: int = 100) -> List[Dict]:
#     keys = redis_client.scan_iter("apikey:sk_*")
#     result = []

#     for i, key in enumerate(keys):
#         if i >= limit:
#             break
#         data = redis_client.hgetall(key)
#         if data:
#             data["credits"] = int(data["credits"])
#             data["id"] = int(data["id"])
#             result.append(data)

#     return result

def list_api_keys(limit: int = 100) -> List[Dict]:
    keys = redis_client.scan_iter("apikey:sk_*")
    result = []

    for key in keys:
        if len(result) >= limit:
            break

        data = redis_client.hgetall(key)
        if not data:
            continue

        # Redis trả string → convert
        if int(data.get("is_active", 0)) != 1:
            continue

        data["credits"] = int(data["credits"])
        data["id"] = int(data["id"])
        data["is_active"] = int(data["is_active"])
        data["rate_limit"] = get_api_rate_limit(data["api_key"])

        result.append(data)

    return result
