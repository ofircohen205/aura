# Database Connection Guide

## TablePlus Connection Parameters

To connect to the Aura PostgreSQL database using TablePlus:

### Connection Details

- **Host**: `localhost`
- **Port**: `5432`
- **User**: `aura` (default, can be overridden with `POSTGRES_USER` env var)
- **Password**: `aura` (default, can be overridden with `POSTGRES_PASSWORD` env var)
- **Database**: `aura_db` (default, can be overridden with `POSTGRES_DB` env var)

### Connection String Format

```
postgresql://aura:aura@localhost:5432/aura_db
```

### TablePlus Setup Steps

1. Open TablePlus
2. Click "Create a new connection"
3. Select "PostgreSQL"
4. Enter the connection details above
5. Click "Test" to verify connection
6. Click "Connect"

## Vector Store Tables

The RAG system uses pgvector with the following tables:

### `langchain_pg_collection`

Stores collection metadata:

- `uuid`: Primary key (UUID)
- `name`: Collection name (e.g., "aura_knowledge_base")
- `cmetadata`: JSONB column for collection metadata

### `langchain_pg_embedding`

Stores document chunks and embeddings:

- `id`: Primary key (UUID)
- `collection_id`: Foreign key to `langchain_pg_collection.uuid`
- `embedding`: Vector embedding (vector type, dimension depends on model)
- `document`: Text content of the chunk
- `cmetadata`: JSONB column for document metadata (includes: source, language, difficulty, keywords, etc.)
- `custom_id`: Optional custom identifier

## Querying Vectors

### View All Collections

```sql
SELECT * FROM langchain_pg_collection;
```

### View All Embeddings in a Collection

```sql
SELECT
    id,
    document,
    cmetadata->>'source' as source,
    cmetadata->>'language' as language,
    cmetadata->>'difficulty' as difficulty,
    cmetadata->>'title' as title,
    LENGTH(document) as content_length
FROM langchain_pg_embedding
WHERE collection_id = (
    SELECT uuid FROM langchain_pg_collection WHERE name = 'aura_knowledge_base'
)
ORDER BY cmetadata->>'source';
```

### Count Documents by Language

```sql
SELECT
    cmetadata->>'language' as language,
    COUNT(*) as count
FROM langchain_pg_embedding
WHERE collection_id = (
    SELECT uuid FROM langchain_pg_collection WHERE name = 'aura_knowledge_base'
)
GROUP BY cmetadata->>'language';
```

### Search by Similarity (Vector Search)

```sql
-- First, you need to create an embedding of your query
-- This requires using the embedding model, typically done via the API
-- But you can view similar vectors if you have a reference embedding

-- Example: Find similar documents (requires embedding vector)
SELECT
    document,
    cmetadata->>'source' as source,
    cmetadata->>'title' as title,
    embedding <-> '[your_query_embedding_vector]' as distance
FROM langchain_pg_embedding
WHERE collection_id = (
    SELECT uuid FROM langchain_pg_collection WHERE name = 'aura_knowledge_base'
)
ORDER BY distance
LIMIT 10;
```

### Filter by Metadata

```sql
-- Find all Python beginner lessons
SELECT
    document,
    cmetadata->>'title' as title,
    cmetadata->>'source' as source
FROM langchain_pg_embedding
WHERE collection_id = (
    SELECT uuid FROM langchain_pg_collection WHERE name = 'aura_knowledge_base'
)
AND cmetadata->>'language' = 'python'
AND cmetadata->>'difficulty' = 'beginner';
```

### View Lesson Statistics

```sql
SELECT
    cmetadata->>'language' as language,
    cmetadata->>'difficulty' as difficulty,
    COUNT(*) as chunk_count,
    COUNT(DISTINCT cmetadata->>'source') as lesson_count
FROM langchain_pg_embedding
WHERE collection_id = (
    SELECT uuid FROM langchain_pg_collection WHERE name = 'aura_knowledge_base'
)
GROUP BY cmetadata->>'language', cmetadata->>'difficulty'
ORDER BY language, difficulty;
```

## Notes

- The `embedding` column uses the `vector` data type from the pgvector extension
- Vector dimension depends on the embedding model (e.g., 1536 for `text-embedding-3-small`)
- For similarity search, use the `<->` operator (L2 distance) or `<#>` operator (cosine distance)
- Metadata is stored as JSONB, so use `->` or `->>` operators to access nested values
