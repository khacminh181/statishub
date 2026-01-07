# app/api/company.py
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.auth import require_api_key, verify_api_key
from app.services.company import get_org_id_by_taxcode
# from app.services.decode import decode_fields
from app.database import supabase
from app.services.credit import consume_credit
from app.core.constants import COMPLIANCE_TABLE_MAP, INDUSTRY_TABLE_MAP
from app.core.redis import redis_client
from app.models.model import BalanceSheet, OrganizationInfo, IncomeStatement, CashFlow, ShareHolder, OrganizationSearchResponse, Person
from app.models.mapping import map_insurance_liability, map_tax_fee_liability
from app.utils.helper import build_search_cache_key
from typing import List, Literal
import json

router = APIRouter(
    prefix="/company",
    # tags=["Company"],
    # dependencies=[Depends(require_api_key)]
    dependencies=[Depends(verify_api_key)]
)

@router.get(
        "/{taxcode}",
        response_model=OrganizationInfo,
        tags=["Company Profile"]
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
        response_model=List[BalanceSheet],
        tags=["Financial Data"]
        )
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
        "/{taxcode}/income-statement",
        response_model=List[IncomeStatement],
        tags=["Financial Data"]
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
        "/{taxcode}/cashflow",
        response_model=List[CashFlow],
        tags=["Financial Data"]
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
        "/{taxcode}/shareholders",
        response_model=List[ShareHolder],
        tags=["Ownership & People"]
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

@router.get("/{taxcode}/structure", tags=["Ownership & People"])
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

@router.get("/{taxcode}/personnel", tags=["Ownership & People"])
def get_personnel(taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key=Depends(verify_api_key)
    ):
    # 1. Consume credit
    consume_credit(api_key["api_key"])

    # 2. Cache
    cache_key = f"personnel:{taxcode}:{language}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)   
    org_id = get_org_id_by_taxcode(taxcode)

    # Fetch position data from database
    position_info = (
        supabase
        .table("position")
        .select("positionid, positionname")
        .execute()
    )

    position_ids = [
        o["positionid"]
        for o in position_info.data
    ]

    position_map = {
        o["positionid"]: o["positionname"]
        for o in position_info.data
    }

    # 2. Lấy person theo org_id
    person_pos = (
        supabase
        .table("person_position")
        .select("*")
        .in_("positionid", list(position_ids))
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not person_pos.data:
        raise HTTPException(status_code=404, detail="person not found")

    person_ids = set()
    for r in person_pos.data:
        person_ids.add(r["personid"])

    person_info = (
        supabase
        .table("person")
        .select("personid, firstname, middlename, lastname")
        .in_("personid", list(person_ids))
        .execute()
    )

    person_map = {
        o["personid"]: f'{o.get("firstname")} {o.get("middlename")} {o.get("lastname")}'
        for o in person_info.data
    }

    personnel = [
    {
        "PersonId": r["personid"],
        "PersonName": person_map.get(r["personid"]),
        "PositionId": r["positionid"],
        "en_PositionName": position_map.get(r["positionid"]),
    }
    for r in person_pos.data
    ]

    # 5. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(personnel))
    return personnel

@router.get("/{taxcode}/compliance",
            tags=["Compliance"]
            )
def get_compliance(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    tablename: Literal["insuranceliability", "taxfeeliability"] = Query(...), 
    api_key=Depends(verify_api_key)
):
    table = COMPLIANCE_TABLE_MAP.get(tablename)
    if not table:
        raise HTTPException(status_code=400, detail="Invalid tablename")

    # 1. Consume credit
    consume_credit(api_key["api_key"])

    # 2. Cache
    cache_key = f"{table}:{taxcode}:{language}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    org_id = get_org_id_by_taxcode(taxcode)
    
    # 2. Query Supabase
    res = (
        supabase
        .table(table)
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Data not found")

    result = []
    # 3. Map data theo đúng docs
    if tablename == "insuranceliability":
        result = [
            map_insurance_liability(row, taxcode)
            for row in res.data
        ]

    if tablename == "taxfeeliability":
        result = [
            map_tax_fee_liability(row, taxcode)
            for row in res.data
        ]
    
    # 5. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(result))
    
    return result

# @router.get("/{taxcode}/industries")
# def get_compliance(
#     taxcode: str,
#     language: str = Query("en", enum=["en", "vi"]),
#     tablename: Literal["companyvsic", "companyicb"] = Query(...), 
#     api_key=Depends(verify_api_key)
# ):
#     table = INDUSTRY_TABLE_MAP.get(tablename)
#     if not table:
#         raise HTTPException(status_code=400, detail="Invalid tablename")

#     # 1. Consume credit
#     consume_credit(api_key["api_key"])

#     # 2. Cache
#     cache_key = f"{table}:{taxcode}:{language}"
#     cached = redis_client.get(cache_key)
#     if cached:
#         return json.loads(cached)
    
#     org_id = get_org_id_by_taxcode(taxcode)
    
#     # 2. Query Supabase
#     res = (
#         supabase
#         .table(table)
#         .select("*")
#         .eq("organizationid", org_id)
#         .eq("ishistory", False)
#         .execute()
#     )

#     if not res.data:
#         raise HTTPException(status_code=404, detail="Data not found")

#     result = []
#     # 3. Map data theo đúng docs
#     if tablename == "companyvsic":
#         result = [
#             map_companyvsic(row, taxcode)
#             for row in res.data
#         ]

#     if tablename == "companyicb":
#         result = [
#             map_companyicb(row, taxcode)
#             for row in res.data
#         ]
    
#     # 5. Cache result
#     redis_client.setex(cache_key, 3600, json.dumps(result))
    
#     return result

searchRouter = APIRouter(
    prefix="",
    # tags=["Company"],
    # dependencies=[Depends(require_api_key)]
    dependencies=[Depends(verify_api_key)]
)
@searchRouter.get(
    "/search",
    response_model=OrganizationSearchResponse,
    tags=["Search"]
)
def search_organization(
    name: str = Query(..., min_length=1, description="Organization name"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    api_key=Depends(verify_api_key)
):
    # 1. Consume credit
    consume_credit(api_key["api_key"])

    cache_key = build_search_cache_key(name, limit, offset)

    # 1 Try cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    keyword = f"%{name}%"

    # 1️ Query data
    data_resp = (
        supabase
        .table("organization_information")
        .select(
           "*" 
        )
        .eq("ishistory", False)
        .or_(
            f"organizationname.ilike.{keyword},"
            f"en_organizationname.ilike.{keyword}"
        )
        .range(offset, offset + limit - 1)
        .execute()
    )

    # 2️ Query total count
    count_resp = (
        supabase
        .table("organization_information")
        .select(
            "organizationid",
            count="exact"
        )
        .eq("ishistory", False)
        .or_(
            f"organizationname.ilike.{keyword},"
            f"en_organizationname.ilike.{keyword}"
        )
        .execute()
    )
    result = {
        "data": data_resp.data or [],
        "pagination": {
            "total": count_resp.count or 0,
            "limit": limit,
            "offset": offset
        }
    }

    # 5. Cache result
    redis_client.setex(cache_key, 3600, json.dumps(result))

    return result