# app/api/company.py
from fastapi import APIRouter, Depends, Query
from app.core.auth import require_api_key
from app.services.company import get_org_id_by_taxcode
# from app.services.decode import decode_fields
from app.database import supabase

router = APIRouter(
    prefix="/company",
    tags=["Company"],
    dependencies=[Depends(require_api_key)]
)

@router.get("/{taxcode}")
def get_company(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"])
):
    res = (
        supabase
        .table("organization_information")
        .select("*")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Not found")

    # decoded = decode_fields(res.data, language)

    return {
        "meta": {
            "taxcode": taxcode,
            "language": language
        },
        "data": res.data
    }


@router.get("/{taxcode}/balance-sheet")
def balance_sheet(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"])
):
    org_id = get_org_id_by_taxcode(taxcode)

    res = (
        supabase
        .table("balance_sheet")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Balance sheet not found")

    return {
        "meta": {"taxcode": taxcode, "language": language},
        "data": res.data
    }