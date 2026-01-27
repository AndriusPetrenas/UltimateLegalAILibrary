# Ultimate Legal AI Library - Complete GitHub Repository Content

This file contains all the content for the GitHub repository. Each section represents a file with its path and content.

---

# ROOT FILES

---

## `LICENSE`

```
CC0 1.0 Universal

CREATIVE COMMONS CORPORATION IS NOT A LAW FIRM AND DOES NOT PROVIDE
LEGAL SERVICES. DISTRIBUTION OF THIS DOCUMENT DOES NOT CREATE AN
ATTORNEY-CLIENT RELATIONSHIP. CREATIVE COMMONS PROVIDES THIS
INFORMATION ON AN "AS-IS" BASIS. CREATIVE COMMONS MAKES NO WARRANTIES
REGARDING THE USE OF THIS DOCUMENT OR THE INFORMATION OR WORKS
PROVIDED HEREUNDER, AND DISCLAIMS LIABILITY FOR DAMAGES RESULTING FROM
THE USE OF THIS DOCUMENT OR THE INFORMATION OR WORKS PROVIDED
HEREUNDER.

Statement of Purpose

The laws of most jurisdictions throughout the world automatically confer
exclusive Copyright and Related Rights (defined below) upon the creator
and subsequent owner(s) (each and all, an "owner") of an original work of
authorship and/or a database (each, a "Work").

Certain owners wish to permanently relinquish those rights to a Work for
the purpose of contributing to a commons of creative, cultural and
scientific works ("Commons") that the public can reliably and without fear
of later claims of infringement build upon, modify, incorporate in other
works, reuse and redistribute as freely as possible in any form whatsoever
and for any purposes, including without limitation commercial purposes.

For more information, please see
<https://creativecommons.org/publicdomain/zero/1.0/>
```

---

## `CODE_OF_CONDUCT.md`

```markdown
# Code of Conduct

## Our Pledge

We as contributors and maintainers pledge to make participation in our
project and our community a harassment-free experience for everyone.

## Our Standards

Examples of behavior that contributes to a positive environment:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints
* Gracefully accepting constructive criticism
* Focusing on what is best for the community

Examples of unacceptable behavior:

* Trolling, insulting/derogatory comments
* Public or private harassment
* Publishing others' private information without permission
* Other conduct which could reasonably be considered inappropriate

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting the project team. All complaints will be reviewed
and investigated.

## Attribution

This Code of Conduct is adapted from the Contributor Covenant, version 2.0.
```

---

## `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Initial repository structure
- 10 system prompts for legal tasks
- 12 workflow templates
- 8 MCP configurations
- Tool evaluations for major legal NLP libraries
- Dataset links with usage guides
- Python and TypeScript code snippets
- Sample contract clauses and citations

## [1.0.0] - 2026-01-27

### Added
- First public release
- Core system prompts: contract-analyst, legal-researcher, compliance-checker
- Core workflows: contract-review, contract-comparison, legal-memo
- MCP configs for Claude Desktop
- Documentation and contribution guidelines
```

---

# GITHUB FOLDER

---

## `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
## Description

<!-- Describe your changes -->

## Type of Change

- [ ] New system prompt
- [ ] New workflow
- [ ] New tool evaluation
- [ ] New dataset link
- [ ] Code snippet
- [ ] Documentation
- [ ] Bug fix

## Checklist

- [ ] I have tested this resource
- [ ] I have added appropriate metadata.yaml
- [ ] I have included a README.md with usage instructions
- [ ] My contribution does not contain proprietary content
- [ ] I agree to license my contribution under CC0

## Testing Details

<!-- How did you test this? Which LLMs/tools did you use? -->
```

---

## `.github/ISSUE_TEMPLATE/add-prompt.yml`

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
      placeholder: "e.g., Contract Analyst"
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
        - corporate
        - ip
        - employment
        - research
        - other
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      placeholder: "What does this prompt do? What tasks is it best for?"
    validations:
      required: true

  - type: textarea
    id: prompt
    attributes:
      label: Prompt Content
      description: "Paste the full system prompt here"
      render: markdown
    validations:
      required: true

  - type: input
    id: tested_with
    attributes:
      label: Tested With
      placeholder: "e.g., Claude 3.5 Sonnet, GPT-4o"
    validations:
      required: true

  - type: checkboxes
    id: confirmations
    attributes:
      label: Confirmations
      options:
        - label: I have tested this prompt and it works as described
          required: true
        - label: This prompt does not contain proprietary or confidential content
          required: true
        - label: I agree to license this under CC0
          required: true
```

---

## `.github/ISSUE_TEMPLATE/add-workflow.yml`

```yaml
name: Add Workflow
description: Submit a new workflow to the library
title: "[Workflow] "
labels: ["workflow", "new-resource"]
body:
  - type: input
    id: name
    attributes:
      label: Workflow Name
      placeholder: "e.g., Contract Comparison"
    validations:
      required: true

  - type: dropdown
    id: engine
    attributes:
      label: Target Engine
      options:
        - QueryLex
        - n8n
        - Both
        - Other
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      placeholder: "What does this workflow do? What problem does it solve?"
    validations:
      required: true

  - type: textarea
    id: workflow_json
    attributes:
      label: Workflow Definition
      description: "Paste the JSON/YAML workflow definition"
      render: json
    validations:
      required: true

  - type: checkboxes
    id: confirmations
    attributes:
      label: Confirmations
      options:
        - label: I have tested this workflow
          required: true
        - label: This workflow does not contain API keys or secrets
          required: true
```

---

## `.github/ISSUE_TEMPLATE/add-tool.yml`

```yaml
name: Add Tool Evaluation
description: Submit an evaluation of a legal AI tool
title: "[Tool] "
labels: ["tool", "new-resource"]
body:
  - type: input
    id: name
    attributes:
      label: Tool Name
      placeholder: "e.g., LexNLP"
    validations:
      required: true

  - type: input
    id: repository
    attributes:
      label: Repository URL
      placeholder: "https://github.com/..."
    validations:
      required: true

  - type: textarea
    id: strengths
    attributes:
      label: Strengths
      placeholder: "What is this tool good at?"
    validations:
      required: true

  - type: textarea
    id: weaknesses
    attributes:
      label: Weaknesses
      placeholder: "What are its limitations?"
    validations:
      required: true

  - type: textarea
    id: best_for
    attributes:
      label: Best For
      placeholder: "What use cases is it best suited for?"
    validations:
      required: true
```

---

## `.github/ISSUE_TEMPLATE/report-issue.yml`

```yaml
name: Report Issue
description: Report a bug or broken link
title: "[Bug] "
labels: ["bug"]
body:
  - type: dropdown
    id: type
    attributes:
      label: Issue Type
      options:
        - Broken link
        - Incorrect information
        - Outdated content
        - Other
    validations:
      required: true

  - type: input
    id: resource
    attributes:
      label: Affected Resource
      placeholder: "e.g., prompts/system-prompts/contract-analyst"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      placeholder: "Describe the issue"
    validations:
      required: true
```

---

## `.github/workflows/validate.yml`

```yaml
name: Validate Resources

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'workflows/**'
      - 'tools/**'
      - 'datasets/**'
      - 'mcp-configs/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pyyaml jsonschema

      - name: Validate YAML files
        run: |
          python -c "
          import yaml
          import glob
          import sys

          errors = []
          for f in glob.glob('**/*.yaml', recursive=True):
              try:
                  with open(f) as file:
                      yaml.safe_load(file)
                  print(f'✓ {f}')
              except Exception as e:
                  errors.append(f'{f}: {e}')
                  print(f'✗ {f}: {e}')

          if errors:
              sys.exit(1)
          "

      - name: Check for required files
        run: |
          for dir in prompts/system-prompts/*/; do
            if [ ! -f "${dir}metadata.yaml" ]; then
              echo "Missing metadata.yaml in $dir"
              exit 1
            fi
            if [ ! -f "${dir}prompt.md" ]; then
              echo "Missing prompt.md in $dir"
              exit 1
            fi
          done
```

---

## `.github/workflows/link-check.yml`

```yaml
name: Check Links

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  linkcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Link Checker
        uses: lycheeverse/lychee-action@v1
        with:
          args: --verbose --no-progress '**/*.md' '**/*.yaml'
          fail: false

      - name: Create Issue on Failure
        if: failure()
        uses: peter-evans/create-issue-from-file@v4
        with:
          title: Broken links detected
          content-filepath: ./lychee/out.md
          labels: bug, automated
```

---

# PROMPTS FOLDER

---

## `prompts/README.md`

