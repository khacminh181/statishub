# app/api/company.py
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.auth import require_api_key
from app.services.company import get_org_id_by_taxcode
# from app.services.decode import decode_fields
from app.database import supabase
from app.services.credit import consume_credit
from app.core.auth import verify_api_key
from app.core.redis import redis_client

router = APIRouter(
    prefix="/company",
    tags=["Company"],
    # dependencies=[Depends(require_api_key)]
    dependencies=[Depends(verify_api_key)]
)

@router.get("/{taxcode}")
def get_company(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key=Depends(verify_api_key)
):
    # 1 Consume credit
    consume_credit(api_key["api_key"])

    # 2 Cache
    cache_key = f"company:{taxcode}:{language}"
    cached = redis_client.get(cache_key)
    if cached:
        return eval(cached)

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
        raise HTTPException(status_code=404, detail="Not found")

    row = res.data

    data = {
        "BusinessTypeId": row.get("business_type_id"),
        "LocationId": row.get("location_id"),
        "ActiveStatusId": row.get("active_status_id"),
        "MainVSICId": row.get("main_vsic_id"),
        "IcbId": row.get("icb_id"),
        "CurrencyId": row.get("currency_id"),
        "TaxCodeStatusId": row.get("taxcode_status_id"),
        "RegisterDateId": row.get("register_date"),
        "TaxCode": row.get("taxcode"),
        "CharterCapital": row.get("charter_capital"),
        "Telephone": row.get("telephone"),
        "Fax": row.get("fax"),
        "Email": row.get("email"),
        "Website": row.get("website"),
        "LogoURL": row.get("logo_url"),
        "CurrentBusinessTypeId": row.get("current_business_type_id"),
        "VersionDateId": row.get("version_date"),
    }

    # Language dependent fields
    if language == "vi":
        data.update({
            "OrganizationName": row.get("organization_name"),
            "OrganizationShortName": row.get("organization_short_name"),
            "Address": row.get("address"),
        })
    else:
        data.update({
            "en_OrganizationName": row.get("en_organization_name"),
            "en_OrganizationShortName": row.get("en_organization_short_name"),
            "en_Address": row.get("en_address"),
        })

    return {
        "meta": {
            "taxcode": taxcode,
            "language": language
        },
        "data": data
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

@router.get("/company/{taxcode}/income-statement")
def get_income_statement(taxcode: str,
    language: str = Query("en", enum=["en", "vi"])
    ):
    org_id = get_org_id_by_taxcode(taxcode)

    # 2. Lấy Income Statement theo org_id
    is_res = (
        supabase
        .table("income_statement")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not is_res.data:
        raise HTTPException(status_code=404, detail="Income Statement not found")

    return {
        "taxcode": taxcode,
        "income-statement": is_res.data
    }


@router.get("/company/{taxcode}/cashflow")
def get_cashflow(taxcode: str,
    language: str = Query("en", enum=["en", "vi"])
    ):
    org_id = get_org_id_by_taxcode(taxcode)

    # 2. Lấy cashflow theo org_id
    res = (
        supabase
        .table("cash_flow")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Cash flow not found")

    return {
        "taxcode": taxcode,
        "cash-flow": res.data
    }


@router.get("/company/{taxcode}/shareholders")
def get_shareholders(taxcode: str,
    language: str = Query("en", enum=["en", "vi"])
    ):
    org_id = get_org_id_by_taxcode(taxcode)

    # 2. Lấy share_holder theo org_id
    res = (
        supabase
        .table("share_holder")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="shareholders not found")

    return {
        "taxcode": taxcode,
        "share_holder": res.data
    }

@router.get("/company/{taxcode}/structure")
def get_structure(taxcode: str,
    language: str = Query("en", enum=["en", "vi"])):
    org_id = get_org_id_by_taxcode(taxcode)

    # 2. Lấy structure theo org_id
    res = (
        supabase
        .table("organization_role")
        .select("*")
        .eq("leftorganizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="structure not found")

    return {
        "taxcode": taxcode,
        "structure": res.data
    }

@router.get("/company/{taxcode}/personnel")
def get_personnel(taxcode: str,
    language: str = Query("en", enum=["en", "vi"])
    ):
    org_id = get_org_id_by_taxcode(taxcode)

    # 2. Lấy person theo org_id
    res = (
        supabase
        .table("person")
        .select("*")
        .eq("sourceorganizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="person not found")

    return {
        "taxcode": taxcode,
        "person": res.data
    }

@router.get("/company/{taxcode}/compliance")
def get_compliance(taxcode: str,
    language: str = Query("en", enum=["en", "vi"])):
    org_id = get_org_id_by_taxcode(taxcode)

    # 2. Lấy tax_fee_liability theo org_id
    res1 = (
        supabase
        .table("tax_fee_liability")
        .select("*")
        .eq("sourceorganizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    # 3. Lấy insurance_liability theo org_id
    res2 = (
        supabase
        .table("insurance_liability")
        .select("*")
        .eq("sourceorganizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    return {
        "taxcode": taxcode,
        "tax_fee_liability": res1.data,
        "insurance_liability": res2.data
    }