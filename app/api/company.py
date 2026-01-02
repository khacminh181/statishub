# app/api/company.py
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.auth import require_api_key
from app.services.company import get_org_id_by_taxcode
# from app.services.decode import decode_fields
from app.database import supabase
from app.services.credit import consume_credit
from app.core.auth import verify_api_key
from app.core.redis import redis_client
from app.models.model import BalanceSheet, OrganizationInfo, IncomeStatement, CashFlow, ShareHolder
from typing import List
import json

router = APIRouter(
    prefix="/company",
    tags=["Company"],
    # dependencies=[Depends(require_api_key)]
    dependencies=[Depends(verify_api_key)]
)

@router.get(
        "/{taxcode}",
        response_model=OrganizationInfo
        )
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
        return json.loads(cached)

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

    # 4. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(res.data, default=str))

    return res.data


@router.get(
        "/{taxcode}/balance-sheet",
        response_model=List[BalanceSheet])
def balance_sheet(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key=Depends(verify_api_key)
):
    # 1. Consume credit
    consume_credit(api_key["api_key"])

    # 2. Cache
    cache_key = f"balance-sheet:{taxcode}:{language}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 3. Query DB
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

    # 4. Inject taxcode
    for row in res.data:
        row["taxcode"] = taxcode

    # 5. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(res.data))
    return res.data

@router.get(
        "/company/{taxcode}/income-statement",
        response_model=List[IncomeStatement]
        )
def get_income_statement(taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key=Depends(verify_api_key)
    ):
    # 1. Consume credit
    consume_credit(api_key["api_key"])

    # 2. Cache
    cache_key = f"income-statement:{taxcode}:{language}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    org_id = get_org_id_by_taxcode(taxcode)

    # 2. Lấy Income Statement theo org_id
    res = (
        supabase
        .table("income_statement")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Income Statement not found")

    # 4. Inject taxcode
    for row in res.data:
        row["taxcode"] = taxcode

    # 5. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(res.data))
    return res.data


@router.get(
        "/company/{taxcode}/cashflow",
        response_model=List[CashFlow]
        )
def get_cashflow(taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key=Depends(verify_api_key)
    ):

    # 1. Consume credit
    consume_credit(api_key["api_key"])

    # 2. Cache
    cache_key = f"cashflow:{taxcode}:{language}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
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

    # 4. Inject taxcode
    for row in res.data:
        row["taxcode"] = taxcode

    # 5. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(res.data))
    return res.data


@router.get(
        "/company/{taxcode}/shareholders",
        response_model=List[ShareHolder]
        )
def get_shareholders(taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key=Depends(verify_api_key)
    ):

    # 1. Consume credit
    consume_credit(api_key["api_key"])

    # 2. Cache
    cache_key = f"shareholders:{taxcode}:{language}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
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
    # 4. Inject taxcode
    for row in res.data:
        row["taxcode"] = taxcode

    # 5. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(res.data))
    return res.data

@router.get("/company/{taxcode}/structure")
def get_structure(taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key=Depends(verify_api_key)
    ):

    # 1. Consume credit
    consume_credit(api_key["api_key"])

    # 2. Cache
    cache_key = f"structure:{taxcode}:{language}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
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


    org_ids = set()
    for r in res.data:
        org_ids.add(r["rightorganizationid"])

    org_info = (
        supabase
        .table("organization_information")
        .select("organizationid, taxcode")
        .in_("organizationid", list(org_ids))
        .execute()
    )

    org_map = {
        o["organizationid"]: o["taxcode"]
        for o in org_info.data
    }

    structure = [
    {
        "LeftTaxCode": taxcode,
        "RightTaxCode": org_map.get(r["rightorganizationid"]),
        "LeftRoleId": r["leftroleid"],
        "RightRoleId": r["rightroleid"],
        "VersionDateId": r["versiondateid"],
    }
    for r in res.data
    ]

    # 5. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(structure))
    
    return structure

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