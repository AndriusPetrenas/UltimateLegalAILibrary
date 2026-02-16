# QueryLex Workflow Engine

The execution engine that powers all QueryLex workflows. Executes a DAG (Directed Acyclic Graph) of nodes defined in JSON.

## Prerequisites

The workflow engine depends on the [RAG Pipeline](../../code-snippets/python/rag-pipeline/) modules for LLM calls, embeddings, and vector search. Make sure the RAG pipeline is set up first (see its README for instructions).

Additional dependency for sandboxed code execution:

```bash
pip install RestrictedPython
```

## Files

| File | Purpose |
|------|---------|
| `workflow_engine.py` | Main engine — DAG executor with all node types |
| `extensions.py` | Standalone helpers for embedding service and vector client initialization |

## Supported Node Types

| Node Type | Purpose | Requires LLM | Requires Dataset |
|-----------|---------|:---:|:---:|
| `start` | Workflow entry point | No | No |
| `action` | LLM call with prompt template | Yes | No |
| `retrieval` | Vector database search | No | Yes |
| `router` | Conditional branching | No | No |
| `code` | Python execution (sandboxed) | No | No |
| `legal_research` | Multi-step research pipeline | Yes | Yes |

## How It Works

```python
from workflow_engine import WorkflowRunner

# Load a workflow definition
workflow_data = {
    "nodes": [...],
    "edges": [...]
}

runner = WorkflowRunner(workflow_data, user=current_user)
result = runner.run({"input": "Your question here"})

print(result["final_output"])
print(result["status"])  # "completed"
```

## Node Data Format

```json
{
  "id": "node_2",
  "type": "action",
  "x": 400,
  "y": 250,
  "data": {
    "name": "Draft Contract",
    "prompt": "Based on: {{input}}\n\nGenerate a contract...",
    "model": "gpt-4o",
    "temperature": 0.3,
    "max_tokens": 4000,
    "json_mode": false
  }
}
```

## Template Variables

The engine supports `{{variable}}` syntax with dot notation for accessing outputs from previous nodes:

- `{{input}}` - The original user input
- `{{node_2.ai_output}}` - Output from node_2's LLM call
- `{{node_3.retrieved_context}}` - Retrieved documents from node_3
- `{{node_4.status}}` - Any field from a code node's return dict

## Context Flow

Each node receives and contributes to a shared `context` dictionary:

```
Start: context = {input: "...", chat_history: [...]}
  |
Node_2: context += {node_2: {ai_output: "..."}, ai_output: "..."}
  |
Node_3: context += {node_3: {retrieved_context: "..."}, retrieved_context: "..."}
```

## Security

- **Code nodes** use RestrictedPython (sandboxed bytecode execution)
- Only `datetime`, `json`, `math`, `re` modules are available
- No access to private attributes (starting with `_`)
- Router conditions evaluated in a restricted sandbox

## Execution Flow

1. Find the `start` node
2. BFS traversal through the DAG via edges
3. Execute each node based on its type
4. Router nodes can halt branches (return `__halt__: True`)
5. Final output comes from the last successfully executed node

## License

CC0 1.0 Universal - Public domain.
