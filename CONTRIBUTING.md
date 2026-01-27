# Contributing to Ultimate Legal AI Library

Thank you for your interest in contributing! This document provides guidelines for contributing resources to the library.

## Types of Contributions

### 1. System Prompts

Well-crafted AI prompts for specific legal tasks.

**Requirements:**
- Tested with at least one major LLM (GPT-4, Claude, Gemini)
- Clear use case description
- Example inputs and outputs
- No hallucination-prone instructions

**Structure:**
```
prompts/system-prompts/your-prompt-name/
├── metadata.yaml     # Required: prompt metadata
├── prompt.md         # Required: the actual prompt
├── README.md         # Required: usage guide
└── examples/         # Optional: example conversations
    ├── input-1.txt
    └── output-1.txt
```

### 2. Prompt Templates

Fill-in-the-blank prompts for common operations.

**Structure:**
```
prompts/prompt-templates/template-name.md
```

Use `{{VARIABLE}}` syntax for placeholders.

### 3. Workflows

Automation definitions that can be imported into workflow engines.

**Requirements:**
- JSON or YAML format
- Compatible with QueryLex or n8n
- Well-documented nodes and connections
- No hardcoded API keys

**Structure:**
```
workflows/workflow-name/
├── metadata.yaml     # Required: workflow metadata
├── workflow.json     # Required: the workflow definition
├── README.md         # Required: setup instructions
└── diagram.png       # Optional: visual representation
```

### 4. Tool Links

Curated references to external legal NLP tools.

**Requirements:**
- Honest evaluation with strengths and weaknesses
- Installation instructions
- License information

**Structure:**
```
tools/category/tool-name.yaml
```

### 5. Dataset Links

References to legal datasets for training and evaluation.

**Requirements:**
- Clear description of contents
- Size and format information
- License and citation requirements
- Download/access instructions

### 6. Code Snippets

Utility functions for legal text processing.

**Requirements:**
- Well-commented code
- Type hints (Python) or TypeScript types
- No external dependencies or clearly documented ones
- Example usage

## Submission Process

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/UltimateLegalAILibrary.git
cd UltimateLegalAILibrary
```

### 2. Create a Branch

```bash
git checkout -b add-contract-analyst-prompt
```

### 3. Add Your Resource

Follow the structure guidelines above.

### 4. Validate

Ensure your metadata.yaml is valid:

```bash
# Install validator (optional)
pip install pyyaml jsonschema

# Validate
python scripts/validate.py your-resource-path
```

### 5. Submit Pull Request

- Use a clear, descriptive title
- Fill out the PR template
- Reference any related issues

## Metadata Schema

### Prompts

```yaml
name: "Your Prompt Name"
slug: your-prompt-name           # URL-safe identifier
type: system-prompt              # system-prompt | prompt-template | few-shot

description: >
  A clear description of what this prompt does.

target_model: claude-3           # claude-3 | gpt-4 | any
input_type: document             # document | text | structured
output_format: structured-json   # text | structured-json | markdown
token_estimate: 2500             # Approximate token count

domain: contracts                # contracts | litigation | compliance | research
tasks:
  - clause-identification
  - risk-assessment

jurisdiction: multi              # multi | us | uk | eu | [specific]

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
  - gpt-4o
```

### Tools

```yaml
name: "Tool Name"
slug: tool-name
type: tool-link

description: >
  What this tool does.

repository: https://github.com/org/repo
documentation: https://docs.example.com
pypi: package-name                # if Python
npm: package-name                 # if JavaScript

language: python                  # python | javascript | go | etc.
install_command: "pip install package-name"
license: MIT

our_evaluation:
  strengths:
    - "Clear strength 1"
    - "Clear strength 2"
  weaknesses:
    - "Honest weakness 1"
  best_for:
    - "Use case 1"
  alternatives:
    - other-tool-slug

category: nlp
subcategory: extraction
tags:
  - ner
  - contracts
```

## Quality Standards

### Do
- Test your resources before submitting
- Provide honest evaluations
- Include clear documentation
- Respect licenses and attribution
- Use descriptive file names

### Don't
- Submit untested prompts
- Include real client data
- Hardcode API keys or secrets
- Copy content without attribution
- Submit resources with restrictive licenses as CC0

## Code of Conduct

- Be respectful and constructive
- Focus on improving legal AI for everyone
- Give credit where credit is due
- Report issues rather than criticizing contributors

## Questions?

- Open a [Discussion](https://github.com/AndriusPetrenas/UltimateLegalAILibrary/discussions)
- Check existing [Issues](https://github.com/AndriusPetrenas/UltimateLegalAILibrary/issues)

Thank you for contributing!
