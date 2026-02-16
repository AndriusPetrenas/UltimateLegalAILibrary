# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.1.0] - 2026-02-12

### Added
- **QueryLex RAG Pipeline** (12 modules, ~7,000 lines): Complete production-grade retrieval pipeline
  - Document Processor with token-based chunking and legal structure awareness
  - Multi-provider Embedding Service (OpenAI, Cohere, Isaacus, Voyage, Qwen3)
  - Cross-Encoder Reranker (+15-25% accuracy)
  - HyDE - Hypothetical Document Embeddings (+10-30% accuracy)
  - Query Decomposer with Reciprocal Rank Fusion
  - Agentic RAG with iterative self-correcting search
  - ColBERT-style token-level scoring
  - Adaptive Query Classifier (zero-cost heuristic routing)
  - Legal Tokenizer (100+ abbreviations, citation patterns)
  - Summary-Augmented Chunking (SAC)
  - LLM-based Metadata Extractor
  - Shared LLM Utils for RAG features
- **French Contract Generator** workflow: Multi-step contract generation for NDA, Service Agreements, and CDI
- **Legal Research Pipeline** workflow: Query decomposition with parallel retrieval and structured analysis
- **Workflow Engine** source code: The execution engine that powers all QueryLex workflows (6 node types)

### Changed
- Updated main README with RAG pipeline section and new workflows
- Updated workflows README with new entries and engine documentation
- Updated code-snippets README with RAG pipeline section

## [1.0.0] - 2026-01-27

### Added
- First public release
- Core system prompts: contract-analyst, legal-researcher, compliance-checker
- Core workflows: contract-review, contract-comparison, legal-memo
- MCP configs for Claude Desktop
- Documentation and contribution guidelines
