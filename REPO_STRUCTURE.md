# Ultimate Legal AI Library - Repository Structure & Roadmap

This document shows the current repository structure and the planned roadmap for future additions. Items marked with `[PLANNED]` do not exist yet and are open for contributions.

---

## Current Directory Tree

```
UltimateLegalAILibrary/
│
├── README.md
├── LICENSE                             # CC0 1.0 Universal
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── REPO_STRUCTURE.md                   # This file
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── add-prompt.yml
│   │   ├── add-workflow.yml
│   │   ├── add-tool.yml
│   │   └── report-issue.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── validate.yml
│       └── link-check.yml
│
├── prompts/
│   ├── README.md
│   │
│   ├── system-prompts/
│   │   ├── contract-analyst/           # metadata.yaml, prompt.md, README.md
│   │   ├── legal-researcher/           # metadata.yaml, prompt.md
│   │   ├── due-diligence/              # metadata.yaml, prompt.md
│   │   ├── compliance-checker/         # metadata.yaml, prompt.md
│   │   └── document-drafter/           # metadata.yaml, prompt.md
│   │
│   └── prompt-templates/
│       ├── clause-extraction.md
│       ├── risk-assessment.md
│       └── summary-generation.md
│
├── workflows/
│   ├── README.md
│   ├── french-contract-generator/      # metadata.yaml, workflow.json, README.md
│   ├── legal-research/                 # metadata.yaml, workflow.json, README.md
│   └── workflow-engine/                # workflow_engine.py, extensions.py, README.md
│
├── mcp-configs/
│   ├── README.md
│   ├── claude-desktop/
│   │   ├── legal-research.json
│   │   ├── document-management.json
│   │   └── full-legal-stack.json
│   └── server-guides/
│       └── courtlistener-mcp.md
│
├── code-snippets/
│   ├── README.md
│   ├── python/
│   │   ├── citation-parser.py
│   │   ├── contract-chunker.py
│   │   └── rag-pipeline/               # 14 modules (~8,500 lines)
│   │       ├── README.md
│   │       ├── requirements.txt
│   │       ├── supabase_setup.sql
│   │       ├── example.py
│   │       ├── __init__.py
│   │       ├── agentic_rag.py
│   │       ├── colbert_service.py
│   │       ├── document_processor.py
│   │       ├── embedding_service.py
│   │       ├── hyde.py
│   │       ├── legal_filters.py
│   │       ├── legal_tokenizer.py
│   │       ├── llm_utils.py
│   │       ├── metadata_extractor.py
│   │       ├── query_classifier.py
│   │       ├── query_decomposer.py
│   │       ├── reranker.py
│   │       ├── sac_generator.py
│   │       └── supabase_client.py
│   └── [PLANNED] typescript/
│
├── sample-data/
│   ├── README.md
│   ├── contract-clauses/
│   │   └── indemnification-clauses.jsonl
│   └── test-documents/
│       └── sample-nda.md
│
├── tools/
│   ├── README.md
│   ├── nlp/
│   │   ├── lexnlp.yaml
│   │   └── eyecite.yaml
│   └── document-processing/
│       └── unstructured.yaml
│
├── datasets/
│   ├── README.md
│   ├── contracts/
│   │   └── cuad.yaml
│   └── benchmarks/
│       └── legalbench.yaml
│
└── docs/
    ├── getting-started.md
    └── faq.md
```

---

## Roadmap (Planned Additions)

The following resources are planned for future releases. Contributions welcome!

### System Prompts
- [ ] Clause Extractor
- [ ] GDPR Auditor
- [ ] Litigation Strategist
- [ ] IP Analyst
- [ ] Employment Law Advisor

### Prompt Templates
- [ ] comparison-analysis.md
- [ ] legal-memo-structure.md
- [ ] client-letter-draft.md
- [ ] deposition-questions.md
- [ ] contract-negotiation.md
- [ ] regulatory-filing.md
- [ ] case-brief-template.md

### Workflows
- [ ] Contract Review
- [ ] Contract Comparison
- [ ] Due Diligence Checklist
- [ ] Compliance Audit
- [ ] Document Assembly
- [ ] Legal Memo Generator
- [ ] Case Summarizer
- [ ] Clause Risk Scorer
- [ ] Late Payment Calculator
- [ ] Email Drafter
- [ ] Legal Translation

### MCP Configs
- [ ] Westlaw integration
- [ ] LexisNexis integration
- [ ] CourtListener standalone
- [ ] EUR-Lex standalone
- [ ] GitHub Legal Repos
- [ ] Additional server guides

### Code Snippets
- [ ] TypeScript utilities (citation-parser, legal-date-parser, contract-types, clause-extractor)
- [ ] Python: legal-ner-utils, bluebook-formatter, date-extractor, clause-classifier, redaction-helper, pdf-to-markdown, embedding-utils

