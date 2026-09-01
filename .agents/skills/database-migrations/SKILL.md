---
name: database-migrations
description: Database migration best practices for schema changes, data migrations, rollbacks, and zero-downtime deployments across PostgreSQL, MySQL, and common ORMs. Use when writing a schema or data migration, planning a rollback, or aiming for zero-downtime deployment.
metadata:
  origin: ECC
---

# Database Migration Patterns

Safe, reversible database schema changes for production systems.

## Core Principles

1. **Every change is a migration** — never alter production databases manually
2. **Migrations are forward-only in production** — rollbacks use new forward migrations
3. **Schema and data migrations are separate** — never mix DDL and DML in one migration
4. **Test migrations against production-sized data**
5. **Migrations are immutable once deployed**

## Migration Safety Checklist

- [ ] Migration has both UP and DOWN
- [ ] No full table locks on large tables
- [ ] New columns have defaults or are nullable
- [ ] Indexes created concurrently
- [ ] Data backfill is a separate migration
- [ ] Rollback plan documented

## PostgreSQL Patterns

### Adding a Column Safely
```sql
-- GOOD: Nullable column, no lock
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- GOOD: Column with default (Postgres 11+ is instant)
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- BAD: NOT NULL without default on existing table
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
```

### Adding an Index Without Downtime
```sql
-- GOOD: Non-blocking
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);
```

### Zero-Downtime Column Rename (Expand-Contract)
```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN display_name TEXT;
-- Step 2: Backfill data
UPDATE users SET display_name = username WHERE display_name IS NULL;
-- Step 3: Update app code to read/write both columns
-- Step 4: Drop old column
ALTER TABLE users DROP COLUMN username;
```

### Large Data Migrations (Batched)
```sql
DO $$
DECLARE batch_size INT := 10000; rows_updated INT;
BEGIN
  LOOP
    UPDATE users SET normalized_email = LOWER(email)
    WHERE id IN (
      SELECT id FROM users WHERE normalized_email IS NULL
      LIMIT batch_size FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    EXIT WHEN rows_updated = 0;
    COMMIT;
  END LOOP;
END $$;
```

## Alembic (Python/SQLAlchemy)

```bash
alembic revision --autogenerate -m "add_user_avatar"
alembic upgrade head
alembic downgrade -1
alembic history
```

## Anti-Patterns

| Anti-Pattern | Better Approach |
|-------------|-----------------|
| Manual SQL in production | Always use migration files |
| Editing deployed migrations | Create new migration instead |
| NOT NULL without default | Add nullable, backfill, then add constraint |
| Inline index on large table | CREATE INDEX CONCURRENTLY |
| Schema + data in one migration | Separate migrations |
