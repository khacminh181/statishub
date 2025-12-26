from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    BigInteger,
    String,
    Date,
    Boolean
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrganizationInformation(Base):
    __tablename__ = "FGFB_COIN_DR_OrganizationInformation"

    # ====== IDs ======
    RecordId = Column(Integer, primary_key=True)
    OrganizationId = Column(Integer)
    BusinessTypeId = Column(SmallInteger)
    LocationId = Column(Integer)
    ActiveStatusId = Column(SmallInteger)
    MainVSICId = Column(SmallInteger)
    GICSId = Column(SmallInteger)
    IcbId = Column(SmallInteger)
    SourceOrganizationId = Column(Integer)
    CurrencyId = Column(SmallInteger)
    TaxCodeStatusId = Column(SmallInteger)

    # ====== Dates ======
    RegisterDateId = Column(Date)
    EffectiveDateId = Column(Date)
    VersionDateId = Column(Date)

    # ====== Codes ======
    TaxCode = Column(String(14), index=True)
    EnterpriseCode = Column(String(30))
    FiinGroupId = Column(String(14))

    # ====== Names ======
    OrganizationName = Column(String(255))
    OrganizationShortName = Column(String(128))
    en_OrganizationName = Column(String(255))
    en_OrganizationShortName = Column(String(128))

    # ====== Financial ======
    CharterCapital = Column(BigInteger)

    # ====== Contact ======
    Address = Column(String(255))
    en_Address = Column(String(255))
    Telephone = Column(String(30))
    Fax = Column(String(30))
    Email = Column(String(50))
    Website = Column(String(128))
    LogoURL = Column(String(128))

    # ====== Audit ======
    ModificationId = Column(BigInteger)
    RecordStatusId = Column(SmallInteger)
    IsHistory = Column(Boolean)
    CurrentBusinessTypeId = Column(SmallInteger)
