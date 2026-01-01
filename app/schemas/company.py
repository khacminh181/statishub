from pydantic import BaseModel
from typing import Optional
from datetime import date


class CompanyData(BaseModel):
    BusinessTypeId: Optional[int]
    LocationId: Optional[int]
    ActiveStatusId: Optional[int]
    MainVSICId: Optional[str]
    IcbId: Optional[str]
    CurrencyId: Optional[str]
    TaxCodeStatusId: Optional[int]
    RegisterDateId: Optional[date]

    TaxCode: str

    OrganizationName: Optional[str] = None
    OrganizationShortName: Optional[str] = None
    en_OrganizationName: Optional[str] = None
    en_OrganizationShortName: Optional[str] = None

    CharterCapital: Optional[int]
    Address: Optional[str] = None
    en_Address: Optional[str] = None

    Telephone: Optional[str]
    Fax: Optional[str]
    Email: Optional[str]
    Website: Optional[str]
    LogoURL: Optional[str]

    CurrentBusinessTypeId: Optional[int]
    VersionDateId: Optional[date]


class CompanyMeta(BaseModel):
    taxcode: str
    language: str


class CompanyResponse(BaseModel):
    meta: CompanyMeta
    data: CompanyData
