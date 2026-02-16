# Ultimate Legal AI Library

Open-source collection of prompts, workflows, datasets, and tools for AI-powered legal applications.

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/AndriusPetrenas/UltimateLegalAILibrary.git

# Browse resources
cd UltimateLegalAILibrary
```

## What's Inside

| Category | Count | Description |
|----------|-------|-------------|
| [**System Prompts**](./prompts/system-prompts/) | 5 | Ready-to-use AI personas for legal tasks |
| [**Prompt Templates**](./prompts/prompt-templates/) | 3 | Fill-in-the-blank prompts for common operations |
| [**Workflows**](./workflows/) | 2 | Importable automation definitions (+ workflow engine) |
| [**MCP Configs**](./mcp-configs/) | 3 | Claude Desktop and server configurations |
| [**Tools**](./tools/) | 3 | Curated links to legal NLP libraries |
| [**Datasets**](./datasets/) | 2 | Links to training and evaluation data |
| [**RAG Pipeline**](./code-snippets/python/rag-pipeline/) | 14 modules | Production RAG system from QueryLex (~8,500 lines) |
| [**Code Snippets**](./code-snippets/) | 17 | Python utilities + example script |
| [**Sample Data**](./sample-data/) | 2 | Example clauses and documents |

## Hosted vs. Linked Resources

### Directly Downloadable (Hosted)
- System prompts and prompt templates (`.md`)
- Workflow definitions (`.json`, `.yaml`)
- MCP server configurations (`.json`)
- Code snippets (`.py`)
- Sample data (`.jsonl`, `.md`)

### External References (Linked)
- Full tools (LexNLP, Eyecite, Unstructured)
- Large datasets (CUAD, LegalBench)
- Embedding models (on HuggingFace)
- Commercial APIs

## Featured Resources

### System Prompts

| Prompt | Use Case | Model |
|--------|----------|-------|
| [Contract Analyst](./prompts/system-prompts/contract-analyst/) | Analyze commercial contracts | Claude, GPT-4 |
| [Legal Researcher](./prompts/system-prompts/legal-researcher/) | Case law and statute research | Any |
| [Due Diligence Reviewer](./prompts/system-prompts/due-diligence/) | M&A due diligence checklists | Claude, GPT-4 |
| [Compliance Checker](./prompts/system-prompts/compliance-checker/) | GDPR, AML compliance review | Any |
| [Document Drafter](./prompts/system-prompts/document-drafter/) | Contract and memo drafting | GPT-4, Claude |

### Workflows

| Workflow | Description | Engine |
|----------|-------------|--------|
| [French Contract Generator](./workflows/french-contract-generator/) | Generate French-law contracts (NDA, CDI, Services) with placeholders | QueryLex |
| [Legal Research Pipeline](./workflows/legal-research/) | Deep research with query decomposition and parallel retrieval | QueryLex |

### RAG Pipeline (Full Source Code)

Production-grade retrieval pipeline from [QueryLex](https://querylex.com). 14 modules, ~8,500 lines of Python. Fully self-contained and downloadable with `requirements.txt`.

| Module | Purpose | Impact |
|--------|---------|--------|
| [Document Processor](./code-snippets/python/rag-pipeline/document_processor.py) | Token-based chunking with legal structure awareness | Core |
| [Embedding Service](./code-snippets/python/rag-pipeline/embedding_service.py) | 5 providers: OpenAI, Cohere, Isaacus, Voyage, Qwen3 | Core |
| [Cross-Encoder Reranker](./code-snippets/python/rag-pipeline/reranker.py) | Two-stage reranking | +15-25% accuracy |
| [HyDE](./code-snippets/python/rag-pipeline/hyde.py) | Hypothetical Document Embeddings | +10-30% accuracy |
| [Query Decomposer](./code-snippets/python/rag-pipeline/query_decomposer.py) | Multi-query with RRF merging | +15-25% recall |
| [Agentic RAG](./code-snippets/python/rag-pipeline/agentic_rag.py) | Iterative search with self-correction | Complex queries |
| [ColBERT Service](./code-snippets/python/rag-pipeline/colbert_service.py) | Token-level scoring approximation | Fine-grained |
| [Query Classifier](./code-snippets/python/rag-pipeline/query_classifier.py) | Adaptive retrieval routing (zero-cost) | Optimization |
| [Legal Tokenizer](./code-snippets/python/rag-pipeline/legal_tokenizer.py) | 100+ legal abbreviations, citation patterns | Legal domain |
| [SAC Generator](./code-snippets/python/rag-pipeline/sac_generator.py) | Summary-Augmented Chunking | +10-20% accuracy |
| [Metadata Extractor](./code-snippets/python/rag-pipeline/metadata_extractor.py) | LLM-based document metadata extraction | Filtering |
| [LLM Utils](./code-snippets/python/rag-pipeline/llm_utils.py) | Shared LLM client for RAG features | Infrastructure |

### MCP Configurations

| Config | Tools | Purpose |
|--------|-------|---------|
| [Legal Research Stack](./mcp-configs/claude-desktop/legal-research.json) | EUR-Lex, CourtListener | EU and US legal research |
| [Document Management](./mcp-configs/claude-desktop/document-management.json) | Google Drive, iManage | File access |

## How to Use

### 1. System Prompts

Copy the prompt content and use it as a system message in your AI application:

```python
with open('prompts/system-prompts/contract-analyst/prompt.md', 'r') as f:
    system_prompt = f.read()

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Analyze this NDA for risks..."}
    ]
)
```

### 2. Workflows

Import workflow JSON into your automation platform:

```bash
# Download workflow
curl -O https://raw.githubusercontent.com/AndriusPetrenas/UltimateLegalAILibrary/main/workflows/legal-research/workflow.json

# Import into QueryLex or n8n
```

### 3. MCP Configurations

Add to your Claude Desktop config:

```json
// ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    // Paste configuration from mcp-configs/claude-desktop/
  }
}
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. **Fork** the repository
2. **Add** your resource following our templates
3. **Submit** a pull request

### What We Accept

- **System prompts** tested with at least one major LLM
- **Workflows** that solve real legal use cases
- **Tool evaluations** with honest assessments
- **Sample data** that respects privacy (no real client data)

## Resource Schemas

### Prompt Metadata (`metadata.yaml`)

```yaml
name: "Contract Analyst"
type: system-prompt
description: "Analyzes commercial contracts for risks"
target_model: claude-3
domain: contracts
tasks:
  - clause-identification
  - risk-assessment
author:
  name: "Your Name"
  github: username
license: CC0
version: "1.0.0"
```

### Tool Link (`toolname.yaml`)

```yaml
name: "LexNLP"
type: tool-link
repository: https://github.com/LexPredict/lexpredict-lexnlp
language: python
license: AGPL-3.0
our_evaluation:
  strengths:
    - "Excellent date extraction"
  weaknesses:
    - "Limited non-English support"
```

## License

- **This repository structure and metadata**: [CC0 1.0 Universal](LICENSE) (public domain)
- **Individual resources**: Check each resource's license
- **Linked external tools**: Subject to their respective licenses

## Related Projects

- [QueryLex](https://querylex.com) - Legal AI platform
- [LegalBench](https://github.com/HazyResearch/legalbench) - Legal reasoning benchmark
- [CUAD](https://www.atticusprojectai.org/cuad) - Contract Understanding dataset

## Support

- [Open an Issue](https://github.com/AndriusPetrenas/UltimateLegalAILibrary/issues) for bugs or suggestions
- [Discussions](https://github.com/AndriusPetrenas/UltimateLegalAILibrary/discussions) for questions

---

Built with care for the legal AI community.
