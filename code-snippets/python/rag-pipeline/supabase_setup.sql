-- ============================================================
-- QueryLex RAG Pipeline - Complete Supabase Setup
-- ============================================================
-- Run this entire file in your Supabase SQL Editor:
--   1. Go to https://supabase.com/dashboard
--   2. Select your project
--   3. Go to SQL Editor (left sidebar)
--   4. Paste this entire file
--   5. Click "Run"
-- ============================================================


-- Step 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;


-- Step 2: Create the collections table
-- Stores dataset/collection metadata and retrieval settings
CREATE TABLE IF NOT EXISTS collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    user_id UUID,
    metadata JSONB DEFAULT '{}',
    retrieval_settings JSONB DEFAULT '{
        "search_mode": "hybrid",
        "reranking_enabled": true,
        "legal_tokenization": true,
        "sac_enabled": false,
        "hyde_enabled": false,
        "query_decomposition_enabled": false,
        "agentic_enabled": false,
        "colbert_enabled": false
    }',
    created_at TIMESTAMPTZ DEFAULT now()
);


-- Step 3: Create the documents table
-- Stores document chunks with embeddings in multiple dimension columns
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding_1536 vector(1536),        -- OpenAI text-embedding-3-small
    embedding_1024 vector(1024),        -- Cohere embed-v3, Voyage, Qwen3
    embedding_1792 vector(1792),        -- Isaacus Kanon 2
    sentence_embeddings JSONB,          -- ColBERT sentence-level embeddings
    sentence_texts JSONB,               -- ColBERT sentence texts
    created_at TIMESTAMPTZ DEFAULT now()
);


