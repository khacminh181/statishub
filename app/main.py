from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal, supabase
from app.crud import get_company_by_taxcode
from app.schemas import CompanyResponse

app = FastAPI(
    title="Statishub Company API",
    version="1.0.0"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/company/{taxcode}")
def get_company(taxcode: str):
    res = (supabase
        .table("organization_information")
        .select("*")
        .eq("taxcode", "taxcode")
        .is_("ishistory", "false")
        .execute())

    if not res.data:
        raise HTTPException(404, "Not found")

    return res.data

@app.get("/company/{taxcode}/balance-sheet")
def get_balance_sheet(taxcode: str):
    org_res = (
        supabase
        .table("organization_information")
        .select("organizationid, taxcode")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not org_res.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization_id = org_res.data["organizationid"]

    # 2. Lấy balance sheet theo organization_id
    bs_res = (
        supabase
        .table("balance_sheet")
        .select("*")
        .eq("organizationid", organization_id)
        .eq("ishistory", False)
        .execute()
    )

    if not bs_res.data:
        raise HTTPException(status_code=404, detail="Balance sheet not found")

    return {
        "taxcode": taxcode,
        "balance_sheet": bs_res.data
    }

@app.get("/company/{taxcode}/income-statement")
def get_income_statement(taxcode: str):
    org_res = (
        supabase
        .table("organization_information")
        .select("organizationid, taxcode")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not org_res.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization_id = org_res.data["organizationid"]


    # 2. Lấy Income Statement theo organization_id
    is_res = (
        supabase
        .table("income_statement")
        .select("*")
        .eq("organizationid", organization_id)
        .eq("ishistory", False)
        .execute()
    )

    if not is_res.data:
        raise HTTPException(status_code=404, detail="Income Statement not found")

    return {
        "taxcode": taxcode,
        "income-statement": is_res.data
    }


@app.get("/company/{taxcode}/cashflow")
def get_cashflow(taxcode: str):
    org_res = (
        supabase
        .table("organization_information")
        .select("organizationid, taxcode")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not org_res.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization_id = org_res.data["organizationid"]


    # 2. Lấy cashflow theo organization_id
    res = (
        supabase
        .table("cash_flow")
        .select("*")
        .eq("organizationid", organization_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="Cash flow not found")

    return {
        "taxcode": taxcode,
        "cash-flow": res.data
    }


@app.get("/company/{taxcode}/shareholders")
def get_shareholders(taxcode: str):
    org_res = (
        supabase
        .table("organization_information")
        .select("organizationid, taxcode")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not org_res.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization_id = org_res.data["organizationid"]


    # 2. Lấy share_holder theo organization_id
    res = (
        supabase
        .table("share_holder")
        .select("*")
        .eq("organizationid", organization_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="shareholders not found")

    return {
        "taxcode": taxcode,
        "share_holder": res.data
    }

@app.get("/company/{taxcode}/structure")
def get_structure(taxcode: str):
    org_res = (
        supabase
        .table("organization_information")
        .select("organizationid, taxcode")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not org_res.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization_id = org_res.data["organizationid"]


    # 2. Lấy structure theo organization_id
    res = (
        supabase
        .table("organization_role")
        .select("*")
        .eq("leftorganizationid", organization_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="structure not found")

    return {
        "taxcode": taxcode,
        "structure": res.data
    }

@app.get("/company/{taxcode}/personnel")
def get_personnel(taxcode: str):
    org_res = (
        supabase
        .table("organization_information")
        .select("organizationid, taxcode")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not org_res.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization_id = org_res.data["organizationid"]


    # 2. Lấy person theo organization_id
    res = (
        supabase
        .table("person")
        .select("*")
        .eq("sourceorganizationid", organization_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        raise HTTPException(status_code=404, detail="person not found")

    return {
        "taxcode": taxcode,
        "person": res.data
    }

@app.get("/company/{taxcode}/compliance")
def get_compliance(taxcode: str):
    org_res = (
        supabase
        .table("organization_information")
        .select("organizationid, taxcode")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not org_res.data:
        raise HTTPException(status_code=404, detail="Organization not found")

    organization_id = org_res.data["organizationid"]


    # 2. Lấy tax_fee_liability theo organization_id
    res1 = (
        supabase
        .table("tax_fee_liability")
        .select("*")
        .eq("sourceorganizationid", organization_id)
        .eq("ishistory", False)
        .execute()
    )

    # 3. Lấy insurance_liability theo organization_id
    res2 = (
        supabase
        .table("insurance_liability")
        .select("*")
        .eq("sourceorganizationid", organization_id)
        .eq("ishistory", False)
        .execute()
    )

    return {
        "taxcode": taxcode,
        "tax_fee_liability": res1.data,
        "insurance_liability": res2.data
    }

# @app.get(
#     "/company/{taxcode}",
#     response_model=CompanyResponse,
#     summary="Get company information by tax code"
# )
# def get_company(taxcode: str, db: Session = Depends(get_db)):
#     company = get_company_by_taxcode(db, taxcode)

#     if not company:
#         raise HTTPException(status_code=404, detail="Company not found")

#     return {
#         "BusinessTypeId": company.BusinessTypeId,
#         "LocationId": company.LocationId,
#         "ActiveStatusId": company.ActiveStatusId,
#         "MainVSICId": company.MainVSICId,
#         "IcbId": company.IcbId,
#         "CurrencyId": company.CurrencyId,
#         "TaxCodeStatusId": company.TaxCodeStatusId,
#         "RegisterDateId": company.RegisterDateId,

#         "TaxCode": company.TaxCode,
#         "OrganizationName": company.OrganizationName,
#         "OrganizationShortName": company.OrganizationShortName,
#         "CharterCapital": company.CharterCapital,
#         "Address": company.Address,
#         "Telephone": company.Telephone,
#         "Fax": company.Fax,
#         "Email": company.Email,
#         "Website": company.Website,
#         "LogoURL": company.LogoURL,

#         "en_OrganizationName": company.en_OrganizationName,
#         "en_OrganizationShortName": company.en_OrganizationShortName,
#         "en_Address": company.en_Address,

#         "CurrentBusinessTypeId": company.CurrentBusinessTypeId,
#         "VersionDateId": company.VersionDateId
#     }
