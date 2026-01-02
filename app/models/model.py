from pydantic import BaseModel, create_model
from typing import Optional
from decimal import Decimal

class OrganizationInfo(BaseModel):
    BusinessTypeId: Optional[int]
    LocationId: Optional[int]
    ActiveStatusId: Optional[int]
    MainVSICId: Optional[int]
    IcbId: Optional[int]
    CurrencyId: Optional[int]
    TaxCodeStatusId: Optional[int]

    RegisterDateId: Optional[int]
    VersionDateId: Optional[int]

    TaxCode: str
    OrganizationName: str
    OrganizationShortName: Optional[str]

    en_OrganizationName: Optional[str]
    en_OrganizationShortName: Optional[str]

    CharterCapital: Optional[float]

    Address: Optional[str]
    en_Address: Optional[str]

    Telephone: Optional[str]
    Fax: Optional[str]
    Email: Optional[str]
    Website: Optional[str]

    LogoURL: Optional[str]

    CurrentBusinessTypeId: Optional[int]

    class Config:
        from_attributes = True


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