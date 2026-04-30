# Database Migrations

This directory contains database migration scripts for the Product Search Agent.

## Available Migrations

### 1. Add Query Optimization Fields
**File:** `add_query_optimization_fields.py`  
**Date:** 2026-04-26  
**Purpose:** Adds fields to support intelligent query refinement and optimization

**New Fields:**
- `query_version` (INTEGER): Tracks the number of query optimization iterations
- `query_history` (JSON/TEXT): Stores history of all query versions with performance metrics
- `optimization_enabled` (BOOLEAN): Flag to enable/disable automatic optimization

**Usage:**
```bash
# Apply migration
python backend/migrations/add_query_optimization_fields.py

# Rollback (see script for instructions)
python backend/migrations/add_query_optimization_fields.py --downgrade
```

## Migration Guidelines

### Before Running Migrations

1. **Backup your database:**
   ```bash
   cp backend/product_search.db backend/product_search.db.backup
   ```

2. **Test in development first:**
   - Never run migrations directly in production without testing
   - Verify the migration works with your data

3. **Check current schema:**
   ```bash
   sqlite3 backend/product_search.db ".schema search_requests"
   ```

### Running Migrations

**Development:**
```bash
# From project root
python backend/migrations/add_query_optimization_fields.py
```

**Production:**
```bash
# 1. Backup database
cp product_search.db product_search.db.backup

# 2. Run migration
python migrations/add_query_optimization_fields.py

# 3. Verify
sqlite3 product_search.db "PRAGMA table_info(search_requests);"
```

### Rollback

SQLite doesn't support `DROP COLUMN`, so rollback requires:
1. Create new table without the columns
2. Copy data from old table
3. Drop old table and rename new one

Or simply restore from backup:
```bash
cp product_search.db.backup product_search.db
```

## Migration History

| Date | Migration | Description |
|------|-----------|-------------|
| 2026-04-26 | add_query_optimization_fields | Added query_version, query_history, optimization_enabled |

## Future Migrations

When creating new migrations:

1. **Name format:** `YYYY-MM-DD_description.py`
2. **Include:**
   - Upgrade function
   - Downgrade function (if possible)
   - Documentation
   - Error handling

3. **Test thoroughly:**
   - Empty database
   - Database with existing data
   - Edge cases

## Troubleshooting

### Migration Already Applied
```
⚠️  Columns already exist. Skipping migration.
```
This is safe - the migration checks if columns exist before adding them.

### Migration Failed
```
❌ Migration failed: [error message]
```
1. Check the error message
2. Restore from backup
3. Fix the issue
4. Try again

### Column Type Mismatch
SQLite stores JSON as TEXT. This is normal and works correctly with SQLAlchemy's JSON type.

## Notes

- SQLite limitations: No `DROP COLUMN`, limited `ALTER TABLE` support
- Always backup before migrations
- Test migrations in development first
- Keep migration scripts for documentation