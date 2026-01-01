from fastapi import HTTPException
from app.core.redis import redis_client


# def consume_credit(api_key_id: int):
#     redis_key = f"credit:{api_key_id}"

#     credit = redis_client.decr(redis_key)

#     if credit < 0:
#         raise HTTPException(402, "Out of credits")

#     # Fallback nếu chưa có cache
#     if credit == -1:
#         res = (
#             supabase
#             .table("api_keys")
#             .select("credits")
#             .eq("id", api_key_id)
#             .single()
#             .execute()
#         )

#         db_credit = res.data["credits"] - 1
#         if db_credit < 0:
#             raise HTTPException(402, "Out of credits")

#         redis_client.set(redis_key, db_credit)
#         supabase.table("api_keys").update(
#             {"credits": db_credit}
#         ).eq("id", api_key_id).execute()


def consume_credit(api_key: str):
    redis_key = f"apikey:{api_key}"
    print(redis_key)
    credit = redis_client.hincrby(redis_key, "credits", -1)
    print(credit)
    if credit < 0:
        raise HTTPException(402, "Out of credits")