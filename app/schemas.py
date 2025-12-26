from pydantic import BaseModel
from typing import Optional
from datetime import date


class CompanyResponse(BaseModel):
    BusinessTypeId: Optional[int]
    LocationId: Optional[int]
    ActiveStatusId: Optional[int]
    MainVSICId: Optional[int]
    IcbId: Optional[int]
    CurrencyId: Optional[int]
    TaxCodeStatusId: Optional[int]
    RegisterDateId: Optional[date]

    TaxCode: str
    OrganizationName: Optional[str]
    OrganizationShortName: Optional[str]
    CharterCapital: Optional[int]
    Address: Optional[str]
    Telephone: Optional[str]
    Fax: Optional[str]
    Email: Optional[str]
    Website: Optional[str]
    LogoURL: Optional[str]

    en_OrganizationName: Optional[str]
    en_OrganizationShortName: Optional[str]
    en_Address: Optional[str]

    CurrentBusinessTypeId: Optional[int]
    VersionDateId: Optional[date]

    class Config:
        from_attributes = True
