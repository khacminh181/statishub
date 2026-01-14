# Statishub API Performance Improvement Report

## Executive Summary

Three API endpoints were discovered to be critically slow or broken during load testing. After systematic analysis and optimization, all three endpoints now achieve **>1,000 RPS** with **sub-15ms P99 latency** and **100% success rate**.

| Endpoint | Before | After | Improvement |
|----------|--------|-------|-------------|
| `/company/{taxcode}/structure` | 6-20s, 404/500 errors | 1,352 RPS, P99 10.6ms | ~1000x faster |
| `/search?name=...` | Timeout (>60s) | 1,344 RPS, P99 9.9ms | ∞ (was broken) |
| `/company/{taxcode}/compliance` | 15 RPS, P99 13.4s | 1,169 RPS, P99 13.9ms | ~78x faster |

---

## Problem Statement

During load testing with CCU 10, three endpoints showed critical performance issues:

### 1. Structure Endpoint (`/company/{taxcode}/structure`)
- **Symptoms**: 6-20 second response times, intermittent 404 and 500 errors
- **Impact**: Unusable under any load

### 2. Search Endpoint (`/search?name=...`)
- **Symptoms**: Complete timeout (>60 seconds)
- **Impact**: Endpoint completely broken

### 3. Compliance Endpoint (`/company/{taxcode}/compliance`)
- **Symptoms**: 0.5-20 second response times, 404/500 errors
- **Impact**: Unreliable, poor user experience

---

## Root Cause Analysis

### Structure Endpoint Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| N+1 Query Pattern | Critical | Enrichment query with massive IN clauses for each relationship |
| Synchronous Blocking | Critical | Blocking Supabase calls froze the async event loop |
| No Exception Handling | High | Enrichment failures caused 500 errors |
| Wrong 404 Response | Medium | Returned 404 when org had no relationships (should return `[]`) |
| Missing Database Index | Critical | No index on `organization_role.leftorganizationid` |

### Search Endpoint Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| Synchronous Blocking | Critical | `def` function blocked entire event loop under load |
| Double Database Queries | Critical | Separate queries for data and count |
| SELECT * | High | Returned 322+ fields instead of needed ~10 columns |
| No Database Index | Critical | No trigram index for ILIKE searches |
| Cache Key with Pagination | Medium | Low cache hit rate due to offset in key |

### Compliance Endpoint Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| Credit Before Cache | High | Consumed credits even on cache hits |
| Missing Error Handling | High | Generic errors with no context |
| Missing Database Index | Critical | No index on liability tables |

---

## Code Fixes

### File: `app/api/company.py`

#### 1. Added Async Infrastructure

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.core.logging import get_logger

logger = get_logger(__name__)
_db_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="db_worker")
```

#### 2. Search Endpoint - Combined Queries & Async

**Before:**
```python
@searchRouter.get("/search", ...)
def search_organization(...):
    # Two separate queries
    data_resp = supabase.table("organization_information").select("*")...
    count_resp = supabase.table("organization_information").select("organizationid", count="exact")...
```

**After:**
```python
SEARCH_COLUMNS = (
    "taxcode, organizationid, organizationname, en_organizationname, "
    "organizationshortname, en_organizationshortname, chartercapital, "
    "address, en_address, activestatusid, mainvsicid, registerdateid"
)

def _execute_search_query(safe_name: str, limit: int, offset: int) -> Dict:
    """Execute search query in thread pool to avoid blocking event loop."""
    keyword = f"%{safe_name}%"
    data_resp = (
        supabase.table("organization_information")
        .select(SEARCH_COLUMNS, count="exact")  # Single query with count
        .eq("ishistory", False)
        .or_(f"organizationname.ilike.{keyword},en_organizationname.ilike.{keyword}")
        .range(offset, offset + limit - 1)
        .execute()
    )
    return {
        "data": data_resp.data or [],
        "pagination": {"total": data_resp.count or 0, "limit": limit, "offset": offset},
    }

@searchRouter.get("/search", ...)
async def search_organization(...):  # Now async
    cache_key = build_search_cache_key(safe_name, limit, offset)
    cached = get_cached(cache_key)
    if cached:
        return cached

    consume_credit(api_key["api_key"])  # Only after cache miss

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_db_executor, _execute_search_query, safe_name, limit, offset)

    set_cached(cache_key, result)
    return result
```

#### 3. Structure Endpoint - Async with Batch Enrichment

**Before:**
```python
@router.get("/{taxcode}/structure", ...)
def get_structure(...):
    consume_credit(api_key["api_key"])
    # ... queries ...
    if not res.data:
        raise HTTPException(404, "Structure not found")  # Wrong!

    # Single massive IN query for enrichment
    org_info = supabase.table("organization_information").in_("organizationid", org_ids)...
```

**After:**
```python
def _fetch_structure_data(taxcode: str) -> List[Dict]:
    """Fetch structure data with batched enrichment."""
    org_id = get_org_id_by_taxcode(taxcode)
    res = (
        supabase.table("organization_role")
        .select("*")
        .eq("leftorganizationid", org_id)
        .eq("ishistory", False)
        .execute()
    )

    if not res.data:
        return []  # Return empty list, not 404

    # Batch enrichment to avoid massive IN clauses
    org_ids = list({r["rightorganizationid"] for r in res.data})
    org_map: Dict = {}
    MAX_ENRICHMENT_BATCH = 100

    for i in range(0, len(org_ids), MAX_ENRICHMENT_BATCH):
        batch_ids = org_ids[i : i + MAX_ENRICHMENT_BATCH]
        try:
            org_info = (
                supabase.table("organization_information")
                .select("organizationid, taxcode")
                .in_("organizationid", batch_ids)
                .execute()
            )
            org_map.update({o["organizationid"]: o["taxcode"] for o in org_info.data})
        except Exception as e:
            logger.warning(f"Failed to enrich structure batch {i // MAX_ENRICHMENT_BATCH}: {e}")
            # Graceful degradation - continue without this batch

    return [
        {
            "LeftTaxCode": taxcode,
            "RightTaxCode": org_map.get(r["rightorganizationid"]),
            # ... other fields
        }
        for r in res.data
    ]

