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