-- Step 4: Create indexes for fast vector search
-- Only create indexes for dimensions you plan to use.
-- ivfflat is good for most use cases. Increase 'lists' for larger datasets.
CREATE INDEX IF NOT EXISTS idx_documents_embedding_1536
    ON documents USING ivfflat (embedding_1536 vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_documents_embedding_1024
    ON documents USING ivfflat (embedding_1024 vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_documents_embedding_1792
    ON documents USING ivfflat (embedding_1792 vector_cosine_ops) WITH (lists = 100);

-- Standard indexes for filtering
CREATE INDEX IF NOT EXISTS idx_documents_collection_id
    ON documents (collection_id);

-- Full-text search index on content (for hybrid search)
CREATE INDEX IF NOT EXISTS idx_documents_content_fts
    ON documents USING gin (to_tsvector('english', content));


-- ============================================================
-- Step 5: Similarity search RPC functions
-- One per embedding dimension (1536, 1024, 1792)
-- ============================================================

-- 1536 dimensions (OpenAI text-embedding-3-small)
CREATE OR REPLACE FUNCTION match_documents_1536(
    collection_id UUID,
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.0,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        (1 - (d.embedding_1536 <=> query_embedding))::FLOAT AS similarity
    FROM documents d
    WHERE d.collection_id = match_documents_1536.collection_id
      AND d.embedding_1536 IS NOT NULL
      AND (1 - (d.embedding_1536 <=> query_embedding)) > match_threshold
    ORDER BY d.embedding_1536 <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 1024 dimensions (Cohere, Voyage, Qwen3)
CREATE OR REPLACE FUNCTION match_documents_1024(
    collection_id UUID,
    query_embedding vector(1024),
    match_threshold FLOAT DEFAULT 0.0,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        (1 - (d.embedding_1024 <=> query_embedding))::FLOAT AS similarity
    FROM documents d
    WHERE d.collection_id = match_documents_1024.collection_id
      AND d.embedding_1024 IS NOT NULL
      AND (1 - (d.embedding_1024 <=> query_embedding)) > match_threshold
    ORDER BY d.embedding_1024 <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 1792 dimensions (Isaacus Kanon 2)
CREATE OR REPLACE FUNCTION match_documents_1792(
    collection_id UUID,
    query_embedding vector(1792),
    match_threshold FLOAT DEFAULT 0.0,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        (1 - (d.embedding_1792 <=> query_embedding))::FLOAT AS similarity
    FROM documents d
    WHERE d.collection_id = match_documents_1792.collection_id
      AND d.embedding_1792 IS NOT NULL
      AND (1 - (d.embedding_1792 <=> query_embedding)) > match_threshold
    ORDER BY d.embedding_1792 <=> query_embedding
    LIMIT match_count;
END;
$$;


-- ============================================================
-- Step 6: Filtered similarity search RPC functions
-- Used for legal source filtering (search across multiple
-- collections with metadata conditions).
-- ============================================================

-- 1536 filtered
CREATE OR REPLACE FUNCTION match_documents_1536_filtered(
    p_collection_ids UUID[],
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.0,
    match_count INT DEFAULT 10,
    filter_conditions JSONB DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        (1 - (d.embedding_1536 <=> query_embedding))::FLOAT AS similarity
    FROM documents d
    WHERE d.collection_id = ANY(p_collection_ids)
      AND d.embedding_1536 IS NOT NULL
      AND (1 - (d.embedding_1536 <=> query_embedding)) > match_threshold
      AND (
          filter_conditions IS NULL
          OR EXISTS (
              SELECT 1 FROM jsonb_array_elements(filter_conditions) AS fc
              WHERE (fc->>'source_api' IS NULL OR d.metadata->>'source_api' = fc->>'source_api')
                AND (fc->>'doc_type' IS NULL OR d.metadata->>'doc_type' = fc->>'doc_type')
                AND (fc->>'jurisdiction_detail' IS NULL OR d.metadata->>'jurisdiction_detail' = fc->>'jurisdiction_detail')
          )
      )
    ORDER BY d.embedding_1536 <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 1024 filtered
CREATE OR REPLACE FUNCTION match_documents_1024_filtered(
    p_collection_ids UUID[],
    query_embedding vector(1024),
    match_threshold FLOAT DEFAULT 0.0,
    match_count INT DEFAULT 10,
    filter_conditions JSONB DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        (1 - (d.embedding_1024 <=> query_embedding))::FLOAT AS similarity
    FROM documents d
    WHERE d.collection_id = ANY(p_collection_ids)
      AND d.embedding_1024 IS NOT NULL
      AND (1 - (d.embedding_1024 <=> query_embedding)) > match_threshold
      AND (
          filter_conditions IS NULL
          OR EXISTS (
              SELECT 1 FROM jsonb_array_elements(filter_conditions) AS fc
              WHERE (fc->>'source_api' IS NULL OR d.metadata->>'source_api' = fc->>'source_api')
                AND (fc->>'doc_type' IS NULL OR d.metadata->>'doc_type' = fc->>'doc_type')
                AND (fc->>'jurisdiction_detail' IS NULL OR d.metadata->>'jurisdiction_detail' = fc->>'jurisdiction_detail')
          )
      )
    ORDER BY d.embedding_1024 <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 1792 filtered
CREATE OR REPLACE FUNCTION match_documents_1792_filtered(
    p_collection_ids UUID[],
    query_embedding vector(1792),
    match_threshold FLOAT DEFAULT 0.0,
    match_count INT DEFAULT 10,
    filter_conditions JSONB DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        (1 - (d.embedding_1792 <=> query_embedding))::FLOAT AS similarity
    FROM documents d
    WHERE d.collection_id = ANY(p_collection_ids)
      AND d.embedding_1792 IS NOT NULL
      AND (1 - (d.embedding_1792 <=> query_embedding)) > match_threshold
      AND (
          filter_conditions IS NULL
          OR EXISTS (
              SELECT 1 FROM jsonb_array_elements(filter_conditions) AS fc
              WHERE (fc->>'source_api' IS NULL OR d.metadata->>'source_api' = fc->>'source_api')
                AND (fc->>'doc_type' IS NULL OR d.metadata->>'doc_type' = fc->>'doc_type')
                AND (fc->>'jurisdiction_detail' IS NULL OR d.metadata->>'jurisdiction_detail' = fc->>'jurisdiction_detail')
          )
      )
    ORDER BY d.embedding_1792 <=> query_embedding
    LIMIT match_count;
END;
$$;


-- ============================================================
-- Step 7: Secure document insertion RPC
-- Used when inserting via anon key (respects RLS).
-- If you use service_key for inserts, this is optional.
-- ============================================================

CREATE OR REPLACE FUNCTION insert_documents_secure(
    p_collection_name TEXT,
    p_documents JSONB
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_collection_id UUID;
    v_doc JSONB;
    v_inserted INT := 0;
BEGIN
    -- Look up collection
    SELECT id INTO v_collection_id
    FROM collections
    WHERE name = p_collection_name;

    IF v_collection_id IS NULL THEN
        RETURN jsonb_build_object('success', false, 'error', 'Collection not found: ' || p_collection_name);
    END IF;

    -- Insert each document
    FOR v_doc IN SELECT * FROM jsonb_array_elements(p_documents)
    LOOP
        INSERT INTO documents (
            id,
            collection_id,
            content,
            metadata,
            embedding_1536,
            embedding_1024,
            embedding_1792,
            sentence_embeddings,
            sentence_texts
        ) VALUES (
            COALESCE((v_doc->>'id')::UUID, gen_random_uuid()),
            v_collection_id,
            v_doc->>'content',
            COALESCE(v_doc->'metadata', '{}'::JSONB),
            CASE WHEN v_doc ? 'embedding_1536' THEN (v_doc->>'embedding_1536')::vector(1536) ELSE NULL END,
            CASE WHEN v_doc ? 'embedding_1024' THEN (v_doc->>'embedding_1024')::vector(1024) ELSE NULL END,
            CASE WHEN v_doc ? 'embedding_1792' THEN (v_doc->>'embedding_1792')::vector(1792) ELSE NULL END,
            v_doc->'sentence_embeddings',
            v_doc->'sentence_texts'
        );
        v_inserted := v_inserted + 1;
    END LOOP;

    RETURN jsonb_build_object('success', true, 'inserted_count', v_inserted);

EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object(
        'success', false,
        'error', SQLERRM,
        'detail', SQLSTATE
    );
END;
$$;


-- ============================================================
-- Done! Your Supabase database is ready for the RAG pipeline.
-- ============================================================
