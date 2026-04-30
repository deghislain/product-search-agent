# Database Migration Summary: Query Optimization Fields

## Overview
This migration adds support for the **Intelligent Query Refinement** feature from the Agentic Upgrade Plan (Phase 1.1).

## Changes Made

### 1. Model Changes (`backend/app/models/search_request.py`)

Added three new columns to the `SearchRequest` model:

```python
# Query Optimization Fields
query_version = Column(
    Integer,
    nullable=False,
    default=0,
    comment="Track query iterations for optimization"
)

query_history = Column(
    JSON,
    nullable=True,
    default=list,
    comment="Store all query versions with timestamps and performance metrics"
)

optimization_enabled = Column(
    Boolean,
    nullable=False,
    default=True,
    comment="Enable/disable automatic query optimization"
)
```

### 2. Schema Changes (`backend/app/schemas/search_request.py`)

Updated Pydantic schemas to include new fields:

**SearchRequestBase:**
- Added `optimization_enabled: bool = True`

**SearchRequestUpdate:**
- Added `optimization_enabled: Optional[bool] = None`

**SearchRequestResponse:**
- Added `query_version: int = 0`
- Added `query_history: Optional[List[Dict[str, Any]]] = None`

### 3. Migration Scripts

Created migration scripts in `backend/migrations/`:
- `add_query_optimization_fields.py` - Python migration script
- `add_query_optimization_fields.sql` - SQL migration script (for PostgreSQL)
- `README.md` - Migration documentation

## Field Descriptions

### query_version (INTEGER)
- **Purpose:** Tracks how many times a query has been optimized
- **Default:** 0
- **Usage:** Incremented each time the QueryOptimizer refines the search query
- **Example:** 
  - Version 0: "Toyota Camry"
  - Version 1: "Toyota Camry 2015-2018 LE SE"
  - Version 2: "Toyota Camry 2015-2018 LE SE under 100k miles"

### query_history (JSON/TEXT)
- **Purpose:** Stores the complete history of query optimizations
- **Default:** NULL (empty)
- **Format:** Array of objects with query details
- **Example:**
```json
[
  {
    "version": 0,
    "query": "Toyota Camry",
    "timestamp": "2026-04-26T10:00:00Z",
    "results_count": 150,
    "avg_match_score": 65.5
  },
  {
    "version": 1,
    "query": "Toyota Camry 2015-2018 LE SE",
    "timestamp": "2026-04-26T12:00:00Z",
    "results_count": 45,
    "avg_match_score": 82.3,
    "optimization_reason": "Added year range and trim levels based on user clicks"
  }
]
```

### optimization_enabled (BOOLEAN)
- **Purpose:** Flag to enable/disable automatic query optimization
- **Default:** TRUE
- **Usage:** Users can disable optimization if they want to keep their original query
- **Example:** Set to FALSE if user wants exact query matching only

## How It Works

1. **Initial Search:**
   - User creates search: "Toyota Camry"
   - `query_version = 0`
   - `query_history = []`
   - `optimization_enabled = true`

2. **After First Search:**
   - System collects results and user feedback
   - QueryOptimizer analyzes patterns
   - Suggests improved query: "Toyota Camry 2015-2018"

3. **Query Update:**
   - `query_version = 1`
   - Original query added to `query_history`
   - New optimized query becomes active

4. **Continuous Learning:**
   - Each optimization iteration is tracked
   - History shows evolution of query refinement
   - Users can see why queries were optimized

## Integration with QueryOptimizer

The QueryOptimizer (from `backend/app/core/query_optimizer.py`) uses these fields:

```python
async def optimize_query(self, search_request: SearchRequest):
    # Get current query and history
    current_query = search_request.product_name
    history = search_request.query_history or []
    
    # Analyze and optimize
    optimized_query = await self.llm.generate_optimization(
        current_query, 
        history
    )
    
    # Update search request
    history.append({
        "version": search_request.query_version,
        "query": current_query,
        "timestamp": datetime.utcnow().isoformat(),
        "results_count": len(previous_results),
        "avg_match_score": calculate_avg_score(previous_results)
    })
    
    search_request.product_name = optimized_query
    search_request.query_version += 1
    search_request.query_history = history
```

## Running the Migration

### Development (SQLite)
```bash
# Backup database
cp backend/product_search.db backend/product_search.db.backup

# Run migration
python backend/migrations/add_query_optimization_fields.py

# Verify
sqlite3 backend/product_search.db "PRAGMA table_info(search_requests);"
```

### Production (PostgreSQL)
```bash
# Backup database
pg_dump -U user -d product_search > backup.sql

# Run migration
psql -U user -d product_search -f backend/migrations/add_query_optimization_fields.sql

# Verify
psql -U user -d product_search -c "\d search_requests"
```

## Rollback

If you need to rollback:

**SQLite:**
```bash
# Restore from backup
cp backend/product_search.db.backup backend/product_search.db
```

**PostgreSQL:**
```sql
ALTER TABLE search_requests DROP COLUMN query_version;
ALTER TABLE search_requests DROP COLUMN query_history;
ALTER TABLE search_requests DROP COLUMN optimization_enabled;
```

## Testing

After migration, test:

1. **Create new search request:**
   ```python
   search = SearchRequest(
       product_name="iPhone 13",
       product_description="Good condition",
       budget=600.0
   )
   # Should have query_version=0, optimization_enabled=True
   ```

2. **Update existing search:**
   ```python
   search.query_version = 1
   search.query_history = [{"version": 0, "query": "iPhone 13"}]
   db.commit()
   ```

3. **Verify API response:**
   ```bash
   curl http://localhost:8000/api/search-requests/{id}
   # Should include query_version and query_history fields
   ```

## Next Steps

After this migration:

1. ✅ Database schema updated
2. ✅ Models and schemas updated
3. ⏳ Implement QueryOptimizer logic (see `docs/AGENTIC_UPGRADE_PLAN.md`)
4. ⏳ Add API endpoint for manual optimization
5. ⏳ Integrate with search execution flow
6. ⏳ Add frontend UI for query history

## Related Files

- `backend/app/models/search_request.py` - Model definition
- `backend/app/schemas/search_request.py` - Pydantic schemas
- `backend/app/core/query_optimizer.py` - Query optimization logic
- `docs/AGENTIC_UPGRADE_PLAN.md` - Full agentic upgrade plan

## Questions?

See `backend/migrations/README.md` for general migration guidelines.