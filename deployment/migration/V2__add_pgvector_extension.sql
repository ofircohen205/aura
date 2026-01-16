-- Enable pgvector extension for vector similarity search
-- This extension is required for the RAG pipeline to store and query embeddings
CREATE EXTENSION IF NOT EXISTS vector;