### Sample Data
- [ ] Additional contract clause types (limitation-of-liability, termination, force-majeure, confidentiality, IP-assignment, non-compete)
- [ ] Legal citations (US case, US statute, EU case, UK case)
- [ ] Additional test documents (MSA, employment agreement, lease, terms of service)

### Tools & Datasets
- [ ] Additional NLP tool evaluations (Blackstone, Legal-BERT, spaCy Legal, Legal-SBERT)
- [ ] Additional document processing tools (Docassemble, pdfplumber, marker-pdf, Camelot)
- [ ] Additional dataset links (CaseHOLD, SCOTUS, CourtListener bulk, ECHR, etc.)

### Models Directory
- [ ] Embedding model comparison
- [ ] LLM legal task benchmarks

---

## File Templates

### 1. System Prompt - metadata.yaml

```yaml
name: "Contract Analyst"
slug: contract-analyst
type: system-prompt

description: >
  A comprehensive system prompt for analyzing commercial contracts,
  identifying risks, and extracting key terms.

target_model: claude-3
input_type: document
output_format: structured-json
token_estimate: 2500

domain: contracts
tasks:
  - clause-identification
  - risk-assessment
  - obligation-extraction
  - deadline-detection

jurisdiction: multi

files:
  prompt: prompt.md
  examples: examples/

author:
  name: "Your Name"
  github: your-username

license: CC0
version: "1.0.0"
created: 2026-01-27
last_updated: 2026-01-27

tested_with:
  - claude-3-5-sonnet
  - claude-3-opus
  - gpt-4o
```

### 2. System Prompt - prompt.md

```markdown
# Contract Analyst

You are an expert contract analyst with 20 years of experience reviewing commercial agreements. Your role is to carefully analyze contracts and provide structured, actionable insights.

## Your Expertise
- Commercial contracts (NDA, MSA, SaaS, licensing)
- Risk identification and mitigation
- Obligation tracking
- Deadline and renewal management

## Analysis Framework

When analyzing a contract, always:

1. **Identify the Parties**: Note all parties and their roles
2. **Summarize Key Terms**: Term, value, renewal conditions
3. **Flag Risks**: Categorize as HIGH/MEDIUM/LOW with explanations
4. **Extract Obligations**: List all obligations by party
5. **Note Deadlines**: All dates and notice periods

## Output Format

Provide your analysis as structured JSON:

```json
{
  "parties": [...],
  "summary": "...",
  "risks": [...],
  "obligations": [...],
  "deadlines": [...]
}
```

## Important Guidelines

- Always cite specific clause numbers
- Note any ambiguous or missing terms
- Highlight unusual or non-standard provisions
- Compare against market standards when relevant
- Never invent terms not present in the document
```

### 3. Workflow - metadata.yaml

```yaml
name: "Contract Comparison"
slug: contract-comparison
type: workflow

description: >
  Compares two contracts side-by-side, identifying differences
  in key clauses and highlighting potential risks.

engine: querylex  # querylex | n8n | both
complexity: medium

inputs:
  - name: contract_a
    type: document
    description: "First contract (base version)"
  - name: contract_b
    type: document
    description: "Second contract (comparison version)"

outputs:
  - name: comparison_report
    type: markdown
    description: "Detailed comparison with risk flags"

nodes:
  - type: start
  - type: action (x2)
  - type: code
  - type: output

estimated_runtime: "30-60 seconds"

author:
  name: "Your Name"
  github: your-username

license: CC0
version: "1.0.0"
created: 2026-01-27
```

### 4. Tool Link - toolname.yaml

```yaml
name: "LexNLP"
slug: lexnlp
type: tool-link

description: >
  Python library for extracting structured data from legal text,
  including dates, monetary values, citations, and named entities.

repository: https://github.com/LexPredict/lexpredict-lexnlp
documentation: https://lexpredict-lexnlp.readthedocs.io/
pypi: lexnlp

language: python
install_command: "pip install lexnlp"
license: AGPL-3.0
stars: 757  # Update periodically

our_evaluation:
  overall_rating: 4  # 1-5 scale

  strengths:
    - "Excellent date and money extraction"
    - "Handles legal abbreviations well"
    - "Active maintenance"
    - "Good documentation"

  weaknesses:
    - "AGPL license may be restrictive for commercial use"
    - "Limited non-English language support"
    - "Heavy dependencies"

  best_for:
    - "Contract data extraction"
    - "Citation parsing"
    - "Date normalization"

  not_recommended_for:
    - "Production systems with proprietary code (due to AGPL)"
    - "Non-English documents"

  alternatives:
    - blackstone
    - spacy-legal

category: nlp
subcategory: extraction
tags:
  - ner
  - extraction
  - contracts
  - citations
  - dates

last_evaluated: 2026-01-27
```

