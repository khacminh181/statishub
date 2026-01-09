"""
Application constants and lookup tables.
"""

# Mapping of API parameter names to database table names for compliance data
COMPLIANCE_TABLE_MAP = {
    "insuranceliability": "insurance_liability",
    "taxfeeliability": "tax_fee_liability",
}

# Mapping of API parameter names to database table names for industry classification
INDUSTRY_TABLE_MAP = {
    "companyvsic": "organization_vsic",
    "companyicb": "organization_icb",
}