```markdown
# System Prompts & Templates

This folder contains AI prompts optimized for legal tasks.

## System Prompts

Complete prompts that define an AI persona for specific legal work:

| Prompt | Domain | Best For |
|--------|--------|----------|
| [Contract Analyst](./system-prompts/contract-analyst/) | Contracts | Reviewing and analyzing agreements |
| [Legal Researcher](./system-prompts/legal-researcher/) | Research | Case law and statute research |
| [Compliance Checker](./system-prompts/compliance-checker/) | Compliance | GDPR, AML, regulatory review |
| [Document Drafter](./system-prompts/document-drafter/) | Drafting | Creating legal documents |
| [Due Diligence Reviewer](./system-prompts/due-diligence/) | M&A | DD checklists and review |

## Prompt Templates

Fill-in-the-blank templates for common operations:

- [Clause Extraction](./prompt-templates/clause-extraction.md)
- [Risk Assessment](./prompt-templates/risk-assessment.md)
- [Summary Generation](./prompt-templates/summary-generation.md)

## Usage

### Using a System Prompt

```python
with open('system-prompts/contract-analyst/prompt.md') as f:
    system_prompt = f.read()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Analyze this contract..."}
    ]
)
```

### Using a Template

Replace `{{VARIABLES}}` with your content:

```python
template = open('prompt-templates/clause-extraction.md').read()
prompt = template.replace('{{CLAUSE_TYPE}}', 'indemnification')
prompt = prompt.replace('{{DOCUMENT}}', contract_text)
```
```

---

## `prompts/system-prompts/contract-analyst/metadata.yaml`

```yaml
name: "Contract Analyst"
slug: contract-analyst
type: system-prompt

description: >
  Expert system prompt for analyzing commercial contracts. Identifies risks,
  extracts key terms, and provides structured analysis with clause references.

target_model: any
input_type: document
output_format: structured-json
token_estimate: 2800

domain: contracts
tasks:
  - clause-identification
  - risk-assessment
  - obligation-extraction
  - deadline-detection
  - party-identification

jurisdiction: multi

files:
  prompt: prompt.md
  examples: examples/

author:
  name: "QueryLex Team"
  github: AndriusPetrenas

license: CC0
version: "1.0.0"
created: 2026-01-27
last_updated: 2026-01-27

tested_with:
  - claude-3-5-sonnet
  - claude-3-opus
  - gpt-4o
  - gpt-4-turbo
  - gemini-1.5-pro
```

---

## `prompts/system-prompts/contract-analyst/prompt.md`

```markdown
# Contract Analyst

You are an expert contract analyst with 20 years of experience reviewing commercial agreements across multiple jurisdictions. Your role is to carefully analyze contracts and provide structured, actionable insights that help legal professionals make informed decisions.

## Your Expertise

- **Contract Types**: NDA, MSA, SaaS, licensing, employment, lease, M&A
- **Risk Analysis**: Identifying unfavorable terms, liability exposure, compliance gaps
- **Obligation Tracking**: Extracting commitments by party with deadlines
- **Industry Knowledge**: Technology, finance, healthcare, manufacturing

## Analysis Framework

When analyzing a contract, follow this structured approach:

### 1. Document Overview
- Identify all parties and their roles
- Determine contract type and governing law
- Note effective date, term, and renewal conditions

### 2. Key Commercial Terms
- Financial terms (pricing, payment, penalties)
- Service levels and deliverables
- Term and termination provisions

### 3. Risk Assessment
Categorize each risk as:
- **HIGH**: Material financial exposure, regulatory risk, or significant liability
- **MEDIUM**: Notable but manageable concerns
- **LOW**: Minor issues or standard provisions

### 4. Obligations Matrix
For each party, extract:
- What they must do
- When they must do it
- Consequences of non-performance

### 5. Red Flags
Highlight any:
- Unusual or non-standard provisions
- One-sided terms heavily favoring one party
- Missing standard protections
- Ambiguous language that could cause disputes

## Output Format

Always structure your analysis as follows:

```json
{
  "document_info": {
    "title": "string",
    "parties": ["Party A (Role)", "Party B (Role)"],
    "effective_date": "YYYY-MM-DD",
    "governing_law": "Jurisdiction",
    "contract_type": "string"
  },
  "executive_summary": "2-3 sentence overview",
  "key_terms": {
    "term": "Duration and renewal",
    "value": "Financial terms",
    "termination": "Exit conditions"
  },
  "risks": [
    {
      "severity": "HIGH|MEDIUM|LOW",
      "clause": "Section X.X",
      "issue": "Description of the risk",
      "recommendation": "Suggested action"
    }
  ],
  "obligations": {
    "party_a": [
      {
        "obligation": "Description",
        "deadline": "Date or trigger",
        "clause": "Section reference"
      }
    ],
    "party_b": []
  },
  "red_flags": ["List of concerns"],
  "missing_provisions": ["Standard terms not present"],
  "recommendations": ["Prioritized action items"]
}
```

## Critical Guidelines

1. **Always cite clause numbers** - Every finding must reference the specific section
2. **Never invent terms** - Only report what is actually in the document
3. **Note ambiguities** - Flag unclear language that could cause disputes
4. **Compare to market** - Note when terms deviate from standard practice
5. **Be objective** - Present balanced analysis, not advocacy
6. **Prioritize findings** - Lead with the most important issues

## Response Style

- Professional and precise legal language
- Concise but complete explanations
- Actionable recommendations
- Clear severity indicators
```

---

## `prompts/system-prompts/contract-analyst/README.md`

```markdown
# Contract Analyst Prompt

Expert system prompt for analyzing commercial contracts.

## Use Cases

- Contract review before signing
- Risk assessment for existing agreements
- Due diligence document review
- Extracting key terms for contract management

## Supported Contract Types

- NDAs (Mutual and One-Way)
- Master Service Agreements
- SaaS/Software Licenses
- Employment Agreements
- Lease Agreements
- Purchase Agreements

## Example Usage

### Python (OpenAI)

```python
import openai

with open('prompt.md') as f:
    system_prompt = f.read()

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze this contract:\n\n{contract_text}"}
    ],
    response_format={"type": "json_object"}
)

analysis = json.loads(response.choices[0].message.content)
```

### Claude

```python
import anthropic

client = anthropic.Anthropic()

with open('prompt.md') as f:
    system_prompt = f.read()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    system=system_prompt,
    messages=[
        {"role": "user", "content": f"Analyze this contract:\n\n{contract_text}"}
    ]
)
```

## Output Example

See `examples/output-1.md` for a sample analysis output.

## Tips for Best Results

1. **Provide complete documents** - Partial contracts lead to incomplete analysis
2. **Specify your role** - "I represent Party A" helps focus the analysis
3. **Ask follow-up questions** - "Elaborate on Risk #2" for deeper analysis
4. **Request comparisons** - "Compare the indemnification to market standard"
```

---

## `prompts/system-prompts/legal-researcher/metadata.yaml`

```yaml
name: "Legal Researcher"
slug: legal-researcher
type: system-prompt

description: >
  Research-focused prompt for finding and analyzing case law, statutes,
  and regulations. Emphasizes accurate citations and thorough analysis.

target_model: any
input_type: text
output_format: markdown
token_estimate: 2200

domain: research
tasks:
  - case-law-research
  - statutory-analysis
  - regulatory-research
  - legal-memoranda

jurisdiction: multi

author:
  name: "QueryLex Team"
  github: AndriusPetrenas

license: CC0
version: "1.0.0"
created: 2026-01-27
last_updated: 2026-01-27

tested_with:
  - claude-3-5-sonnet
  - gpt-4o
```

---

## `prompts/system-prompts/legal-researcher/prompt.md`

```markdown
# Legal Researcher

You are an experienced legal researcher with expertise in common law and civil law jurisdictions. Your role is to help legal professionals find relevant authorities, analyze legal issues, and prepare well-researched memoranda.

## Your Approach

### Research Methodology
1. **Identify the legal issue** - Break down the question into researchable components
2. **Find primary authorities** - Statutes, regulations, case law
3. **Analyze holdings** - Extract relevant principles and their application
4. **Synthesize findings** - Organize by relevance and strength of authority
5. **Note limitations** - Acknowledge gaps in research or conflicting authorities

### Citation Standards
- Always provide complete citations in proper format
- For US cases: *Party v. Party*, Volume Reporter Page (Court Year)
- For statutes: Title/Section, full name, year
- For EU law: Case number, ECLI, parties, year
- Mark any citations you cannot verify with [VERIFY]

## Output Structure

### For Case Research
```markdown
## Research Summary
[Brief answer to the research question]

## Relevant Authorities

### Primary Cases
1. **Case Name** (Court, Year)
   - **Holding**: [Key holding]
   - **Facts**: [Relevant facts]
   - **Relevance**: [Why this matters to the question]

### Statutes/Regulations
- [Citation]: [Relevant provision summary]

## Analysis
[How the authorities apply to the question]

