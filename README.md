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
| [**System Prompts**](./prompts/system-prompts/) | 25+ | Ready-to-use AI personas for legal tasks |
| [**Prompt Templates**](./prompts/prompt-templates/) | 15+ | Fill-in-the-blank prompts for common operations |
| [**Workflows**](./workflows/) | 12+ | Importable automation definitions |
| [**MCP Configs**](./mcp-configs/) | 8+ | Claude Desktop and server configurations |
| [**Tools**](./tools/) | 20+ | Curated links to legal NLP libraries |
| [**Datasets**](./datasets/) | 15+ | Links to training and evaluation data |
| [**Code Snippets**](./code-snippets/) | 15+ | Python/TypeScript utilities |
| [**Sample Data**](./sample-data/) | Various | Example clauses, citations, documents |

## Hosted vs. Linked Resources

### Directly Downloadable (Hosted)
- System prompts and prompt templates (`.md`, `.txt`)
- Workflow definitions (`.json`, `.yaml`)
- MCP server configurations (`.json`)
- Code snippets (`.py`, `.ts`)
- Sample datasets (`.csv`, `.jsonl`)

### External References (Linked)
- Full tools (LexNLP, Docassemble, etc.)
- Large datasets (CUAD, CaseHOLD, LegalBench)
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
| [Contract Comparison](./workflows/contract-comparison/) | Compare two contracts and highlight differences | QueryLex, n8n |
| [Due Diligence](./workflows/due-diligence/) | Generate DD checklists from company info | QueryLex |
| [Legal Memo Generator](./workflows/legal-memo/) | Structured memo from research query | Any |

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
curl -O https://raw.githubusercontent.com/AndriusPetrenas/UltimateLegalAILibrary/main/workflows/contract-comparison/workflow.json

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
