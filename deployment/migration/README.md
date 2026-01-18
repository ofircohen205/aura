# Database Migrations

This directory contains SQL migration scripts for the Aura database.

## Migration Files

- `V3__create_users_tables.sql` - Creates users table for authentication
- `V3__create_users_tables_ROLLBACK.sql` - Rollback script for V3 migration

## Migration Naming Convention

Migrations follow the pattern: `V{version}__{description}.sql`

- Version numbers are sequential integers
- Descriptions are snake_case

## Running Migrations

### Using Flyway (if configured)

```bash
flyway migrate
```

### Manual Execution

```bash
psql -U aura -d aura_db -f V3__create_users_tables.sql
```

## Rollback Procedures

### V3 Migration Rollback

To rollback the V3 migration (removes users table):

```bash
psql -U aura -d aura_db -f V3__create_users_tables_ROLLBACK.sql
```

**WARNING**: Rollback scripts will delete data. Always backup before rolling back.

## Migration Best Practices

1. **Always test migrations** in a development environment first
2. **Backup database** before running migrations in production
3. **Review rollback scripts** to understand data loss implications
4. **Test rollback procedures** in development before production use
5. **Document breaking changes** in migration comments
6. **Use transactions** where possible for atomic migrations

## Index Strategy

- **Single column indexes**: Created for frequently queried columns (email, username)
- **Composite indexes**: Created for common query patterns (email + is_active, is_active + created_at)
- **Unique indexes**: Enforce data integrity (email, username)

## Future Migrations

When creating new migrations:

1. Increment version number
2. Include rollback script
3. Document any breaking changes
4. Test in development first
5. Update this README
