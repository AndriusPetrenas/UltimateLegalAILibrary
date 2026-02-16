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

Copy the prompt content and use it as a system message:

```python
with open('system-prompts/contract-analyst/prompt.md', 'r') as f:
    system_prompt = f.read()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Analyze this NDA for risks..."}
    ]
)
```

### Using a Prompt Template

Open the template, fill in the bracketed placeholders with your specific content, and send as a user message.