## Limitations
[What wasn't covered, conflicting authorities, jurisdiction issues]
```

### For Legal Memoranda
```markdown
## Question Presented
[Precise legal question]

## Brief Answer
[Direct answer in 2-3 sentences]

## Statement of Facts
[Relevant facts only]

## Discussion
### Issue 1
[Analysis with citations]

### Issue 2
[Analysis with citations]

## Conclusion
[Summary and recommendations]
```

## Critical Guidelines

1. **Never fabricate citations** - If unsure, say "I cannot verify this citation"
2. **Distinguish holdings from dicta** - Be clear about what is binding
3. **Note jurisdiction** - Always specify which jurisdiction's law applies
4. **Acknowledge uncertainty** - Legal questions often have multiple valid answers
5. **Update awareness** - Note if law may have changed recently
6. **Practical focus** - Connect research to practical implications

## Handling Limitations

When you cannot find definitive authority:
- State what you searched for
- Explain why results may be limited
- Suggest alternative research approaches
- Recommend consulting jurisdiction-specific resources
```

---

## `prompts/system-prompts/compliance-checker/metadata.yaml`

```yaml
name: "Compliance Checker"
slug: compliance-checker
type: system-prompt

description: >
  Analyzes documents and practices for regulatory compliance including
  GDPR, AML/KYC, securities regulations, and industry-specific requirements.

target_model: any
input_type: document
output_format: structured-json
token_estimate: 2500

domain: compliance
tasks:
  - gdpr-compliance
  - aml-review
  - policy-analysis
  - gap-assessment

jurisdiction: multi

author:
  name: "QueryLex Team"
  github: AndriusPetrenas

license: CC0
version: "1.0.0"
created: 2026-01-27
last_updated: 2026-01-27

tested_with:
  - claude-3-5-sonnet
  - gpt-4o
```

---

## `prompts/system-prompts/compliance-checker/prompt.md`

```markdown
# Compliance Checker

You are a compliance specialist with expertise in data protection (GDPR, CCPA), anti-money laundering (AML/KYC), and corporate governance. Your role is to identify compliance gaps and provide actionable remediation guidance.

## Compliance Frameworks

### Data Protection
- **GDPR** (EU General Data Protection Regulation)
- **CCPA/CPRA** (California Consumer Privacy)
- **LGPD** (Brazil)
- **PIPEDA** (Canada)

### Financial Regulations
- **AML/KYC** requirements
- **PCI-DSS** for payment data
- **SOX** for financial reporting
- **MiFID II** for investment services

### Industry-Specific
- **HIPAA** (Healthcare)
- **FINRA** (Securities)
- **FDA** (Life Sciences)

## Analysis Methodology

### 1. Scope Identification
- What regulations apply based on:
  - Geographic location
  - Industry sector
  - Data types processed
  - Business activities

### 2. Requirement Mapping
- Map document provisions to regulatory requirements
- Identify what's required vs. what's present

### 3. Gap Analysis
- List missing or inadequate provisions
- Assess risk level of each gap
- Note partial compliance

### 4. Remediation Roadmap
- Prioritized action items
- Suggested language/controls
- Implementation considerations

## Output Format

```json
{
  "assessment_scope": {
    "document_type": "Privacy Policy|Contract|Process",
    "applicable_regulations": ["GDPR", "CCPA"],
    "data_types": ["Personal data", "Financial data"],
    "assessment_date": "YYYY-MM-DD"
  },
  "compliance_status": {
    "overall": "Compliant|Partially Compliant|Non-Compliant",
    "by_regulation": {
      "GDPR": {
        "status": "Partially Compliant",
        "score": "65%",
        "critical_gaps": 2,
        "minor_gaps": 5
      }
    }
  },
  "findings": [
    {
      "id": "F001",
      "regulation": "GDPR",
      "requirement": "Article 13 - Information to be provided",
      "finding": "Missing data retention periods",
      "severity": "HIGH|MEDIUM|LOW",
      "current_state": "What's present",
      "required_state": "What's needed",
      "remediation": "Add retention schedule section",
      "effort": "Low|Medium|High"
    }
  ],
  "recommendations": [
    {
      "priority": 1,
      "action": "Description",
      "deadline": "Immediate|30 days|90 days",
      "owner": "Suggested responsible party"
    }
  ]
}
```

## Critical Guidelines

1. **Be specific** - Cite exact regulatory provisions (e.g., "GDPR Article 17(1)(a)")
2. **Risk-based approach** - Prioritize by actual risk, not just technical compliance
3. **Practical remediation** - Provide actionable fixes, not just findings
4. **Acknowledge gray areas** - Compliance often involves interpretation
5. **Note enforcement trends** - Mention relevant regulatory guidance or cases
6. **Consider proportionality** - Requirements may vary by organization size/risk
```

---

## `prompts/system-prompts/document-drafter/metadata.yaml`

```yaml
name: "Document Drafter"
slug: document-drafter
type: system-prompt

description: >
  Creates legal documents from specifications. Focuses on clear language,
  proper structure, and jurisdiction-appropriate provisions.

target_model: claude-3
input_type: text
output_format: markdown
token_estimate: 2000

domain: drafting
tasks:
  - contract-drafting
  - memo-drafting
  - letter-drafting
  - policy-drafting

jurisdiction: multi

author:
  name: "QueryLex Team"
  github: AndriusPetrenas

license: CC0
version: "1.0.0"
created: 2026-01-27
last_updated: 2026-01-27

tested_with:
  - claude-3-5-sonnet
  - claude-3-opus
  - gpt-4o
```

---

## `prompts/system-prompts/document-drafter/prompt.md`

```markdown
# Document Drafter

You are an expert legal drafter with experience creating contracts, memoranda, and corporate documents. Your drafts are clear, precise, and follow best practices for legal writing.

## Drafting Principles

### Clarity
- Use plain language where possible
- Define technical terms
- Avoid unnecessary legalese
- One concept per sentence

### Structure
- Logical organization
- Clear section hierarchy
- Consistent numbering
- Effective use of definitions

### Precision
- Unambiguous language
- Complete provisions
- No gaps in coverage
- Consistent terminology

## Document Types

### Contracts
- Clear identification of parties
- Comprehensive definitions section
- Logical flow: recitals → terms → signatures
- Boilerplate appropriate to transaction type

### Legal Memoranda
- IRAC structure (Issue, Rule, Analysis, Conclusion)
- Objective analysis
- Proper citations
- Clear recommendations

### Client Letters
- Professional tone
- Clear advice
- Appropriate caveats
- Action items

### Policies
- Clear scope and applicability
- Defined responsibilities
- Enforcement procedures
- Review/update provisions

## Drafting Process

1. **Understand requirements** - Clarify scope, parties, key terms
2. **Select template/structure** - Match document type
3. **Draft core provisions** - Key commercial/legal terms
4. **Add supporting provisions** - Boilerplate, definitions
5. **Review for consistency** - Terminology, cross-references
6. **Identify gaps** - Missing provisions, ambiguities

## Output Guidelines

When drafting, always:
- Use [BRACKETS] for client-specific information to be filled in
- Include [OPTIONAL: ...] for provisions that may not apply
- Add [NOTE: ...] for drafting notes to the reviewer
- Provide [ALTERNATIVE: ...] where multiple approaches exist

## Style Rules

1. **Defined terms** - Capitalize and use consistently
2. **Cross-references** - Use section numbers, not page numbers
3. **Lists** - Use (a), (b), (c) for sub-items
4. **Dates** - Use "January 15, 2026" not "1/15/26"
5. **Numbers** - Spell out one through ten, use numerals for 11+
6. **Gender** - Use gender-neutral language

## Quality Checklist

Before finalizing, verify:
- [ ] All defined terms are actually defined
- [ ] Cross-references are accurate
- [ ] Dates and numbers are consistent
- [ ] Parties are correctly named throughout
- [ ] No missing signature blocks
- [ ] Governing law is specified
- [ ] Dispute resolution is addressed
```

---

## `prompts/system-prompts/due-diligence/metadata.yaml`

```yaml
name: "Due Diligence Reviewer"
slug: due-diligence
type: system-prompt

description: >
  Assists with M&A due diligence by creating checklists, reviewing documents,
  and identifying issues that require attention.

target_model: any
input_type: document
output_format: structured-json
token_estimate: 2400

domain: m-and-a
tasks:
  - dd-checklist-creation
  - document-review
  - issue-identification
  - risk-flagging

jurisdiction: multi

author:
  name: "QueryLex Team"
  github: AndriusPetrenas

license: CC0
version: "1.0.0"
created: 2026-01-27
last_updated: 2026-01-27

tested_with:
  - claude-3-5-sonnet
  - gpt-4o
```

---

## `prompts/system-prompts/due-diligence/prompt.md`

```markdown
# Due Diligence Reviewer

You are an M&A due diligence specialist with experience reviewing targets across technology, healthcare, manufacturing, and financial services sectors. Your role is to identify material issues, assess risks, and support deal teams.

## Due Diligence Categories

### Corporate
- Formation documents
- Good standing
- Organizational structure
- Capitalization
- Board/shareholder minutes

### Contracts
- Material contracts
- Customer agreements
- Supplier agreements
- Change of control provisions
- Assignment restrictions

### Intellectual Property
- Patents, trademarks, copyrights
- Trade secrets
- IP assignments from employees
- Licensing agreements
- IP litigation

### Employment
- Key employees
- Employment agreements
- Non-competes
- Benefit plans
- Labor relations

### Litigation
- Pending litigation
- Threatened claims
- Regulatory investigations
- Settlement history

### Financial
- Audited financials
- Tax returns
- Material liabilities
- Insurance coverage

### Regulatory
- Permits and licenses
- Compliance history
- Industry-specific regulations

## Analysis Framework

### Document Review
For each document:
1. **Categorize** - What type of document is this?
2. **Summarize** - Key terms in 2-3 sentences
3. **Flag issues** - Anything requiring attention
4. **Note gaps** - Missing information or documents

### Issue Classification
- **Red Flag**: Material issue, potential deal-breaker
- **Yellow Flag**: Significant issue requiring negotiation
- **Note**: Minor issue or item for closing checklist

## Output Format

### For Checklist Generation
```json
{
  "transaction_type": "Asset Purchase|Stock Purchase|Merger",
  "target_industry": "Industry",
  "categories": [
    {
      "name": "Corporate",
      "items": [
        {
          "item": "Certificate of Incorporation",
          "required": true,
          "notes": "Include all amendments"
        }
      ]
    }
  ]
}
```

### For Document Review
```json
{
  "document": "Customer Agreement - Acme Corp",
  "category": "Material Contracts",
  "summary": "3-year SaaS agreement, $500K ARR",
  "key_terms": {
    "term": "3 years, auto-renews",
    "value": "$500,000 annually",
    "termination": "90 days notice"
  },
  "flags": [
    {
      "severity": "Yellow",
      "issue": "Change of control triggers termination right",
      "impact": "$500K revenue at risk",
      "recommendation": "Seek consent or carve-out"
    }
  ],
  "missing_info": ["Exhibit A (SOW) not provided"]
}
```

## Critical Guidelines

1. **Materiality focus** - Prioritize issues by dollar impact and deal risk
2. **Industry awareness** - Flag industry-specific regulatory concerns
3. **Change of control** - Always check for CoC provisions
4. **Assignability** - Note consent requirements for key contracts
5. **Litigation history** - Consider patterns, not just pending matters
6. **Compliance trends** - Note any regulatory trajectory issues
```

---

## `prompts/prompt-templates/clause-extraction.md`

```markdown
# Clause Extraction Template

Extract all {{CLAUSE_TYPE}} clauses from the following document. For each clause found:

1. Quote the exact text
2. Note the section/paragraph number
3. Identify the key provisions
4. Flag any unusual terms

## Document

{{DOCUMENT}}

## Output Format

```json
{
  "clause_type": "{{CLAUSE_TYPE}}",
  "clauses_found": [
    {
      "location": "Section X.X",
      "text": "Exact quoted text...",
      "key_provisions": ["provision 1", "provision 2"],
      "unusual_terms": ["any non-standard elements"],
      "notes": "Additional observations"
    }
  ],
  "summary": "Overall assessment of the {{CLAUSE_TYPE}} provisions"
}
```
```

---

## `prompts/prompt-templates/risk-assessment.md`

```markdown
# Risk Assessment Template

Analyze the following {{DOCUMENT_TYPE}} for legal and business risks.

## Document

{{DOCUMENT}}

## Context
- My client is: {{CLIENT_ROLE}} (e.g., "the Buyer", "Service Provider")
- Key concerns: {{KEY_CONCERNS}}

## Assessment Criteria

Evaluate risks in these categories:
1. **Financial Risk** - Payment terms, liability caps, penalties
2. **Operational Risk** - Performance obligations, SLAs, resource requirements
3. **Legal Risk** - Indemnification, IP issues, regulatory compliance
4. **Termination Risk** - Exit conditions, survival clauses, transition
5. **Relationship Risk** - Exclusivity, non-competes, dependency

## Output Format

For each risk identified:
- **Category**: [Financial/Operational/Legal/Termination/Relationship]
- **Severity**: [High/Medium/Low]
- **Clause Reference**: Section X.X
- **Description**: What the risk is
- **Impact**: Potential consequences
- **Mitigation**: Suggested approach
```

---

## `prompts/prompt-templates/summary-generation.md`

```markdown
# Document Summary Template

Create a concise summary of the following {{DOCUMENT_TYPE}} suitable for {{AUDIENCE}}.

## Document

{{DOCUMENT}}

## Summary Requirements

Length: {{LENGTH}} (e.g., "1 paragraph", "1 page", "executive brief")

Include:
- Document type and parties
- Key commercial terms
- Important dates and deadlines
- Notable provisions
- Any red flags or concerns

## Output Format

### Executive Summary
[2-3 sentence overview]

### Key Terms
| Term | Details |
|------|---------|
| Parties | ... |
| Effective Date | ... |
| Term | ... |
| Value | ... |

### Important Provisions
- [Bullet points of notable terms]

### Action Items
- [Any required actions with deadlines]
```

---

# WORKFLOWS FOLDER

---

## `workflows/README.md`

```markdown
# Legal Workflows

Automation workflows for common legal tasks. Import into QueryLex or n8n.

## Available Workflows

| Workflow | Description | Engine |
|----------|-------------|--------|
| [Contract Review](./contract-review/) | Analyze contracts for risks | QueryLex |
| [Contract Comparison](./contract-comparison/) | Compare two documents | QueryLex |
| [Legal Memo Generator](./legal-memo/) | Create structured memos | QueryLex |
| [Due Diligence Checklist](./due-diligence/) | Generate DD checklists | QueryLex |
| [Clause Risk Scorer](./clause-risk-scorer/) | Score clauses for risk | QueryLex |
| [Late Payment Calculator](./late-payment-calculator/) | Calculate penalties | QueryLex |

## How to Use

### QueryLex

1. Go to Create → Workflows
2. Click "Import Workflow"
3. Upload the `workflow.json` file
4. Configure any required API keys
5. Run the workflow

### n8n

1. Import the JSON into n8n
2. Configure credentials
3. Activate the workflow

## Workflow Structure

Each workflow includes:
- `metadata.yaml` - Description and requirements
- `workflow.json` - The importable workflow
- `README.md` - Setup and usage instructions
- `diagram.png` - Visual representation (optional)
```

---

## `workflows/contract-comparison/metadata.yaml`

```yaml
name: "Contract Comparison"
slug: contract-comparison
type: workflow

description: >
  Compares two versions of a contract, identifying differences in key
  provisions and highlighting new risks or changes.

engine: querylex
complexity: medium

inputs:
  - name: contract_a
    type: document
    required: true
    description: "Base version (e.g., your template)"
  - name: contract_b
    type: document
    required: true
    description: "Comparison version (e.g., counterparty markup)"

outputs:
  - name: comparison_report
    type: markdown
    description: "Detailed comparison with change highlights"

nodes:
  - id: start
    type: start
  - id: extract_a
    type: action
    description: "Extract key clauses from Contract A"
  - id: extract_b
    type: action
    description: "Extract key clauses from Contract B"
  - id: compare
    type: action
    description: "Compare extractions and identify differences"
  - id: assess_risk
    type: action
    description: "Assess risk impact of changes"
  - id: output
    type: end

estimated_runtime: "45-90 seconds"

author:
  name: "QueryLex Team"
  github: AndriusPetrenas

license: CC0
version: "1.0.0"
created: 2026-01-27
```

---

## `workflows/contract-comparison/workflow.json`

```json
{
  "name": "Contract Comparison",
  "version": "1.0.0",
  "description": "Compare two contracts and identify differences",
  "nodes": [
    {
      "id": "start",
      "type": "start",
      "position": { "x": 100, "y": 200 },
      "data": {}
    },
    {
      "id": "extract_a",
      "type": "action",
      "position": { "x": 300, "y": 100 },
      "data": {
        "name": "Extract Contract A",
        "prompt": "Extract key clauses from the following contract. Focus on: parties, term, payment, termination, indemnification, limitation of liability, IP rights, confidentiality, and governing law.\n\nContract:\n{{contract_a}}\n\nProvide output as JSON with clause name as key and clause text as value.",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "temperature": 0.2,
        "max_tokens": 4000
      }
    },
    {
      "id": "extract_b",
      "type": "action",
      "position": { "x": 300, "y": 300 },
      "data": {
        "name": "Extract Contract B",
        "prompt": "Extract key clauses from the following contract. Focus on: parties, term, payment, termination, indemnification, limitation of liability, IP rights, confidentiality, and governing law.\n\nContract:\n{{contract_b}}\n\nProvide output as JSON with clause name as key and clause text as value.",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "temperature": 0.2,
        "max_tokens": 4000
      }
    },
    {
      "id": "compare",
      "type": "action",
      "position": { "x": 500, "y": 200 },
      "data": {
        "name": "Compare Clauses",
        "prompt": "Compare the following two contract extractions and identify all differences.\n\nContract A (Base):\n{{extract_a.ai_output}}\n\nContract B (Comparison):\n{{extract_b.ai_output}}\n\nFor each difference found:\n1. Identify the clause\n2. Show the text from each version\n3. Describe the nature of the change\n4. Assess whether the change favors Party A, Party B, or is neutral\n\nFormat as a detailed comparison report.",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "temperature": 0.3,
        "max_tokens": 4000
      }
    },
    {
      "id": "assess_risk",
      "type": "action",
      "position": { "x": 700, "y": 200 },
      "data": {
        "name": "Risk Assessment",
        "prompt": "Based on the following contract comparison, provide a risk assessment.\n\nComparison:\n{{compare.ai_output}}\n\nFor each material change:\n1. Rate the risk as HIGH, MEDIUM, or LOW\n2. Explain the potential impact\n3. Suggest negotiation points or mitigations\n\nConclude with an overall assessment and recommended next steps.",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "temperature": 0.3,
        "max_tokens": 2000
      }
    }
  ],
  "edges": [
    { "source": "start", "target": "extract_a" },
    { "source": "start", "target": "extract_b" },
    { "source": "extract_a", "target": "compare" },
    { "source": "extract_b", "target": "compare" },
    { "source": "compare", "target": "assess_risk" }
  ]
}
```

---

## `workflows/contract-comparison/README.md`

```markdown
# Contract Comparison Workflow

Compares two versions of a contract to identify differences and assess risks.

## Use Cases

- Comparing your template vs. counterparty markup
- Reviewing changes between contract versions
- Identifying deviations from standard terms

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| `contract_a` | Document/Text | Base version (e.g., your template) |
| `contract_b` | Document/Text | Comparison version (e.g., markup) |

## Output

Markdown report containing:
- Side-by-side clause comparison
- Nature of each change
- Risk assessment (HIGH/MEDIUM/LOW)
- Negotiation recommendations

## How It Works

1. **Extract A**: Pulls key clauses from Contract A
2. **Extract B**: Pulls key clauses from Contract B (parallel)
3. **Compare**: Identifies differences between extractions
4. **Risk Assessment**: Evaluates impact of changes

## Import Instructions

### QueryLex
1. Navigate to Create → Workflows
2. Click "Import"
3. Upload `workflow.json`
4. Click "Save"

## Example

**Input**: Your NDA template + counterparty's marked-up version

**Output**:
```markdown
## Contract Comparison Report

### Confidentiality Period
- **Contract A**: 3 years from disclosure
- **Contract B**: 5 years from disclosure
- **Change**: Extended by 2 years
- **Risk**: MEDIUM - Longer obligation period
- **Recommendation**: Negotiate to 3 years or add carve-outs

### Governing Law
- **Contract A**: Delaware
- **Contract B**: New York
- **Change**: Different jurisdiction
- **Risk**: LOW - Both are common choices
- **Recommendation**: Acceptable if operations are in NY
```
```

---

# MCP-CONFIGS FOLDER

---

## `mcp-configs/README.md`

```markdown
# MCP Configurations

Model Context Protocol configurations for connecting AI assistants to legal tools and data sources.

## What is MCP?

MCP (Model Context Protocol) allows AI assistants like Claude to connect to external tools and databases. For legal work, this enables:

- Querying legal databases (EUR-Lex, CourtListener)
- Accessing document management systems
- Connecting to legal research platforms

## Available Configurations

### Claude Desktop

Ready-to-use configurations for Claude Desktop:

| Config | Tools | Use Case |
|--------|-------|----------|
| [legal-research.json](./claude-desktop/legal-research.json) | EUR-Lex, CourtListener | Legal research |
| [document-management.json](./claude-desktop/document-management.json) | Google Drive, filesystem | File access |
| [full-legal-stack.json](./claude-desktop/full-legal-stack.json) | All tools combined | Complete setup |

### Server Guides

Setup guides for MCP servers:
- [CourtListener MCP](./server-guides/courtlistener-mcp.md)
- [EUR-Lex MCP](./server-guides/eurlex-mcp.md)
- [Google Drive for Legal](./server-guides/google-drive-legal.md)

## Installation

### macOS

1. Open Claude Desktop settings
2. Navigate to Developer → MCP Servers
3. Add configuration:

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    // Paste configuration here
  }
}
```

### Windows

Configuration location:
```
%APPDATA%\Claude\claude_desktop_config.json
```

## Creating Custom Servers

See [custom-servers/](./custom-servers/) for examples of building your own MCP servers for legal applications.
```

---

## `mcp-configs/claude-desktop/legal-research.json`

```json
{
  "mcpServers": {
    "courtlistener": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-courtlistener"],
      "env": {
        "COURTLISTENER_API_KEY": "${COURTLISTENER_API_KEY}"
      },
      "description": "US case law search via CourtListener"
    },
    "eurlex": {
      "command": "python",
      "args": ["-m", "eurlex_mcp_server"],
      "env": {},
      "description": "EU legislation and case law via EUR-Lex"
    }
  }
}
```

---

## `mcp-configs/claude-desktop/document-management.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "/Users/[USERNAME]/Documents/Legal,/Users/[USERNAME]/Documents/Cases"
      },
      "description": "Access to local legal document folders"
    },
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-gdrive"],
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "~/.config/gcloud/application_default_credentials.json"
      },
      "description": "Access Google Drive documents"
    }
  }
}
```

---

## `mcp-configs/claude-desktop/full-legal-stack.json`

```json
{
  "mcpServers": {
    "courtlistener": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-courtlistener"],
      "env": {
        "COURTLISTENER_API_KEY": "${COURTLISTENER_API_KEY}"
      }
    },
    "eurlex": {
      "command": "python",
      "args": ["-m", "eurlex_mcp_server"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "/Users/[USERNAME]/Documents/Legal"
      }
    },
    "google-drive": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-gdrive"],
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "~/.config/gcloud/application_default_credentials.json"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-memory"],
      "env": {},
      "description": "Persistent memory across conversations"
    }
  }
}
```

---

## `mcp-configs/server-guides/courtlistener-mcp.md`

```markdown
# CourtListener MCP Setup

