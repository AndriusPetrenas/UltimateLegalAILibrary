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
