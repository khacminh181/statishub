from pydantic import BaseModel, create_model, Field
from typing import Optional
from decimal import Decimal

class OrganizationInfo(BaseModel):
    BusinessTypeId: Optional[int] = Field(None, alias="businesstypeid")
    LocationId: Optional[int] = Field(None, alias="locationid")
    ActiveStatusId: Optional[int] = Field(None, alias="activestatusid")
    MainVSICId: Optional[int] = Field(None, alias="mainvsicid")
    IcbId: Optional[int] = Field(None, alias="icbid")
    CurrencyId: Optional[int] = Field(None, alias="currencyid")
    TaxCodeStatusId: Optional[int] = Field(None, alias="taxcodestatusid")

    RegisterDateId: Optional[str] = Field(None, alias="registerdateid")
    VersionDateId: Optional[str] = Field(None, alias="versiondateid")

    TaxCode: Optional[str] = Field(None, alias="taxcode")
    OrganizationName: Optional[str] = Field(None, alias="organizationname")
    OrganizationShortName: Optional[str] = Field(None, alias="organizationshortname")

    en_OrganizationName: Optional[str] = Field(None, alias="en_organizationname")
    en_OrganizationShortName: Optional[str] = Field(None, alias="en_organizationshortname")

    CharterCapital: Optional[Decimal] = Field(None, alias="chartercapital")
    Address: Optional[str] = Field(None, alias="address")
    en_Address: Optional[str] = Field(None, alias="en_address")

    Telephone: Optional[str] = Field(None, alias="telephone")
    Fax: Optional[str] = Field(None, alias="fax")
    Email: Optional[str] = Field(None, alias="email")
    Website: Optional[str] = Field(None, alias="website")
    LogoURL: Optional[str] = Field(None, alias="logourl")

    CurrentBusinessTypeId: Optional[int] = Field(None, alias="currentbusinesstypeid")

    class Config:
        allow_population_by_field_name = True


# Các field cố định
base_fields = {
    "taxcode": (str, ...),
    "periodid": (int, ...),
    "publicdateid": (str, ...),
    "reportformid": (int, ...),
    "reporttypeid": (int, ...),
}

# Sinh 322 chỉ tiêu BS1 -> BS322 (kiểu số)
bs_fields = {
    f"bs{i}": (Optional[Decimal], None)
    for i in range(1, 323)
}

# Gộp lại thành BalanceSheet
BalanceSheet = create_model(
    "BalanceSheet",
    **base_fields,
    **bs_fields
)

# Sinh 192 chỉ tiêu IS1 -> IS192 (kiểu số)
is_fields = {
    f"is{i}": (Optional[Decimal], None)
    for i in range(1, 193)
}

# Gộp lại thành IncomeStatement
IncomeStatement = create_model(
    "IncomeStatement",
    **base_fields,
    **is_fields
)

# Sinh 211 chỉ tiêu CF1 -> CF211 (kiểu số)
cf_fields = {
    f"cf{i}": (Optional[Decimal], None)
    for i in range(1, 212)
}

# Gộp lại thành IncomeStatement
CashFlow = create_model(
    "CashFlow",
    **base_fields,
    isdirect=(bool, ...),
    **cf_fields
)


class ShareHolder(BaseModel):
    organizationid: int
    taxcode: Optional[str] = None

    organizationname: Optional[str] = None
    organizationaddress: Optional[str] = None

    ownerorganizationid: Optional[int] = None
    ownercompanytaxcode: Optional[str] = None
    ownerorganizationname: Optional[str] = None
    ownerorganizationaddress: Optional[str] = None

    ownerpersonid: Optional[int] = None
    ownershiptypeid: Optional[int] = None

    publicdateid: Optional[str] = None
    currencyid: Optional[int] = None

    quantity: Optional[Decimal] = None
    percentage: Optional[Decimal] = None

    quantityadjusted: Optional[Decimal] = None
    percentageadjusted: Optional[Decimal] = None

    bookvalue: Optional[Decimal] = None
    marketvalue: Optional[Decimal] = None

    versiondateid: Optional[str] = None


class Structure(BaseModel):
    lefttaxcode: Optional[str]
    righttaxcode: Optional[str]

    leftroleid: Optional[int]
    rightroleid: Optional[int]

    versiondateid: Optional[str]


class Person(BaseModel):
    PersonId: int = Field(..., description="The Person identifier (internal use only)")
    PersonName: Optional[str] = Field(
        None, description="The Person’s name"
    )

    PositionId: Optional[int] = Field(
        None,
        description="The position identifier. The mapping of PositionId is stored in the Position master table"
    )

    en_PositionName: Optional[str] = Field(
        None, description="The position name"
    )

    class Config:
        allow_population_by_field_name = True


class InsuranceLiabilityResponse(BaseModel):
    TaxCode: str
    DepartmentOrganization: Optional[str]

    periodid: Optional[int]
    insurancetypeid: Optional[int]

    publicdateid: Optional[str]
    recorddateid: Optional[str]

    currencyid: Optional[int]

    monthowed: Optional[int]
    numberofemployee: Optional[int]

    totalvalue: Optional[Decimal]

    versiondateid: Optional[str]

    class Config:
        from_attributes = True

class TaxFeeLiabilityResponse(BaseModel):
    TaxCode: str
    DepartmentOrganization: Optional[str]

    periodid: Optional[int]

    taxfeetypeid: Optional[int]
    nationalbudgettypeid: Optional[int]

    taxfeeliabilitystatusid: Optional[int]
    enforcementtypeid: Optional[int]

    publicdateid: Optional[str]
    currencyid: Optional[int]

    totalvalue: Optional[Decimal]

    versiondateid: Optional[str]

    class Config:
        from_attributes = True