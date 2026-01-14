"""
Company API endpoints for financial and organizational data.
"""

import re
from typing import Dict, List, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.auth import verify_api_key
from app.core.constants import COMPLIANCE_TABLE_MAP, INDUSTRY_TABLE_MAP
from app.core.dependency import rate_limit_dep
from app.core.exceptions import OrganizationNotFoundError
from app.database import supabase
from app.models.mapping import (
    map_companyicb,
    map_companyvsic,
    map_insurance_liability,
    map_tax_fee_liability,
)
from app.models.model import (
    BalanceSheet,
    CashFlow,
    IncomeStatement,
    OrganizationInfo,
    OrganizationSearchResponse,
    ShareHolder,
)
from app.services.company import get_org_id_by_taxcode
from app.services.credit import consume_credit
from app.utils.helper import (
    build_cache_key,
    build_search_cache_key,
    get_cached,
    inject_taxcode,
    set_cached,
)

router = APIRouter(
    prefix="/company",
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dep)],
)


@router.get("/{taxcode}", response_model=OrganizationInfo, tags=["Company Profile"])
def get_company(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> Dict:
    """Get company profile by taxcode."""
    consume_credit(api_key["api_key"])

    cache_key = build_cache_key("company", taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    res = (
        supabase.table("organization_information")
        .select("*")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not res.data:
        raise OrganizationNotFoundError(taxcode=taxcode)

    set_cached(cache_key, res.data)
    return res.data


@router.get("/{taxcode}/balance-sheet", response_model=List[BalanceSheet], tags=["Financial Data"])
def get_balance_sheet(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> List[Dict]:
    """Get balance sheet data for a company."""
    consume_credit(api_key["api_key"])

    cache_key = build_cache_key("balance-sheet", taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    org_id = get_org_id_by_taxcode(taxcode)
    res = (
        supabase.table("balance_sheet")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Balance sheet not found")

    result = inject_taxcode(res.data, taxcode)
    set_cached(cache_key, result)
    return result


@router.get(
    "/{taxcode}/income-statement",
    response_model=List[IncomeStatement],
    tags=["Financial Data"],
)
def get_income_statement(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> List[Dict]:
    """Get income statement data for a company."""
    consume_credit(api_key["api_key"])

    cache_key = build_cache_key("income-statement", taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    org_id = get_org_id_by_taxcode(taxcode)
    res = (
        supabase.table("income_statement")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Income statement not found")

    result = inject_taxcode(res.data, taxcode)
    set_cached(cache_key, result)
    return result


@router.get("/{taxcode}/cashflow", response_model=List[CashFlow], tags=["Financial Data"])
def get_cashflow(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> List[Dict]:
    """Get cashflow data for a company."""
    consume_credit(api_key["api_key"])

    cache_key = build_cache_key("cashflow", taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    org_id = get_org_id_by_taxcode(taxcode)
    res = (
        supabase.table("cash_flow")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Cash flow not found")

    result = inject_taxcode(res.data, taxcode)
    set_cached(cache_key, result)
    return result


@router.get(
    "/{taxcode}/shareholders", response_model=List[ShareHolder], tags=["Ownership & People"]
)
def get_shareholders(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> List[Dict]:
    """Get shareholders data for a company."""
    consume_credit(api_key["api_key"])

    cache_key = build_cache_key("shareholders", taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    org_id = get_org_id_by_taxcode(taxcode)
    res = (
        supabase.table("share_holder")
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Shareholders not found")

    result = inject_taxcode(res.data, taxcode)
    set_cached(cache_key, result)
    return result


@router.get("/{taxcode}/structure", tags=["Ownership & People"])
def get_structure(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> List[Dict]:
    """Get organizational structure/relationships for a company."""
    consume_credit(api_key["api_key"])

    cache_key = build_cache_key("structure", taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    org_id = get_org_id_by_taxcode(taxcode)
    res = (
        supabase.table("organization_role")
        .select("*")
        .eq("leftorganizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Structure not found")

    # Get related organization taxcodes
    org_ids = {r["rightorganizationid"] for r in res.data}
    org_info = (
        supabase.table("organization_information")
        .select("organizationid, taxcode")
        .in_("organizationid", list(org_ids))
        .execute()
    )
    org_map = {o["organizationid"]: o["taxcode"] for o in org_info.data}

    result = [
        {
            "LeftTaxCode": taxcode,
            "RightTaxCode": org_map.get(r["rightorganizationid"]),
            "LeftRoleId": r["leftroleid"],
            "RightRoleId": r["rightroleid"],
            "VersionDateId": r["versiondateid"],
        }
        for r in res.data
    ]

    set_cached(cache_key, result)
    return result


@router.get("/{taxcode}/personnel", tags=["Ownership & People"])
def get_personnel(
    taxcode: str,
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> List[Dict]:
    """Get personnel/management data for a company."""
    consume_credit(api_key["api_key"])

    cache_key = build_cache_key("personnel", taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    org_id = get_org_id_by_taxcode(taxcode)

    # Fetch position data
    position_info = supabase.table("dm_position").select("positionid, positionname").execute()
    position_ids = [o["positionid"] for o in position_info.data]
    position_map = {o["positionid"]: o["positionname"] for o in position_info.data}

    # Fetch person positions
    person_pos = (
        supabase.table("person_position")
        .select("*")
        .in_("positionid", position_ids)
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .in_("recordstatusid", [1, 6])
        .execute()
    )

    if not person_pos.data:
        raise HTTPException(404, "Personnel not found")

    # Fetch person details
    person_ids = {r["personid"] for r in person_pos.data}
    person_info = (
        supabase.table("person")
        .select("personid, firstname, middlename, lastname")
        .in_("personid", list(person_ids))
        .execute()
    )
    person_map = {
        o["personid"]: f'{o.get("firstname")} {o.get("middlename")} {o.get("lastname")}'
        for o in person_info.data
    }

    result = [
        {
            "PersonId": r["personid"],
            "PersonName": person_map.get(r["personid"]),
            "PositionId": r["positionid"],
            "en_PositionName": position_map.get(r["positionid"]),
        }
        for r in person_pos.data
    ]

    set_cached(cache_key, result)
    return result


@router.get("/{taxcode}/compliance", tags=["Compliance"])
def get_compliance(
    taxcode: str,
    tablename: Literal["insuranceliability", "taxfeeliability"] = Query(...),
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> List[Dict]:
    """Get compliance data (insurance/tax liability) for a company."""
    table = COMPLIANCE_TABLE_MAP.get(tablename)
    if not table:
        raise HTTPException(400, "Invalid tablename")

    consume_credit(api_key["api_key"])

    cache_key = build_cache_key(table, taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    org_id = get_org_id_by_taxcode(taxcode)
    res = (
        supabase.table(table)
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Data not found")

    if tablename == "insuranceliability":
        result = [map_insurance_liability(row, taxcode) for row in res.data]
    else:
        result = [map_tax_fee_liability(row, taxcode) for row in res.data]

    set_cached(cache_key, result)
    return result


@router.get("/{taxcode}/industries", tags=["Company Profile"])
def get_industries(
    taxcode: str,
    tablename: Literal["companyvsic", "companyicb"] = Query(...),
    language: str = Query("en", enum=["en", "vi"]),
    api_key: Dict = Depends(verify_api_key),
) -> List[Dict]:
    """Get industry classification data (VSIC/ICB) for a company."""
    table = INDUSTRY_TABLE_MAP.get(tablename)
    if not table:
        raise HTTPException(400, "Invalid tablename")

    consume_credit(api_key["api_key"])

    cache_key = build_cache_key(table, taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    org_id = get_org_id_by_taxcode(taxcode)
    res = (
        supabase.table(table)
        .select("*")
        .eq("organizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(404, "Data not found")

    if tablename == "companyvsic":
        vsic_ids = list({row["vsicid"] for row in res.data if row.get("vsicid")})
        vsic_map = {}
        if vsic_ids:
            vsic_master = (
                supabase.table("cmms_dm_vsic").select("*").in_("vsicid", vsic_ids).execute()
            )
            vsic_map = {v["vsicid"]: v for v in (vsic_master.data or [])}

        result = [
            map_companyvsic(
                row=row,
                taxcode=taxcode,
                vsic_master=vsic_map.get(row.get("vsicid"), {}),
                language=language,
            )
            for row in res.data
        ]
    else:
        icb_ids = list({row["icbid"] for row in res.data if row.get("icbid")})
        icb_map = {}
        if icb_ids:
            icb_master = supabase.table("cmms_dm_icb").select("*").in_("icbid", icb_ids).execute()
            icb_map = {i["icbid"]: i for i in (icb_master.data or [])}

        result = [
            map_companyicb(
                row=row,
                taxcode=taxcode,
                icb_master=icb_map.get(row.get("icbid"), {}),
                language=language,
            )
            for row in res.data
        ]

    set_cached(cache_key, result)
    return result


searchRouter = APIRouter(
    prefix="",
    dependencies=[Depends(verify_api_key), Depends(rate_limit_dep)],
)


def _sanitize_search_input(name: str) -> str:
    """
    Sanitize search input to prevent SQL/filter injection.

    Removes special characters that could modify PostgREST filter syntax
    while preserving Vietnamese characters and common punctuation.
    """
    # Remove PostgREST filter operators and dangerous characters
    # Keep alphanumeric, Vietnamese characters, spaces, and basic punctuation
    sanitized = re.sub(r"[^\w\sÀ-ỹ\-\.]", "", name, flags=re.UNICODE)
    # Remove multiple consecutive spaces
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized


@searchRouter.get("/search", response_model=OrganizationSearchResponse, tags=["Search"])
def search_organization(
    name: str = Query(..., min_length=1, max_length=200, description="Organization name"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    api_key: Dict = Depends(verify_api_key),
) -> Dict:
    """Search organizations by name."""
    consume_credit(api_key["api_key"])

    # Sanitize input to prevent filter injection
    safe_name = _sanitize_search_input(name)
    if not safe_name:
        return {"data": [], "pagination": {"total": 0, "limit": limit, "offset": offset}}

    cache_key = build_search_cache_key(safe_name, limit, offset)
    cached = get_cached(cache_key)
    if cached:
        return cached

    keyword = f"%{safe_name}%"

    # Query data
    data_resp = (
        supabase.table("organization_information")
        .select("*")
        .eq("ishistory", False)
        .or_(f"organizationname.ilike.{keyword},en_organizationname.ilike.{keyword}")
        .range(offset, offset + limit - 1)
        .execute()
    )

    # Query total count
    count_resp = (
        supabase.table("organization_information")
        .select("organizationid", count="exact")
        .eq("ishistory", False)
        .or_(f"organizationname.ilike.{keyword},en_organizationname.ilike.{keyword}")
        .execute()
    )

    result = {
        "data": data_resp.data or [],
        "pagination": {"total": count_resp.count or 0, "limit": limit, "offset": offset},
    }

    set_cached(cache_key, result)
    return result