### 5. Dataset Link - datasetname.yaml

```yaml
name: "CUAD"
slug: cuad
type: dataset-link
full_name: "Contract Understanding Atticus Dataset"

description: >
  Expert-annotated dataset of 510 commercial contracts with
  41 types of legal clause annotations. Created for training
  and evaluating contract analysis models.

source:
  organization: "The Atticus Project"
  website: https://www.atticusprojectai.org/cuad
  paper: https://arxiv.org/abs/2103.06268

download:
  huggingface: "cuad"
  direct: https://zenodo.org/record/4599830

size:
  documents: 510
  annotations: 13000+
  file_size: "~500MB"

format:
  type: json
  structure: "SQuAD-style question answering"

license: CC-BY-4.0

citation: |
  @inproceedings{hendrycks2021cuad,
    title={CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review},
    author={Hendrycks, Dan and Burns, Collin and Chen, Anya and Ball, Spencer},
    booktitle={NeurIPS},
    year={2021}
  }

use_cases:
  - "Contract clause extraction"
  - "Legal NER training"
  - "Contract analysis benchmarking"

our_notes: >
  Excellent for training contract analysis models. The 41 clause
  types cover most common commercial contract provisions.
  Consider combining with MAUD for M&A-specific use cases.

related_datasets:
  - maud
  - contract-nli

last_updated: 2026-01-27
```

### 6. MCP Config - example.json

```json
{
  "mcpServers": {
    "legal-research": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-legal-research"],
      "env": {
        "COURTLISTENER_API_KEY": "${COURTLISTENER_API_KEY}"
      }
    },
    "eurlex": {
      "command": "python",
      "args": ["-m", "eurlex_mcp"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "/Users/lawyer/Documents/Cases"
      }
    }
  }
}
```

---

## GitHub Actions

### validate.yml

```yaml
name: Validate Resources

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'workflows/**'
      - 'tools/**'
      - 'datasets/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pyyaml jsonschema
      - run: python scripts/validate.py
```

### build-index.yml

```yaml
name: Build Index

on:
  push:
    branches: [main]
    paths:
      - 'prompts/**'
      - 'workflows/**'
      - 'tools/**'
      - 'datasets/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python scripts/build_index.py
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: update library index"
          file_pattern: "_index/*.json"
```

---

## Issue Templates

### add-prompt.yml

```yaml
name: Add System Prompt
description: Submit a new system prompt to the library
title: "[Prompt] "
labels: ["prompt", "new-resource"]
body:
  - type: input
    id: name
    attributes:
      label: Prompt Name
      placeholder: "Contract Analyst"
    validations:
      required: true

  - type: dropdown
    id: domain
    attributes:
      label: Domain
      options:
        - contracts
        - litigation
        - compliance
        - research
        - other
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      placeholder: "What does this prompt do?"
    validations:
      required: true

  - type: textarea
    id: prompt
    attributes:
      label: Prompt Content
      description: "Paste the full prompt here"
    validations:
      required: true

  - type: checkboxes
    id: tested
    attributes:
      label: Testing
      options:
        - label: I have tested this prompt with at least one LLM
          required: true
        - label: I confirm this prompt does not contain proprietary content
          required: true
```

---

## Priority Content to Create

### Phase 1 (Week 1)
- [ ] README.md ✅
- [ ] CONTRIBUTING.md ✅
- [ ] LICENSE (CC0)
- [ ] 5 system prompts (contract-analyst, legal-researcher, compliance-checker, document-drafter, due-diligence)
- [ ] 3 workflows (contract-review, legal-memo, contract-comparison)
- [ ] 3 MCP configs (legal-research, document-management, full-stack)

### Phase 2 (Week 2)
- [ ] 5 more system prompts
- [ ] 5 prompt templates
- [ ] 5 tool evaluations (lexnlp, blackstone, eyecite, docassemble, unstructured)
- [ ] 5 dataset links (cuad, casehold, legalbench, courtlistener, eurlex)
- [ ] Python code snippets (citation-parser, contract-chunker)

### Phase 3 (Week 3)
- [ ] MCP server guides
- [ ] Sample data (contract clauses, citations)
- [ ] Use case documentation
- [ ] GitHub Actions automation

### Phase 4 (Week 4)
- [ ] Connect to QueryLex Library page
- [ ] Public announcement
- [ ] Community feedback loop

---

## Notes

- All hosted resources use **CC0** license (public domain)
- Linked resources respect their original licenses
- No real client data - all samples are synthetic or public domain
- Focus on practical, tested resources over quantity
