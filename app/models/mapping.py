def map_insurance_liability(row: dict, taxcode: str) -> dict:
    return {
        "TaxCode": taxcode,
        "DepartmentOrganization": row.get("departmentorganizationid"),
        "periodid": row.get("periodid"),
        "insurancetypeid": row.get("insurancetypeid"),
        "publicdateid": row.get("publicdateid"),
        "recorddateid": row.get("recorddateid"),
        "currencyid": row.get("currencyid"),
        "monthowed": row.get("monthowed"),
        "numberofemployee": row.get("numberofemployee"),
        "totalvalue": row.get("totalvalue"),
        "versiondateid": row.get("versiondateid"),
    }


def map_tax_fee_liability(row: dict, taxcode: str) -> dict:
    return {
        "TaxCode": taxcode,
        "DepartmentOrganization": row.get("departmentorganizationid"),
        "periodid": row.get("periodid"),
        "taxfeetypeid": row.get("taxfeetypeid"),
        "nationalbudgettypeid": row.get("nationalbudgettypeid"),
        "taxfeeliabilitystatusid": row.get("taxfeeliabilitystatusid"),
        "enforcementtypeid": row.get("enforcementtypeid"),
        "publicdateid": row.get("publicdateid"),
        "currencyid": row.get("currencyid"),
        "totalvalue": row.get("totalvalue"),
        "versiondateid": row.get("versiondateid"),
    }