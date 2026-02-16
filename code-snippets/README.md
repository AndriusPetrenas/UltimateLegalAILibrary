# Code Snippets

Utility functions and complete systems for legal text processing.

## RAG Pipeline (Complete System)

The **[RAG Pipeline](./python/rag-pipeline/)** is a production-grade Retrieval-Augmented Generation system from [QueryLex](https://querylex.com). 14 modules, ~8,500 lines of Python. Fully self-contained and downloadable with `requirements.txt`, Supabase SQL setup, and an end-to-end example script.

| Module | Purpose |
|--------|---------|
| [document_processor.py](./python/rag-pipeline/document_processor.py) | Token-based chunking with legal structure awareness |
| [embedding_service.py](./python/rag-pipeline/embedding_service.py) | Multi-provider embeddings (OpenAI, Cohere, Isaacus, Voyage, Qwen3) |
| [reranker.py](./python/rag-pipeline/reranker.py) | Cross-encoder reranking |
| [hyde.py](./python/rag-pipeline/hyde.py) | Hypothetical Document Embeddings |
| [query_decomposer.py](./python/rag-pipeline/query_decomposer.py) | Multi-query decomposition with RRF merging |
| [agentic_rag.py](./python/rag-pipeline/agentic_rag.py) | Iterative search with self-correction |
| [colbert_service.py](./python/rag-pipeline/colbert_service.py) | ColBERT-style token-level scoring |
| [query_classifier.py](./python/rag-pipeline/query_classifier.py) | Adaptive retrieval routing |
| [legal_tokenizer.py](./python/rag-pipeline/legal_tokenizer.py) | Legal abbreviation and citation handling |
| [sac_generator.py](./python/rag-pipeline/sac_generator.py) | Summary-Augmented Chunking |
| [metadata_extractor.py](./python/rag-pipeline/metadata_extractor.py) | Document metadata extraction |
| [llm_utils.py](./python/rag-pipeline/llm_utils.py) | Shared LLM client for RAG features |
| [supabase_client.py](./python/rag-pipeline/supabase_client.py) | Supabase pgvector store with multi-dimension support |
| [legal_filters.py](./python/rag-pipeline/legal_filters.py) | Legal source metadata filter mapping (FR/EU) |

See the [RAG Pipeline README](./python/rag-pipeline/README.md) for architecture details, setup instructions, and usage examples.

## Python Utilities

| Snippet | Purpose |
|---------|---------|
| [citation-parser.py](./python/citation-parser.py) | Parse legal citations |
| [contract-chunker.py](./python/contract-chunker.py) | Smart document chunking |

## Usage

Copy the snippet into your project and modify as needed. All snippets are CC0 licensed.
