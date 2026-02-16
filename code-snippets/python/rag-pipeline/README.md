# QueryLex RAG Pipeline - Complete Source Code

Production-grade Retrieval-Augmented Generation (RAG) pipeline optimized for legal documents. Used in [QueryLex](https://querylex.com) to power legal research, contract analysis, and document Q&A.

This is a **fully self-contained, downloadable package**. All modules reference each other locally with no external application dependencies.

## Architecture Overview

```
User Query
    |
    v
[Legal Tokenizer] --> Normalize abbreviations, citations
    |
    v
[Query Classifier] --> Route: FACTUAL / KEYWORD / COMPLEX / CONCEPTUAL
    |
    +---> [HyDE] --> Generate hypothetical answer for better embedding match
    +---> [Query Decomposer] --> Break into 3-4 sub-queries
    |
    v
[Embedding Service] --> Multi-provider: OpenAI / Cohere / Isaacus / Voyage / Qwen3
    |
    v
[Vector Search] --> Supabase pgvector hybrid search (semantic + BM25)
    |
    v
[Cross-Encoder Reranker] --> ms-marco-MiniLM-L-6-v2
    |
    +---> [ColBERT Service] --> Token-level re-ranking (optional)
    +---> [Agentic RAG] --> Multi-step iterative search (optional)
    |
    v
LLM Response with Citations
```

## Quick Start

### 1. Download

```bash
git clone https://github.com/AndriusPetrenas/UltimateLegalAILibrary.git
cd UltimateLegalAILibrary/code-snippets/python/rag-pipeline/
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the pipeline directory:

```bash
# === Required: At least one LLM provider ===
OPENAI_API_KEY=sk-...              # For embeddings + LLM (most common)
# MISTRAL_API_KEY=...              # EU-based, GDPR compliant (preferred for RAG utils)
# DEEPSEEK_API_KEY=...             # Cost-efficient alternative
# OPENROUTER_API_KEY=...           # Multi-provider fallback

# === Required: Supabase (vector store) ===
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...        # For admin operations (document upload)
```

The `.env` file is automatically loaded by the example script and can be loaded in your own code with `python-dotenv`.

### 4. Set Up Supabase

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** in the left sidebar
3. Paste the contents of **`supabase_setup.sql`** and click **Run**

This creates everything you need: tables, indexes, and all 9 RPC functions for similarity search across all embedding dimensions.

### 5. Run the Example

```bash
python example.py
```

This runs the full pipeline end-to-end: loads your `.env`, creates a collection, chunks sample legal text, generates embeddings, stores them in Supabase, runs a semantic search, and reranks the results. Read through `example.py` to understand each step.

## Components (14 modules, ~8,500 lines)

| # | File | Purpose | Key Class/Function |
|---|------|---------|--------------------|
| 1 | `document_processor.py` | Token-based chunking with legal structure awareness | `LegalDocumentProcessor` |
| 2 | `embedding_service.py` | Multi-provider embedding orchestration (5 providers) | `EmbeddingService` |
| 3 | `reranker.py` | Cross-encoder reranking (+15-25% accuracy) | `rerank_results()` |
| 4 | `hyde.py` | Hypothetical Document Embeddings (+10-30% accuracy) | `HyDEGenerator` |
| 5 | `query_decomposer.py` | Multi-query decomposition with RRF merging | `QueryDecomposer` |
| 6 | `agentic_rag.py` | Iterative search with self-correction (up to 3 iterations) | `AgenticSearcher` |
| 7 | `colbert_service.py` | ColBERT-style token-level scoring approximation | `ColBERTService` |
| 8 | `query_classifier.py` | Adaptive retrieval routing (no LLM required) | `AdaptiveQueryClassifier` |
| 9 | `legal_tokenizer.py` | 100+ legal abbreviations, citation-aware tokenization | `LegalTokenizer` |
| 10 | `sac_generator.py` | Summary-Augmented Chunking for context preservation | `SACGenerator` |
| 11 | `metadata_extractor.py` | LLM-based structured metadata extraction | `MetadataExtractor` |
| 12 | `llm_utils.py` | Shared LLM client for RAG enhancement features | `RAGLLMClient` |
| 13 | `supabase_client.py` | Supabase pgvector store with multi-dimension support | `SupabaseVectorClient` |
| 14 | `legal_filters.py` | Legal source metadata filter mapping (FR/EU) | `resolve_filters()` |

## Why These Technical Choices

### Token-based chunking (not character-based)

Character counts don't correlate with how embedding models process text. A 500-character chunk might be 80 tokens or 200 tokens depending on the language and vocabulary. Token-based chunking ensures each chunk is **optimally sized for the embedding model's context window**, preventing truncation and wasted capacity. Each of our 5 embedding providers has its own optimal chunk size configured in `embedding_service.py`.

### Multiple embedding columns (not one)

Different embedding models produce different dimension vectors (1536, 1024, 1792). Rather than re-embedding an entire dataset when switching models, we store **one column per dimension**. This lets users try different embedding providers on the same data without re-processing. The RPC functions automatically route to the correct column.

### Cross-encoder reranking (not just bi-encoder)

Bi-encoders (used in initial vector search) encode query and document **independently** — fast but approximate. Cross-encoders process the query-document pair **jointly**, capturing token-level interactions that bi-encoders miss. The trade-off: cross-encoders are ~100x slower, so we use them only on the top 15-30 candidates from the bi-encoder stage. This two-stage approach gives us **+15-25% accuracy** at negligible latency cost.

### HyDE (Hypothetical Document Embeddings)

When a user asks "What constitutes unfair dismissal?", the raw query embedding is far from the embedding of the actual legal text that answers it. HyDE generates a **hypothetical answer passage** using an LLM, then embeds *that* for retrieval. The hypothetical passage is semantically closer to the real documents, improving recall by **+10-30%** for conceptual queries. Cost: ~$0.001-0.005 per query.

### Query decomposition with RRF (Reciprocal Rank Fusion)

Complex legal questions often span multiple topics ("Compare GDPR and CCPA requirements for data controllers"). A single search can't cover all aspects. We decompose into 2-4 focused sub-queries, search each independently, then merge results using **Reciprocal Rank Fusion** — a parameter-free merging algorithm that weights documents appearing across multiple sub-queries higher.

### ColBERT approximation (not full ColBERT)

Full ColBERT requires storing per-token embeddings for every document (~128 vectors per passage), demanding massive storage and a specialized index. Our approximation uses **sentence-level embeddings** — breaking documents into sentences and computing max-similarity across sentence pairs. This captures ~70% of ColBERT's fine-grained matching benefit at a fraction of the storage cost.

### Supabase + pgvector (not Pinecone/Weaviate/Chroma)

We chose Supabase because:
- **PostgreSQL foundation** — battle-tested, SQL-queryable, supports JSONB metadata filtering
- **pgvector extension** — native vector similarity search without a separate service
- **Row Level Security (RLS)** — built-in multi-tenancy, each user only sees their own data
- **Single infrastructure** — vectors, metadata, auth, and API all in one place
- **Free tier** — sufficient for development and small-scale production

### Heuristic query classification (no LLM)

The query classifier routes queries to different retrieval strategies without any LLM call. It uses **regex patterns and keyword detection** to classify as FACTUAL/KEYWORD/COMPLEX/CONCEPTUAL. This is a zero-cost optimization — each query type triggers different feature combinations (HyDE for conceptual, decomposition for complex, etc.), so you don't burn LLM tokens on simple keyword searches.

### Mistral as default RAG utility model

The LLM utils module (used by HyDE, SAC, query decomposition, metadata extraction) defaults to Mistral Nemo because:
- **EU-based** — data processed in Europe, important for GDPR-sensitive legal data
- **No training on API data** — Mistral commits to not training on API inputs
- **Fast and cheap** — $0.15/M tokens, 128K context, low latency
- **OpenAI-compatible API** — uses the same SDK, easy to swap

### Legal tokenizer (domain-specific preprocessing)

Standard NLP tokenizers break on legal abbreviations: "Art. 101" becomes "Art" + "." + "101" (3 tokens) when it should be one concept. Our tokenizer handles 100+ legal abbreviations (Art., Reg., Dir., etc.), citation patterns (C-123/45, 2016/679), and multi-jurisdiction formats (US, EU, French, German). This prevents embedding models from fragmenting legal terms.

### Summary-Augmented Chunking (SAC)

When you chunk a 50-page contract into 256-token pieces, each chunk loses context: *which* contract is this from? *What section* are we in? SAC prepends a 2-3 sentence LLM-generated summary to each chunk, providing context that survives chunking. Cost: ~$0.001-0.01 per chunk. Impact: **+10-20% retrieval accuracy** on context-dependent queries.

## Component Details

### 1. Document Processor (`document_processor.py`)

The core chunking engine. Token-based sizing with legal structure awareness.

```python
from document_processor import LegalDocumentProcessor, count_tokens

processor = LegalDocumentProcessor(embedding_service=your_embedding_service)

# Process and index documents
processor.create_ragmodel(
    dataset_name="my-legal-docs",
    documents=["page 1 text...", "page 2 text..."],
    metadatas=[{"source": "contract.pdf", "page": 1}, ...],
    chunk_size_tokens=256,
    chunk_overlap_tokens=50
)

# Query with hybrid search + reranking
results = processor.query_dataset(
    dataset_name="my-legal-docs",
    query="What are the termination conditions?",
    n_results=8,
    use_hybrid_search=True,
    use_reranking=True
)
```

### 2. Embedding Service (`embedding_service.py`)

Unified interface for 5 embedding providers with model-specific chunking configs.

```python
from embedding_service import EmbeddingService, get_chunk_config

service = EmbeddingService(provider="openai", model="text-embedding-3-small")
embeddings = service.embed_documents(["text1", "text2"])
query_embedding = service.embed_query("search query")

# Get optimal chunking parameters for a model
config = get_chunk_config("text-embedding-3-small")
# {'chunk_size_tokens': 256, 'chunk_overlap_tokens': 50, 'max_tokens': 8191}
```

**Supported Providers:**

| Provider | Model | Dimensions | Specialization |
|----------|-------|-----------|----------------|
| OpenAI | text-embedding-3-small | 1536 | General purpose |
| Cohere | embed-v3 | 1024 | Multilingual |
| Isaacus | kanon-2-embedder | 1792 | Legal-specialized |
| Voyage AI | voyage-3-large | 1024 | High quality |
| Qwen3 (OpenRouter) | qwen3-embedding-8b | 1024 | Cost-efficient |

### 3. Cross-Encoder Reranker (`reranker.py`)

Two-stage retrieval with cross-encoder scoring.

```python
from reranker import rerank_results

reranked, stats = rerank_results(
    query="force majeure clause interpretation",
    results=initial_results,  # From vector search
    top_k=5,
    enabled=True
)
```

### 4. HyDE - Hypothetical Document Embeddings (`hyde.py`)

Generates a hypothetical answer, embeds it, and uses that for retrieval.

```python
from hyde import apply_hyde

expanded_query, hypotheticals, stats = apply_hyde(
    query="What constitutes unfair dismissal in French law?",
    enabled=True,
    num_hypothetical=1
)
```

### 5. Query Decomposer (`query_decomposer.py`)

Breaks complex multi-part questions into focused sub-queries, merges results with Reciprocal Rank Fusion.

```python
from query_decomposer import decompose_query, merge_results

sub_queries, stats = decompose_query(
    query="Compare GDPR and CCPA requirements for data controllers",
    enabled=True,
    max_subqueries=4
)

# After searching each sub-query:
merged = merge_results(results_per_query, max_results=8)
```

### 6. Agentic RAG (`agentic_rag.py`)

Multi-step iterative search with self-evaluation and query reformulation.

```python
from agentic_rag import AgenticSearcher

searcher = AgenticSearcher(
    llm_client=your_llm,
    search_fn=your_search_function,
    max_iterations=3
)

results, metadata = searcher.search(
    query="What are the penalties for GDPR non-compliance?",
    n_results=8
)
# metadata: {iterations: 2, total_searches: 4, search_history: [...]}
```

### 7. ColBERT Service (`colbert_service.py`)

Sentence-level embedding approximation of ColBERT's token-level scoring.

```python
from colbert_service import ColBERTService

colbert = ColBERTService(embedding_service=your_embedding_service)

results, metadata = colbert.search(
    query="Article 101 TFEU horizontal agreements",
    dataset_name="eu-competition",
    n_results=5,
    n_candidates=15
)
```

### 8. Query Classifier (`query_classifier.py`)

Zero-cost heuristic classification for adaptive retrieval routing.

```python
from query_classifier import get_adaptive_retrieval_params

params = get_adaptive_retrieval_params(query, retrieval_settings)
# Returns: {use_hybrid_search: True, use_reranking: True, n_results: 8}
```

**Query Types:** FACTUAL, KEYWORD, COMPLEX, CONCEPTUAL — each with optimized retrieval parameters.

### 9. Legal Tokenizer (`legal_tokenizer.py`)

Handles 100+ legal abbreviations and citation patterns across US, EU, French, and German law.

```python
from legal_tokenizer import preprocess_legal_query

processed = preprocess_legal_query(
    "Art. 101 TFEU and Reg. (EU) 2016/679",
    enabled=True
)
```

### 10. SAC Generator (`sac_generator.py`)

Summary-Augmented Chunking — generates contextual summaries to preserve document-level context.

```python
from sac_generator import SACGenerator

sac = SACGenerator(enabled=True, batch_size=5)
enhanced_text, summary = sac.enhance_chunk(
    chunk_text="The parties agree to...",
    source="contract.pdf",
    position=3,
    total_chunks=20
)
```

### 11. Metadata Extractor (`metadata_extractor.py`)

LLM-based extraction of document type, jurisdiction, dates, parties, and practice area.

```python
from metadata_extractor import extract_document_metadata

metadata = extract_document_metadata(
    content="REGULATION (EU) 2016/679...",
    filename="gdpr.pdf",
    enabled=True,
    use_llm=True
)
# Returns: {document_type: "reglement_eu", jurisdiction: "EU", date: "2016-04-27", ...}
```

### 12. LLM Utils (`llm_utils.py`)

Shared lightweight LLM client used by SAC, HyDE, Query Decomposer, and Metadata Extractor.

```python
from llm_utils import RAGLLMClient

client = RAGLLMClient(preferred_model="open-mistral-nemo")
response = client.complete(
    prompt="Summarize this clause...",
    system_prompt="You are a legal expert.",
    max_tokens=500
)
```

**Model Priority:** Mistral (EU/GDPR) > DeepSeek (cost) > OpenAI (reliable) > OpenRouter (multi-provider)

### 13. Supabase Vector Client (`supabase_client.py`)

Handles all vector store operations: collection management, document insertion, and similarity search.

```python
from supabase_client import SupabaseVectorClient

client = SupabaseVectorClient(use_service_key=True)

# Create a collection
client.create_collection("my-legal-docs", user_id="...")

# Add documents with embeddings
client.add_documents(
    collection_name="my-legal-docs",
    documents=["text1", "text2"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    metadatas=[{"source": "doc1.pdf"}, {"source": "doc2.pdf"}],
    embedding_model="text-embedding-3-small"
)

# Query for similar documents
results = client.query_collection(
    collection_name="my-legal-docs",
    query_embedding=[0.1, 0.2, ...],
    n_results=5
)
```

### 14. Legal Filters (`legal_filters.py`)

Maps UI filter keys to metadata conditions for filtering legal sources (French and EU law).

```python
from legal_filters import resolve_filters

# Translate user filter selections into query conditions
conditions = resolve_filters(["codes", "cedh_cour"])
# Returns: [
#     {"source_api": "legifrance", "doc_type": "code_article"},
#     {"source_api": "hudoc"}
# ]
```

## How These Work Together

The pipeline is modular — you can use any combination:

| Configuration | Components | Best For |
|--------------|------------|----------|
| **Minimal** | Embeddings + Vector Search | Simple document Q&A |
| **Standard** | + Reranker + Legal Tokenizer | Most legal use cases |
| **Advanced** | + HyDE + Query Decomposer | Complex research queries |
| **Maximum** | + Agentic RAG + ColBERT + SAC | Deep legal analysis |

## License

CC0 1.0 Universal — Public domain. Use freely in any project.

## Credits

Built by the [QueryLex](https://querylex.com) team. Production-tested on thousands of legal documents across EU and French law.
