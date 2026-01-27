# Ultimate Legal AI Library - Repository Structure

This document defines the complete repository structure for the Legal AI Library. Use this as a blueprint when creating files and folders.

---

## Directory Tree

```
UltimateLegalAILibrary/
│
├── README.md                           # Main landing page
├── LICENSE                             # CC0 1.0 Universal
├── CONTRIBUTING.md                     # Contribution guidelines
├── CODE_OF_CONDUCT.md                  # Community standards
├── CHANGELOG.md                        # Version history
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── add-prompt.yml              # Form for adding prompts
│   │   ├── add-workflow.yml            # Form for adding workflows
│   │   ├── add-tool.yml                # Form for linking tools
│   │   ├── add-dataset.yml             # Form for datasets
│   │   └── report-issue.yml            # Bug/broken link reports
│   ├── PULL_REQUEST_TEMPLATE.md        # PR template
│   └── workflows/
│       ├── validate.yml                # Schema validation on PR
│       ├── build-index.yml             # Auto-generate library-index.json
│       └── link-check.yml              # Weekly dead link detection
│
├── _index/                             # Auto-generated indexes (don't edit)
│   ├── library-index.json              # Complete searchable index
│   ├── prompts-index.json              # Prompts only
│   ├── workflows-index.json            # Workflows only
│   └── stats.json                      # Counts, last updated, etc.
│
│ ══════════════════════════════════════════════════════════════════════
│ HOSTED RESOURCES (Directly Downloadable)
│ ══════════════════════════════════════════════════════════════════════
│
├── prompts/
│   ├── README.md                       # How to use prompts
│   │
│   ├── system-prompts/
│   │   ├── contract-analyst/
│   │   │   ├── metadata.yaml           # Prompt metadata
│   │   │   ├── prompt.md               # THE ACTUAL PROMPT
│   │   │   ├── README.md               # Usage guide, examples
│   │   │   └── examples/
│   │   │       ├── input-1.txt
│   │   │       └── output-1.md
│   │   │
│   │   ├── legal-researcher/
│   │   │   ├── metadata.yaml
│   │   │   ├── prompt.md
│   │   │   └── README.md
│   │   │
│   │   ├── due-diligence-reviewer/
│   │   │   ├── metadata.yaml
│   │   │   ├── prompt.md
│   │   │   └── README.md
│   │   │
│   │   ├── compliance-checker/
│   │   │   ├── metadata.yaml
│   │   │   ├── prompt.md
│   │   │   └── README.md
│   │   │
│   │   ├── document-drafter/
│   │   │   ├── metadata.yaml
│   │   │   ├── prompt.md
│   │   │   └── README.md
│   │   │
│   │   ├── clause-extractor/
│   │   │   ├── metadata.yaml
│   │   │   ├── prompt.md
│   │   │   └── README.md
│   │   │
│   │   ├── gdpr-auditor/
│   │   │   ├── metadata.yaml
│   │   │   ├── prompt.md
│   │   │   └── README.md
│   │   │
│   │   ├── litigation-strategist/
│   │   │   ├── metadata.yaml
│   │   │   ├── prompt.md
│   │   │   └── README.md
│   │   │
│   │   ├── ip-analyst/
│   │   │   ├── metadata.yaml
│   │   │   ├── prompt.md
│   │   │   └── README.md
│   │   │
│   │   └── employment-law-advisor/
│   │       ├── metadata.yaml
│   │       ├── prompt.md
│   │       └── README.md
│   │
│   └── prompt-templates/
│       ├── README.md
│       ├── clause-extraction.md        # Template with {{CLAUSE_TYPE}}
│       ├── risk-assessment.md          # Template with {{DOCUMENT}}
│       ├── summary-generation.md
│       ├── comparison-analysis.md
│       ├── legal-memo-structure.md
│       ├── client-letter-draft.md
│       ├── deposition-questions.md
│       ├── contract-negotiation.md
│       ├── regulatory-filing.md
│       └── case-brief-template.md
│
├── workflows/
│   ├── README.md                       # How workflows work
│   │
│   ├── contract-review/
│   │   ├── metadata.yaml
│   │   ├── workflow.json               # Importable workflow
│   │   ├── README.md                   # Setup instructions
│   │   └── diagram.png                 # Visual representation
│   │
│   ├── contract-comparison/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   ├── README.md
│   │   └── diagram.png
│   │
│   ├── due-diligence/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   └── README.md
│   │
│   ├── legal-research/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   └── README.md
│   │
│   ├── compliance-audit/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   └── README.md
│   │
│   ├── document-assembly/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   └── README.md
│   │
│   ├── legal-memo-generator/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   └── README.md
│   │
│   ├── case-summarizer/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   └── README.md
│   │
│   ├── clause-risk-scorer/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   └── README.md
│   │
│   ├── late-payment-calculator/
│   │   ├── metadata.yaml
│   │   ├── workflow.json               # Includes code node
│   │   └── README.md
│   │
│   ├── email-drafter/
│   │   ├── metadata.yaml
│   │   ├── workflow.json
│   │   └── README.md
│   │
│   └── legal-translation/
│       ├── metadata.yaml
│       ├── workflow.json
│       └── README.md
│
├── mcp-configs/
│   ├── README.md                       # MCP setup guide
│   │
│   ├── claude-desktop/
│   │   ├── legal-research.json         # EUR-Lex + CourtListener
│   │   ├── document-management.json    # Google Drive + iManage
│   │   ├── full-legal-stack.json       # Combined config
│   │   ├── westlaw-integration.json    # Westlaw API (requires subscription)
│   │   ├── lexisnexis-integration.json # LexisNexis API
│   │   ├── courtlistener.json          # Free US case law
│   │   ├── eurlex.json                 # EU legislation
│   │   └── github-legal-repos.json     # Access legal code repos
│   │
│   ├── server-guides/
│   │   ├── courtlistener-mcp.md        # Setup guide for CourtListener MCP
│   │   ├── eurlex-mcp.md               # EUR-Lex MCP setup
│   │   ├── imanage-mcp.md              # iManage integration
│   │   ├── google-drive-legal.md       # Google Drive for legal docs
│   │   ├── westlaw-mcp.md              # Westlaw API integration
│   │   └── custom-database-mcp.md      # Connect to custom legal DB
│   │
│   └── custom-servers/
│       └── citation-validator/
│           ├── metadata.yaml
│           ├── server.py               # Custom MCP server
│           ├── requirements.txt
│           └── README.md
│
├── code-snippets/
│   ├── README.md
│   │
│   ├── python/
│   │   ├── citation-parser.py          # Parse legal citations
│   │   ├── contract-chunker.py         # Smart document chunking
│   │   ├── legal-ner-utils.py          # Named entity recognition
│   │   ├── bluebook-formatter.py       # Format citations to Bluebook
│   │   ├── date-extractor.py           # Extract dates from legal text
│   │   ├── clause-classifier.py        # Classify clause types
│   │   ├── redaction-helper.py         # PII detection and redaction
│   │   ├── pdf-to-markdown.py          # Convert legal PDFs
│   │   └── embedding-utils.py          # Embedding generation helpers
│   │
│   └── typescript/
│       ├── citation-parser.ts          # TypeScript citation parser
│       ├── legal-date-parser.ts        # Date parsing utilities
│       ├── contract-types.ts           # TypeScript types for contracts
│       └── clause-extractor.ts         # Extract clauses from HTML/MD
│
├── sample-data/
│   ├── README.md
│   │
│   ├── contract-clauses/
│   │   ├── metadata.yaml
│   │   ├── indemnification-clauses.jsonl    # ~100 examples
│   │   ├── limitation-of-liability.jsonl
│   │   ├── termination-clauses.jsonl
│   │   ├── force-majeure-clauses.jsonl
│   │   ├── confidentiality-clauses.jsonl
│   │   ├── ip-assignment-clauses.jsonl
│   │   └── non-compete-clauses.jsonl
│   │
│   ├── legal-citations/
│   │   ├── us-case-citations.csv            # ~1000 examples
│   │   ├── us-statute-citations.csv
│   │   ├── eu-case-citations.csv
│   │   └── uk-case-citations.csv
│   │
│   └── test-documents/
│       ├── sample-nda.pdf
│       ├── sample-nda.md                    # Markdown version
│       ├── sample-msa.pdf
│       ├── sample-employment-agreement.pdf
│       ├── sample-lease.pdf
│       └── sample-terms-of-service.md
│
│ ══════════════════════════════════════════════════════════════════════
│ LINKED RESOURCES (Curated External References)
│ ══════════════════════════════════════════════════════════════════════
│
├── tools/
│   ├── README.md                       # Tool selection guide
│   │
│   ├── nlp/
│   │   ├── lexnlp.yaml                 # LexPredict/LexNLP
│   │   ├── blackstone.yaml             # ICL Blackstone
│   │   ├── legal-bert.yaml             # Legal-BERT models
│   │   ├── spacy-legal.yaml            # spaCy for legal text
│   │   ├── eyecite.yaml                # Citation extraction
│   │   └── legal-sbert.yaml            # Sentence transformers
│   │
│   ├── document-processing/
│   │   ├── docassemble.yaml            # Document automation
│   │   ├── pdfplumber.yaml             # PDF extraction
│   │   ├── unstructured.yaml           # Universal doc parser
│   │   ├── marker-pdf.yaml             # PDF to markdown
│   │   └── camelot.yaml                # Table extraction
│   │
│   ├── automation/
│   │   ├── accord-project.yaml         # Smart legal contracts
│   │   ├── hotdocs.yaml                # Document assembly
│   │   └── contract-express.yaml       # Contract automation
│   │
│   └── research/
│       ├── courtlistener-api.yaml      # Free US case law API
│       ├── caselaw-access-project.yaml # Harvard case law
│       ├── eurlex-api.yaml             # EU legislation
│       └── google-scholar-legal.yaml   # Legal academic search
│
├── datasets/
│   ├── README.md                       # Dataset selection guide
│   │
│   ├── contracts/
│   │   ├── cuad.yaml                   # Contract Understanding Atticus
│   │   ├── atticus.yaml                # Atticus project contracts
│   │   ├── contract-nli.yaml           # Contract NLI dataset
│   │   └── maud.yaml                   # M&A contract dataset
│   │
│   ├── case-law/
│   │   ├── casehold.yaml               # CaseHOLD benchmark
│   │   ├── scotus-opinions.yaml        # Supreme Court opinions
│   │   ├── courtlistener-bulk.yaml     # Bulk case law download
│   │   ├── echr-cases.yaml             # European Court of HR
│   │   └── caselaw-access.yaml         # Harvard Law case corpus
│   │
│   ├── legislation/
│   │   ├── us-code.yaml                # US Code dataset
│   │   ├── eurlex-corpus.yaml          # EU legislation corpus
│   │   └── uk-legislation.yaml         # UK legislation dataset
│   │
│   └── benchmarks/
│       ├── legalbench.yaml             # Legal reasoning benchmark
│       ├── lexglue.yaml                # Legal NLU benchmark
│       ├── legal-lama.yaml             # Legal knowledge probing
│       └── legal-qa.yaml               # Legal Q&A benchmarks
│
├── models/
│   ├── README.md                       # Model selection guide
│   │
│   ├── embeddings/
│   │   ├── comparison.md               # Benchmark comparison table
│   │   ├── legal-bert.yaml
│   │   ├── legal-sbert.yaml
│   │   ├── bge-legal.yaml
│   │   ├── e5-legal.yaml
│   │   └── openai-embeddings.yaml
│   │
│   └── llm-benchmarks/
│       └── legal-task-performance.md   # LLM performance on legal tasks
│
└── docs/
    ├── getting-started.md              # Quick start guide
    ├── faq.md                          # Frequently asked questions
    │
    ├── use-cases/
    │   ├── contract-review-pipeline.md
    │   ├── legal-research-assistant.md
    │   ├── compliance-automation.md
    │   ├── due-diligence-workflow.md
    │   └── document-drafting-system.md
    │
    └── contributing/
        ├── prompt-guidelines.md        # How to write good legal prompts
        ├── workflow-guidelines.md      # How to structure workflows
        └── quality-standards.md        # What we accept
```

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