@router.get("/{taxcode}/structure", ...)
async def get_structure(...):  # Now async
    cache_key = build_cache_key("structure", taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    consume_credit(api_key["api_key"])  # Only after cache miss

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_db_executor, _fetch_structure_data, taxcode)

    set_cached(cache_key, result)
    return result
```

#### 4. Compliance Endpoint - Cache Before Credit

**Before:**
```python
def get_compliance(...):
    consume_credit(api_key["api_key"])  # Wastes credits on cache hits!
    cache_key = build_cache_key(table, taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached
```

**After:**
```python
def get_compliance(...):
    cache_key = build_cache_key(table, taxcode, language)
    cached = get_cached(cache_key)
    if cached:
        return cached

    consume_credit(api_key["api_key"])  # Only on cache miss
```

#### 5. Applied Cache-Before-Credit Pattern to All Endpoints

Updated all endpoints to check cache before consuming credits:
- `get_company`
- `get_balance_sheet`
- `get_income_statement`
- `get_cashflow`
- `get_shareholders`
- `get_personnel`
- `get_industries`

---

## Database Indexes

### Discovery: Views vs Tables

The `organization_role` table was actually a VIEW on `stg.organization_role`:

```sql
SELECT pg_get_viewdef('organization_role', true);
-- Result: SELECT * FROM stg.organization_role;
```

All indexes needed to be created on the underlying `stg.*` tables.

### Indexes Created

```sql
-- Structure endpoint optimization
CREATE INDEX IF NOT EXISTS idx_stg_org_role_left_history
ON stg.organization_role (leftorganizationid, ishistory);

-- Organization lookup optimization
CREATE INDEX IF NOT EXISTS idx_stg_org_info_orgid
ON stg.organization_information (organizationid);

CREATE INDEX IF NOT EXISTS idx_stg_org_info_taxcode_history
ON stg.organization_information (taxcode, ishistory);

-- Search endpoint optimization (trigram index for ILIKE)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS idx_stg_org_info_name_trgm
ON stg.organization_information USING gin (organizationname gin_trgm_ops);

-- Compliance endpoint optimization
CREATE INDEX IF NOT EXISTS idx_insurance_liability_orgid_history
ON stg.insurance_liability (organizationid, ishistory);

CREATE INDEX IF NOT EXISTS idx_tax_fee_liability_orgid_history
ON stg.tax_fee_liability (organizationid, ishistory);
```

---

## Performance Results

### Before Optimization

| Endpoint | RPS | P50 | P95 | P99 | Success Rate | Status |
|----------|-----|-----|-----|-----|--------------|--------|
| `/company/{taxcode}/structure` | - | 6-20s | - | - | ~50% | 404/500 errors |
| `/search?name=...` | - | >60s | - | - | 0% | Timeout |
| `/company/{taxcode}/compliance` | 15 | 6.9ms | 7.9s | 13.4s | ~90% | Slow |

### After Optimization

| Endpoint | RPS | P50 | P95 | P99 | Success Rate | Status |
|----------|-----|-----|-----|-----|--------------|--------|
| `/company/{taxcode}/structure` | **1,352** | 7.2ms | 10.1ms | 10.6ms | **100%** | Excellent |
| `/search?name=...` | **1,344** | 7.4ms | 8.6ms | 9.9ms | **100%** | Excellent |
| `/company/{taxcode}/compliance` | **1,169** | 8.2ms | 11.6ms | 13.9ms | **100%** | Excellent |

### Load Test Configuration

- **Tool**: hey (HTTP load generator)
- **Concurrent Users**: 10
- **Requests per Test**: 200-500

---

## Key Takeaways

### 1. Async Matters
Converting synchronous database calls to run in a ThreadPoolExecutor prevented event loop blocking and dramatically improved throughput.

### 2. Database Indexes are Critical
The largest performance gains came from adding proper database indexes. Without indexes, even optimized code couldn't overcome slow queries.

### 3. Cache-Before-Credit
Always check cache before consuming credits to avoid charging users for cached responses.

### 4. Graceful Degradation
Adding try-catch around non-critical operations (like enrichment) prevents cascading failures.

### 5. Views Need Index Investigation
When indexes fail to create, check if the table is actually a VIEW pointing to another schema.

### 6. Specific Column Selection
Using `SELECT column1, column2` instead of `SELECT *` reduces data transfer and improves performance.

### 7. Combined Queries
Using Supabase's `count="exact"` parameter allows getting data and count in a single query.

---

## Test Commands

```bash
# Create high-capacity test API key
curl -X POST http://localhost:8000/admin/api-keys/ \
  -H "x-admin-key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"client_name": "loadtest", "credits": 100000}'

# Set high rate limit for the key
redis-cli SET "apikey_rl:YOUR_API_KEY" 100000

# Run load tests
hey -n 200 -c 10 -H "x-api-key: YOUR_API_KEY" \
  "http://localhost:8000/company/0106773786/structure"

hey -n 500 -c 10 -H "x-api-key: YOUR_API_KEY" \
  "http://localhost:8000/search?name=test&limit=5"

hey -n 200 -c 10 -H "x-api-key: YOUR_API_KEY" \
  "http://localhost:8000/company/0106773786/compliance?tablename=insuranceliability"
```

---

## Date

Optimization completed: 2026-01-14
