"""
Company data retrieval services.
"""

from app.core.exceptions import OrganizationNotFoundError
from app.database import supabase


def get_org_id_by_taxcode(taxcode: str) -> str:
    """
    Get organization ID by taxcode.

    Args:
        taxcode: The company taxcode

    Returns:
        The organization ID

    Raises:
        OrganizationNotFoundError: If organization is not found
    """
    res = (
        supabase.table("organization_information")
        .select("organizationid")
        .eq("taxcode", taxcode)
        .eq("ishistory", False)
        .single()
        .execute()
    )

    if not res.data:
        raise OrganizationNotFoundError(taxcode=taxcode)

    return res.data["organizationid"]
