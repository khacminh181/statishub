"""
Database connection management for Supabase.
"""
from supabase import create_client
from app.core.config import settings

supabase = create_client(settings.supabase_url, settings.supabase_key)

# response = (
#     supabase
#     .table("organization_information")
#     .select("*")
#     .eq("taxcode", "5702076880")
#     .is_("ishistory", "false")
#     .execute()
# )

# print(response.data)