Connect Claude to CourtListener for US case law research.

## What is CourtListener?

[CourtListener](https://www.courtlistener.com/) is a free, open database of US court opinions, maintained by Free Law Project.

## Prerequisites

1. CourtListener API key (free): https://www.courtlistener.com/api/
2. Node.js 18+
3. Claude Desktop

## Installation

### 1. Get API Key

1. Create account at courtlistener.com
2. Go to Profile → API Keys
3. Create new key

### 2. Configure Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "courtlistener": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-courtlistener"],
      "env": {
        "COURTLISTENER_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

## Usage

Once configured, you can ask Claude:

- "Find Supreme Court cases about qualified immunity from 2020-2024"
- "Search for cases citing Miranda v. Arizona"
- "Find Ninth Circuit opinions on software patents"

## Available Tools

| Tool | Description |
|------|-------------|
| `search_opinions` | Search case opinions by keyword, court, date |
| `get_opinion` | Retrieve full opinion by ID |
| `search_dockets` | Search court dockets |
| `get_citations` | Find cases citing a given case |

## Limitations

- API rate limits apply (check CourtListener docs)
- Some opinions may not have full text
- Primarily US federal and state courts
```

---

# TOOLS FOLDER

---

## `tools/README.md`

```markdown
# Legal AI Tools

Curated evaluations of tools for legal NLP and document processing.

## Categories

### NLP Libraries
Tools for natural language processing on legal text:
- [LexNLP](./nlp/lexnlp.yaml) - Legal entity extraction
- [Blackstone](./nlp/blackstone.yaml) - UK legal NLP
- [EyeCite](./nlp/eyecite.yaml) - Citation extraction

### Document Processing
Tools for handling legal documents:
- [Docassemble](./document-processing/docassemble.yaml) - Document automation
- [PDFPlumber](./document-processing/pdfplumber.yaml) - PDF extraction
- [Unstructured](./document-processing/unstructured.yaml) - Universal parser

## Evaluation Criteria

Each tool is evaluated on:
1. **Functionality** - What it does well
2. **Ease of Use** - Setup and learning curve
3. **Maintenance** - Active development, community
4. **License** - Commercial use implications
5. **Performance** - Speed and accuracy

## How to Read Evaluations

Each YAML file contains:
- Basic info (name, repo, license)
- Our honest evaluation with strengths/weaknesses
- Best use cases
- Alternatives to consider
```

---

## `tools/nlp/lexnlp.yaml`

```yaml
name: "LexNLP"
slug: lexnlp
type: tool-link

description: >
  Comprehensive Python library for extracting structured information from
  legal and regulatory text. Extracts dates, money, citations, named
  entities, and more.

repository: https://github.com/LexPredict/lexpredict-lexnlp
documentation: https://lexpredict-lexnlp.readthedocs.io/
pypi: lexnlp

language: python
install_command: "pip install lexnlp"
license: AGPL-3.0
stars: 760
last_commit: "2024-08"

our_evaluation:
  overall_rating: 4

  strengths:
    - "Comprehensive extraction: dates, money, citations, definitions"
    - "Legal-domain specific (not generic NLP)"
    - "Good documentation with examples"
    - "Active maintenance by LexPredict"
    - "Pre-trained models included"

  weaknesses:
    - "AGPL license restricts commercial use without open-sourcing"
    - "Heavy dependencies (spaCy, scikit-learn, etc.)"
    - "Primarily English-focused"
    - "Some extractors have mediocre accuracy on complex text"

  best_for:
    - "Contract data extraction pipelines"
    - "Legal document preprocessing"
    - "Citation parsing and normalization"
    - "Building legal search indexes"

  not_recommended_for:
    - "Closed-source commercial products (AGPL)"
    - "Non-English documents"
    - "Real-time/low-latency applications"

  alternatives:
    - blackstone
    - spacy-legal
    - eyecite

category: nlp
subcategory: extraction
tags:
  - ner
  - extraction
  - contracts
  - citations
  - dates
  - money

last_evaluated: 2026-01-27
```

---

## `tools/nlp/eyecite.yaml`

```yaml
name: "EyeCite"
slug: eyecite
type: tool-link

description: >
  Fast, accurate citation extraction from legal text. Developed by Free Law
  Project for CourtListener. Handles reporter citations, statutory citations,
  and Id. references.

repository: https://github.com/freelawproject/eyecite
documentation: https://github.com/freelawproject/eyecite#readme
pypi: eyecite

language: python
install_command: "pip install eyecite"
license: BSD-2-Clause
stars: 120
last_commit: "2024-10"

our_evaluation:
  overall_rating: 5

  strengths:
    - "Very fast - processes thousands of citations per second"
    - "High accuracy on US legal citations"
    - "Handles complex citation formats (Id., supra, etc.)"
    - "Permissive BSD license"
    - "Lightweight with minimal dependencies"
    - "Used in production by CourtListener"

  weaknesses:
    - "US-centric (limited EU/UK citation support)"
    - "No entity extraction beyond citations"
    - "Requires understanding of legal citation formats"

  best_for:
    - "Building legal citation networks"
    - "Citation validation and normalization"
    - "Legal research tools"
    - "Document cross-referencing"

  not_recommended_for:
    - "Non-US legal documents"
    - "General legal NER (use LexNLP instead)"

  alternatives:
    - lexnlp

category: nlp
subcategory: citations
tags:
  - citations
  - extraction
  - case-law
  - research

last_evaluated: 2026-01-27
```

---

## `tools/document-processing/unstructured.yaml`

```yaml
name: "Unstructured"
slug: unstructured
type: tool-link

description: >
  Universal document parser that handles PDFs, Word docs, images, HTML, and
  more. Extracts text while preserving structure. Good for RAG pipelines.

repository: https://github.com/Unstructured-IO/unstructured
documentation: https://unstructured-io.github.io/unstructured/
pypi: unstructured

language: python
install_command: "pip install unstructured[all-docs]"
license: Apache-2.0
stars: 6500
last_commit: "2024-11"

our_evaluation:
  overall_rating: 4

  strengths:
    - "Handles many document formats (PDF, DOCX, HTML, images)"
    - "OCR support for scanned documents"
    - "Preserves document structure (headers, tables, lists)"
    - "Apache 2.0 license (commercial-friendly)"
    - "Active development and good community"
    - "Integrates well with LangChain, LlamaIndex"

  weaknesses:
    - "Large install with many dependencies"
    - "OCR quality varies by document"
    - "Can be slow on large documents"
    - "Table extraction not always perfect"

  best_for:
    - "Building RAG pipelines"
    - "Legal document ingestion"
    - "Processing mixed document types"
    - "OCR of scanned legal documents"

  not_recommended_for:
    - "Simple text files (overkill)"
    - "High-volume real-time processing"

  alternatives:
    - pdfplumber
    - marker-pdf

category: document-processing
subcategory: parsing
tags:
  - pdf
  - docx
  - ocr
  - rag
  - extraction

last_evaluated: 2026-01-27
```

---

# DATASETS FOLDER

---

## `datasets/README.md`

```markdown
# Legal Datasets

Curated links to datasets for training and evaluating legal AI models.

## Categories

### Contract Datasets
- [CUAD](./contracts/cuad.yaml) - Contract clause extraction
- [MAUD](./contracts/maud.yaml) - M&A contract understanding
- [Contract-NLI](./contracts/contract-nli.yaml) - Contract entailment

### Case Law
- [CaseHOLD](./case-law/casehold.yaml) - Holding statement identification
- [CourtListener Bulk](./case-law/courtlistener-bulk.yaml) - US case law corpus

### Benchmarks
- [LegalBench](./benchmarks/legalbench.yaml) - Legal reasoning tasks
- [LexGLUE](./benchmarks/lexglue.yaml) - Legal NLU benchmark

## Usage Notes

1. **Check licenses** before commercial use
2. **Cite properly** in academic work
3. **Verify currency** - legal data changes
4. **Consider jurisdiction** - most datasets are US/UK focused
```

---

## `datasets/contracts/cuad.yaml`

```yaml
name: "CUAD"
slug: cuad
type: dataset-link
full_name: "Contract Understanding Atticus Dataset"

description: >
  Expert-annotated dataset of 510 commercial contracts with 41 types of
  legal clause annotations. Created by The Atticus Project with legal
  experts. The gold standard for contract analysis.

source:
  organization: "The Atticus Project"
  website: https://www.atticusprojectai.org/cuad
  paper: https://arxiv.org/abs/2103.06268
  year: 2021

download:
  huggingface: "theatticusproject/cuad-qa"
  direct: https://zenodo.org/record/4599830
  github: https://github.com/TheAtticusProject/cuad

size:
  documents: 510
  annotations: 13000
  file_size: "~500MB"

format:
  type: "SQuAD-style JSON"
  structure: "Question-answer pairs for clause extraction"

clause_types:
  - Document Name
  - Parties
  - Agreement Date
  - Effective Date
  - Expiration Date
  - Renewal Term
  - Notice Period
  - Governing Law
  - Most Favored Nation
  - Non-Compete
  - Exclusivity
  - No-Solicit
  - Termination for Convenience
  - "... and 28 more"

license: CC-BY-4.0

citation: |
  @inproceedings{hendrycks2021cuad,
    title={CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review},
    author={Hendrycks, Dan and Burns, Collin and Chen, Anya and Ball, Spencer},
    booktitle={NeurIPS 2021},
    year={2021}
  }

use_cases:
  - "Training contract analysis models"
  - "Clause extraction fine-tuning"
  - "Benchmarking legal NLP systems"
  - "Building contract review tools"

our_notes: >
  The best publicly available contract dataset. The 41 clause types cover
  most provisions you'd want to extract from commercial agreements.
  Consider using with MAUD for M&A-specific clauses.

related_datasets:
  - maud
  - contract-nli
  - atticus

last_updated: 2026-01-27
```

---

## `datasets/benchmarks/legalbench.yaml`

```yaml
name: "LegalBench"
slug: legalbench
type: dataset-link
full_name: "LegalBench: A Collaboratively Built Benchmark for Legal Reasoning"

description: >
  Comprehensive benchmark with 162 tasks covering legal reasoning abilities.
  Created collaboratively by 40+ legal professionals and NLP researchers.
  Tests issue spotting, rule recall, rule application, and more.

source:
  organization: "Stanford, MIT, et al."
  website: https://hazyresearch.stanford.edu/legalbench/
  paper: https://arxiv.org/abs/2308.11462
  year: 2023

download:
  huggingface: "nguha/legalbench"
  github: https://github.com/HazyResearch/legalbench

size:
  tasks: 162
  samples: "~20,000 total"
  file_size: "~100MB"

format:
  type: "JSON"
  structure: "Task-specific prompts with gold answers"

task_categories:
  - Issue Spotting (identify legal issues)
  - Rule Recall (recall relevant legal rules)
  - Rule Application (apply rules to facts)
  - Rule Conclusion (draw legal conclusions)
  - Interpretation (statutory interpretation)
  - Rhetorical Understanding (legal writing analysis)

license: CC-BY-4.0

citation: |
  @article{guha2023legalbench,
    title={LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models},
    author={Guha, Neel and others},
    journal={NeurIPS 2023},
    year={2023}
  }

use_cases:
  - "Evaluating LLM legal reasoning"
  - "Comparing model performance on legal tasks"
  - "Identifying model weaknesses"
  - "Academic research"

our_notes: >
  The most comprehensive legal reasoning benchmark available. Essential for
  anyone building or evaluating legal AI. Use this alongside domain-specific
  datasets like CUAD for complete evaluation.

related_datasets:
  - lexglue
  - legal-lama
  - casehold

last_updated: 2026-01-27
```

---

# CODE-SNIPPETS FOLDER

---

## `code-snippets/README.md`

```markdown
# Code Snippets

Utility functions for legal text processing.

## Python

| Snippet | Purpose |
|---------|---------|
| [citation-parser.py](./python/citation-parser.py) | Parse legal citations |
| [contract-chunker.py](./python/contract-chunker.py) | Smart document chunking |
| [legal-ner-utils.py](./python/legal-ner-utils.py) | Named entity helpers |

## TypeScript

| Snippet | Purpose |
|---------|---------|
| [citation-parser.ts](./typescript/citation-parser.ts) | Citation parsing |
| [legal-date-parser.ts](./typescript/legal-date-parser.ts) | Date extraction |

## Usage

Copy the snippet into your project and modify as needed. All snippets are CC0 licensed.
```

---

## `code-snippets/python/citation-parser.py`

```python
"""
Legal Citation Parser
Extracts and normalizes legal citations from text.

License: CC0 (Public Domain)
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Citation:
    """Represents a parsed legal citation."""
    full_text: str
    volume: Optional[str] = None
    reporter: Optional[str] = None
    page: Optional[str] = None
    court: Optional[str] = None
    year: Optional[str] = None
    pin_cite: Optional[str] = None
    citation_type: str = "unknown"  # case, statute, regulation


# Common reporter abbreviations
REPORTERS = {
    "U.S.": "United States Reports",
    "S.Ct.": "Supreme Court Reporter",
    "L.Ed.": "Lawyers' Edition",
    "F.2d": "Federal Reporter, Second Series",
    "F.3d": "Federal Reporter, Third Series",
    "F.4th": "Federal Reporter, Fourth Series",
    "F.Supp.": "Federal Supplement",
    "F.Supp.2d": "Federal Supplement, Second Series",
    "F.Supp.3d": "Federal Supplement, Third Series",
}

# Case citation pattern: Volume Reporter Page (Court Year)
CASE_PATTERN = re.compile(
    r'(\d+)\s+'                           # Volume
    r'([A-Z][A-Za-z\.\s]+?)\s+'           # Reporter
    r'(\d+)'                              # Page
    r'(?:,\s*(\d+))?'                     # Pin cite (optional)
    r'\s*\(([^)]+)\s+(\d{4})\)',          # Court and Year
    re.VERBOSE
)

# Statute pattern: Title U.S.C. § Section
STATUTE_PATTERN = re.compile(
    r'(\d+)\s+U\.S\.C\.\s*§\s*(\d+[a-z]?(?:\([a-z0-9]+\))?)',
    re.IGNORECASE
)


def extract_citations(text: str) -> List[Citation]:
    """
    Extract all legal citations from text.

    Args:
        text: Legal text to parse

    Returns:
        List of Citation objects
    """
    citations = []

    # Find case citations
    for match in CASE_PATTERN.finditer(text):
        citations.append(Citation(
            full_text=match.group(0),
            volume=match.group(1),
            reporter=match.group(2).strip(),
            page=match.group(3),
            pin_cite=match.group(4),
            court=match.group(5),
            year=match.group(6),
            citation_type="case"
        ))

    # Find statute citations
    for match in STATUTE_PATTERN.finditer(text):
        citations.append(Citation(
            full_text=match.group(0),
            volume=match.group(1),  # Title
            reporter="U.S.C.",
            page=match.group(2),    # Section
            citation_type="statute"
        ))

    return citations


def normalize_citation(citation: Citation) -> str:
    """
    Convert citation to standard Bluebook format.

    Args:
        citation: Parsed Citation object

    Returns:
        Normalized citation string
    """
    if citation.citation_type == "case":
        result = f"{citation.volume} {citation.reporter} {citation.page}"
        if citation.pin_cite:
            result += f", {citation.pin_cite}"
        result += f" ({citation.court} {citation.year})"
        return result

    elif citation.citation_type == "statute":
        return f"{citation.volume} U.S.C. § {citation.page}"

    return citation.full_text


# Example usage
if __name__ == "__main__":
    sample_text = """
    In Brown v. Board of Education, 347 U.S. 483 (1954), the Supreme Court
    held that segregation was unconstitutional. This was later affirmed in
    Cooper v. Aaron, 358 U.S. 1, 17 (1958). See also 42 U.S.C. § 1983 for
    civil rights actions.
    """

    citations = extract_citations(sample_text)
    for cit in citations:
        print(f"Found: {cit.full_text}")
        print(f"  Type: {cit.citation_type}")
        print(f"  Normalized: {normalize_citation(cit)}")
        print()
```

---

## `code-snippets/python/contract-chunker.py`

```python
"""
Smart Contract Chunker
Splits legal documents into semantically meaningful chunks for RAG.

License: CC0 (Public Domain)
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chunk:
    """Represents a document chunk."""
    content: str
    chunk_type: str  # section, clause, paragraph, definition
    section_number: Optional[str] = None
    section_title: Optional[str] = None
    parent_section: Optional[str] = None
    start_char: int = 0
    end_char: int = 0


def chunk_contract(
    text: str,
    max_chunk_size: int = 1000,
    overlap: int = 100,
    preserve_sections: bool = True
) -> List[Chunk]:
    """
    Split a contract into chunks suitable for embedding.

    Args:
        text: Full contract text
        max_chunk_size: Maximum characters per chunk
        overlap: Character overlap between chunks
        preserve_sections: Try to keep sections intact

    Returns:
        List of Chunk objects
    """
    chunks = []

    # First, try to split by section headers
    section_pattern = re.compile(
        r'^(\d+(?:\.\d+)*)\s*[.\-–]\s*(.+?)(?=\n)',
        re.MULTILINE
    )

    sections = []
    last_end = 0

    for match in section_pattern.finditer(text):
        # Add text before this section
        if match.start() > last_end:
            preamble = text[last_end:match.start()].strip()
            if preamble:
                sections.append({
                    'number': None,
                    'title': 'Preamble',
                    'start': last_end,
                    'content': preamble
                })

        # Find section end (next section or end of doc)
        next_match = section_pattern.search(text, match.end())
        section_end = next_match.start() if next_match else len(text)

        sections.append({
            'number': match.group(1),
            'title': match.group(2).strip(),
            'start': match.start(),
            'content': text[match.start():section_end].strip()
        })
        last_end = section_end

    # If no sections found, treat whole document as one section
    if not sections:
        sections = [{
            'number': None,
            'title': 'Document',
            'start': 0,
            'content': text
        }]

    # Now chunk each section
    for section in sections:
        section_content = section['content']

        if len(section_content) <= max_chunk_size:
            # Section fits in one chunk
            chunks.append(Chunk(
                content=section_content,
                chunk_type='section',
                section_number=section['number'],
                section_title=section['title'],
                start_char=section['start'],
                end_char=section['start'] + len(section_content)
            ))
        else:
            # Need to split section into smaller chunks
            # Try to split on paragraph boundaries
            paragraphs = re.split(r'\n\s*\n', section_content)

            current_chunk = ""
            chunk_start = section['start']

            for para in paragraphs:
                if len(current_chunk) + len(para) + 2 <= max_chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(Chunk(
                            content=current_chunk.strip(),
                            chunk_type='paragraph',
                            section_number=section['number'],
                            section_title=section['title'],
                            start_char=chunk_start,
                            end_char=chunk_start + len(current_chunk)
                        ))
                        chunk_start += len(current_chunk) - overlap

                    # Start new chunk with overlap
                    if overlap > 0 and current_chunk:
                        current_chunk = current_chunk[-overlap:] + para + "\n\n"
                    else:
                        current_chunk = para + "\n\n"

            # Don't forget the last chunk
            if current_chunk.strip():
                chunks.append(Chunk(
                    content=current_chunk.strip(),
                    chunk_type='paragraph',
                    section_number=section['number'],
                    section_title=section['title'],
                    start_char=chunk_start,
                    end_char=chunk_start + len(current_chunk)
                ))

    return chunks


def add_context_prefix(chunk: Chunk) -> str:
    """
    Add contextual prefix to chunk for better retrieval.

    Args:
        chunk: Chunk object

    Returns:
        Chunk content with context prefix
    """
    prefix_parts = []

    if chunk.section_number:
        prefix_parts.append(f"Section {chunk.section_number}")

    if chunk.section_title:
        prefix_parts.append(chunk.section_title)

    if prefix_parts:
        prefix = f"[{' - '.join(prefix_parts)}]\n\n"
        return prefix + chunk.content

    return chunk.content


# Example usage
if __name__ == "__main__":
    sample_contract = """
    MASTER SERVICE AGREEMENT

    This Agreement is entered into as of January 1, 2026.

    1. DEFINITIONS

    1.1 "Services" means the consulting services described in Exhibit A.

    1.2 "Confidential Information" means any non-public information.

    2. SERVICES

    2.1 Scope. Provider shall perform the Services in accordance with
    the specifications set forth in Exhibit A.

    2.2 Standards. All Services shall be performed in a professional
    and workmanlike manner consistent with industry standards.

    3. PAYMENT

    3.1 Fees. Client shall pay Provider the fees set forth in Exhibit B.

    3.2 Expenses. Client shall reimburse Provider for pre-approved expenses.
    """

    chunks = chunk_contract(sample_contract, max_chunk_size=500)

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i + 1} ({chunk.chunk_type}):")
        print(f"  Section: {chunk.section_number} - {chunk.section_title}")
        print(f"  Length: {len(chunk.content)} chars")
        print(f"  Preview: {chunk.content[:100]}...")
        print()
```

---

# DOCS FOLDER

---

## `docs/getting-started.md`

```markdown
# Getting Started

Quick guide to using the Ultimate Legal AI Library.

## 1. Browse Resources

Start by exploring the categories:
- [System Prompts](../prompts/system-prompts/) - Ready-to-use AI personas
- [Workflows](../workflows/) - Automation templates
- [Tools](../tools/) - NLP library evaluations

## 2. Use a System Prompt

```python
# Download
curl -O https://raw.githubusercontent.com/AndriusPetrenas/UltimateLegalAILibrary/main/prompts/system-prompts/contract-analyst/prompt.md

# Use with OpenAI
import openai

with open('prompt.md') as f:
    system_prompt = f.read()

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Analyze this contract..."}
    ]
)
```

## 3. Import a Workflow

1. Download `workflow.json` from any workflow folder
2. Import into QueryLex or n8n
3. Configure inputs and run

## 4. Set Up MCP

See [MCP Configurations](../mcp-configs/) for Claude Desktop setup.

## 5. Contribute

Found something useful? Share it back!
- Fork the repo
- Add your resource
- Submit a PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
```

---

## `docs/faq.md`

```markdown
# Frequently Asked Questions

## General

### What is this library?
A curated collection of prompts, workflows, and tools for legal AI applications. All hosted content is CC0 (public domain).

### Who maintains this?
The QueryLex team and community contributors.

### Can I use this commercially?
Yes! Hosted content is CC0. For linked external tools, check their individual licenses.

## Prompts

### Which LLM should I use?
Most prompts work with any modern LLM (GPT-4, Claude 3.5+, Gemini Pro). Check the `tested_with` field in metadata.

### Why aren't prompts working well?
- Ensure you're using a capable model
- Provide clear, complete input documents
- Try adjusting temperature (lower = more precise)

## Workflows

### Which workflow engine do I need?
Most workflows are designed for QueryLex. Some also work with n8n.

### Can I modify workflows?
Absolutely! They're CC0 licensed. Adapt them to your needs.

## Contributing

### How do I contribute?
1. Fork the repo
2. Add your resource following our templates
3. Submit a PR
4. See [CONTRIBUTING.md](../CONTRIBUTING.md)

### What if my prompt uses proprietary content?
Don't submit it. Only contribute content you have rights to and can release as CC0.
```

---

# SAMPLE-DATA FOLDER

---

## `sample-data/README.md`

```markdown
# Sample Data

Small, immediately usable datasets for testing and development.

## Contract Clauses

Sample clause collections in JSONL format:
- [indemnification-clauses.jsonl](./contract-clauses/indemnification-clauses.jsonl)
- [termination-clauses.jsonl](./contract-clauses/termination-clauses.jsonl)
- [confidentiality-clauses.jsonl](./contract-clauses/confidentiality-clauses.jsonl)

## Legal Citations

Citation examples for testing parsers:
- [us-case-citations.csv](./legal-citations/us-case-citations.csv)
- [us-statute-citations.csv](./legal-citations/us-statute-citations.csv)

## Test Documents

Sample documents for pipeline testing:
- [sample-nda.md](./test-documents/sample-nda.md)

## Usage

All sample data is synthetic or from public domain sources. Safe for testing and development.
```

---

## `sample-data/contract-clauses/indemnification-clauses.jsonl`

```jsonl
{"id": "ind_001", "text": "Contractor shall indemnify, defend, and hold harmless Client and its officers, directors, employees, and agents from and against any and all claims, damages, losses, costs, and expenses (including reasonable attorneys' fees) arising out of or relating to Contractor's breach of this Agreement or negligent acts or omissions.", "clause_type": "indemnification", "party_indemnifying": "contractor", "scope": "broad", "carve_outs": []}
{"id": "ind_002", "text": "Each party shall indemnify the other party against any third-party claims arising from the indemnifying party's gross negligence or willful misconduct in connection with this Agreement.", "clause_type": "indemnification", "party_indemnifying": "mutual", "scope": "limited", "carve_outs": ["gross_negligence", "willful_misconduct"]}
{"id": "ind_003", "text": "Vendor agrees to indemnify and hold Customer harmless from any claims of intellectual property infringement arising from Customer's use of the Products in accordance with this Agreement.", "clause_type": "indemnification", "party_indemnifying": "vendor", "scope": "ip_only", "carve_outs": ["ip_infringement"]}
{"id": "ind_004", "text": "Provider shall defend, indemnify, and hold harmless Customer from any data breach claims to the extent caused by Provider's failure to maintain industry-standard security measures.", "clause_type": "indemnification", "party_indemnifying": "provider", "scope": "data_breach", "carve_outs": ["security_failure"]}
{"id": "ind_005", "text": "The Supplier's total liability under this indemnification provision shall not exceed the fees paid by Buyer in the twelve (12) months preceding the claim.", "clause_type": "indemnification", "party_indemnifying": "supplier", "scope": "capped", "carve_outs": [], "cap": "12_months_fees"}
```

---

## `sample-data/test-documents/sample-nda.md`

```markdown
# MUTUAL NON-DISCLOSURE AGREEMENT

**Effective Date:** January 1, 2026

This Mutual Non-Disclosure Agreement ("Agreement") is entered into by and between:

**Party A:** Acme Corporation, a Delaware corporation ("Acme")
**Party B:** Beta Industries LLC, a California limited liability company ("Beta")

(each a "Party" and collectively the "Parties")

## 1. PURPOSE

The Parties wish to explore a potential business relationship concerning [DESCRIBE PURPOSE] (the "Purpose"). In connection with the Purpose, each Party may disclose certain confidential information to the other Party.

## 2. DEFINITIONS

2.1 **"Confidential Information"** means any non-public information disclosed by one Party (the "Disclosing Party") to the other Party (the "Receiving Party"), whether orally, in writing, or by inspection, that is designated as confidential or that reasonably should be understood to be confidential given the nature of the information and circumstances of disclosure.

2.2 **"Representatives"** means a Party's employees, officers, directors, advisors, and agents who have a need to know the Confidential Information for the Purpose.

## 3. CONFIDENTIALITY OBLIGATIONS

3.1 The Receiving Party shall:
   (a) Hold the Confidential Information in strict confidence;
   (b) Not disclose the Confidential Information to any third party except its Representatives;
   (c) Use the Confidential Information solely for the Purpose;
   (d) Protect the Confidential Information using the same degree of care it uses for its own confidential information, but no less than reasonable care.

3.2 The Receiving Party shall ensure that its Representatives are bound by confidentiality obligations at least as protective as those in this Agreement.

## 4. EXCLUSIONS

Confidential Information does not include information that:
   (a) Is or becomes publicly available without breach of this Agreement;
   (b) Was rightfully in the Receiving Party's possession before disclosure;
   (c) Is rightfully obtained from a third party without restriction;
   (d) Is independently developed without use of Confidential Information.

## 5. TERM AND TERMINATION

5.1 This Agreement shall remain in effect for three (3) years from the Effective Date.

5.2 The confidentiality obligations shall survive termination for a period of five (5) years.

5.3 Upon termination, the Receiving Party shall return or destroy all Confidential Information upon written request.

## 6. NO LICENSE

Nothing in this Agreement grants any license or right to use any intellectual property of the Disclosing Party, except as necessary for the Purpose.

## 7. REMEDIES

The Parties acknowledge that breach of this Agreement may cause irreparable harm for which monetary damages would be inadequate. The Disclosing Party shall be entitled to seek equitable relief, including injunction and specific performance, in addition to any other remedies available at law.

## 8. GOVERNING LAW

This Agreement shall be governed by the laws of the State of Delaware, without regard to conflict of law principles.

## 9. MISCELLANEOUS

9.1 **Entire Agreement.** This Agreement constitutes the entire agreement between the Parties concerning the subject matter hereof.

9.2 **Amendment.** This Agreement may only be amended in writing signed by both Parties.

9.3 **Waiver.** No waiver of any provision shall be effective unless in writing.

9.4 **Severability.** If any provision is held unenforceable, the remaining provisions shall continue in effect.

9.5 **Counterparts.** This Agreement may be executed in counterparts.

---

**IN WITNESS WHEREOF**, the Parties have executed this Agreement as of the Effective Date.

**ACME CORPORATION**

By: _________________________
Name:
Title:
Date:

**BETA INDUSTRIES LLC**

By: _________________________
Name:
Title:
Date:
```

---

# END OF REPOSITORY CONTENT

This file contains all the essential content for the UltimateLegalAILibrary GitHub repository. To create the actual repository:

1. Create a new GitHub repository at `github.com/AndriusPetrenas/UltimateLegalAILibrary`
2. Create the folder structure as outlined
3. Copy each file's content from this document to its corresponding path
4. Commit and push

**Placeholders to fill:**
- Additional system prompts (10 total planned)
- Additional workflows (12 total planned)
- Additional tool evaluations (20+ planned)
- Additional dataset links (15+ planned)
- More code snippets as needed
- Workflow diagram images (PNG files)
