"""
Data mapping functions for transforming database records to API responses.
"""

from typing import Dict


def map_insurance_liability(row: Dict, taxcode: str) -> Dict:
    """Map insurance liability database record to API response format."""
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


def map_tax_fee_liability(row: Dict, taxcode: str) -> Dict:
    """Map tax/fee liability database record to API response format."""
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


def map_companyvsic(
    row: Dict,
    taxcode: str,
    vsic_master: Dict,
    language: str = "en",
) -> Dict:
    """Map company VSIC (Vietnam Standard Industrial Classification) to API response."""
    return {
        "TaxCode": taxcode,
        "VSICId": row.get("vsicid"),
        "IsMain": row.get("ismain"),
        "VSICCode": vsic_master.get("vsiccode"),
        "VSICName": vsic_master.get("vsicname"),
        "VSICLevel": vsic_master.get("vsiclevel"),
        "VSICOrder": vsic_master.get("vsicorder"),
        "VSICCodePath": vsic_master.get("vsiccodepath"),
        "VSICNamePath": vsic_master.get("vsicnamepath"),
        "en_VSICName": vsic_master.get("en_vsicname"),
        "en_VSICNamePath": vsic_master.get("en_vsicname_path"),
        "VersionDateId": vsic_master.get("versiondateid"),
    }


def map_companyicb(
    row: Dict,
    taxcode: str,
    icb_master: Dict,
    language: str = "en",
) -> Dict:
    """Map company ICB (Industry Classification Benchmark) to API response."""
    return {
        "TaxCode": taxcode,
        "ICBId": row.get("icbid"),
        "IcbCode": icb_master.get("icbcode"),
        "ICBName": icb_master.get("icbname"),
        "ICBLevel": icb_master.get("icblevel"),
        "ICBOrder": icb_master.get("icborder"),
        "ICBCodePath": icb_master.get("icbcodepath"),
        "ICBNamePath": icb_master.get("icbnamepath"),
        "en_ICBName": row.get("en_icbname"),
        "en_ICBNamePath": row.get("en_icbname_path"),
        "VersionDateId": icb_master.get("versiondateid"),
    }
