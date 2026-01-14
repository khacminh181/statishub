"""
Input validation utilities for API endpoints.
"""

import re

from fastapi import HTTPException

TAXCODE_PATTERN = re.compile(r"^[0-9]{10,14}(-[0-9]{3})?$")


def validate_taxcode(taxcode: str) -> str:
    """
    Validate Vietnamese taxcode format.

    Valid formats:
    - 10-14 digits (main company): 0123456789, 01234567890123
    - With branch suffix: 0123456789-001

    Args:
        taxcode: The taxcode to validate

    Returns:
        The validated taxcode

    Raises:
        HTTPException: If taxcode format is invalid
    """
    if not TAXCODE_PATTERN.match(taxcode):
        raise HTTPException(
            status_code=400,
            detail="Invalid taxcode format. Expected 10-14 digits, optionally followed by -XXX branch code",
        )
    return taxcode
