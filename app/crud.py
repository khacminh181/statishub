from sqlalchemy.orm import Session
from app.models import OrganizationInformation


def get_company_by_taxcode(db: Session, taxcode: str):
    return (
        db.query(OrganizationInformation)
        .filter(
            OrganizationInformation.TaxCode == taxcode,
            OrganizationInformation.IsHistory == False,
            OrganizationInformation.RecordStatusId == 1
        )
        .first()
    )
