# Legal Workflows

Automation workflows for common legal tasks. Import into QueryLex or n8n.

## Available Workflows

| Workflow | Description | Engine | Dataset Required |
|----------|-------------|--------|:---:|
| [French Contract Generator](./french-contract-generator/) | Generate French-law contracts (NDA, CDI, Services) | QueryLex | No |
| [Legal Research Pipeline](./legal-research/) | Deep research with query decomposition and parallel retrieval | QueryLex | Yes |

## Workflow Engine

The [Workflow Engine](./workflow-engine/) executes all workflows. It supports 6 node types: `start`, `action` (LLM), `retrieval` (vector search), `router` (conditional), `code` (sandboxed Python), and `legal_research` (multi-step research).

[Download workflow_engine.py](./workflow-engine/workflow_engine.py)

## How to Use

### QueryLex

1. Go to Create > Workflows
2. Click "Import Workflow"
3. Upload the `workflow.json` file
4. Configure any required API keys or datasets
5. Run the workflow

### n8n

1. Import the JSON into n8n
2. Configure credentials
3. Activate the workflow

### Standalone (Python)

```python
from workflow_engine import WorkflowRunner
import json

with open("workflows/french-contract-generator/workflow.json") as f:
    workflow = json.load(f)

runner = WorkflowRunner(workflow)
result = runner.run({"input": "NDA entre deux societes tech a Paris"})
print(result["final_output"])
```

## Workflow Structure

Each workflow includes:
- `metadata.yaml` - Description and requirements
- `workflow.json` - The importable workflow definition
- `README.md` - Setup and usage instructions
