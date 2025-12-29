# app/services/company.py
from fastapi import HTTPException
from app.database import supabase

def get_org_id_by_taxcode(taxcode: str) -> str:
    res = (
        supabase
        .table("organization_information")
        .select("organizationid")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Organization not found")

    return res.data["organizationid"]
