# Legal Research Pipeline

Deep legal research workflow that decomposes complex questions into 3 sub-questions, retrieves documents in parallel, and generates structured analysis with citations.

## How It Works

```
User Query
    |
    v
[Decompose into 3 Sub-Questions]
    |
    +----+----+
    |    |    |
    v    v    v
[Retrieve] [Retrieve] [Retrieve]    (parallel, 3 threads)
    |    |    |
    v    v    v
[Analyze]  [Analyze]  [Analyze]     (parallel, 3 threads)
    |    |    |
    +----+----+
    |
    v
[Generate Summary]
    |
    v
Structured Legal Analysis with Citations
```

**This is a specialized `legal_research` node type** that internally performs:

1. **Query Decomposition:** Breaks the query into 3 focused sub-questions
   - Sub-question 1: **Foundational Framework** (definitions, legal regime, principles)
   - Sub-question 2: **Conditions & Obligations** (requirements, eligibility, powers)
   - Sub-question 3: **Application & Variations** (concrete cases, special conditions, mechanisms)

2. **Parallel Retrieval:** Uses `ThreadPoolExecutor` with 3 workers to simultaneously search the vector database for each sub-question (top_k=8 documents each)

3. **Parallel Analysis:** Generates a detailed 800-1500 word analysis for each sub-question with inline citations

4. **Summary:** Combines all analyses into a concise final summary

## Citation Format

The workflow generates citations in French legal format:
- `(Code civil - Article - XXX)`
- `(Cour de cassation, date, numero)`
- `(CJUE - Affaire C-XXX/XX)`

## Output Structure

```markdown
# Legal Research: [Original Question]

## Sub-Question 1: Foundational Framework
[800-1500 word analysis with citations]

## Sub-Question 2: Conditions & Obligations
[800-1500 word analysis with citations]

## Sub-Question 3: Application & Variations
[800-1500 word analysis with citations]

## Summary
[Concise synthesis of all findings]
```

## Usage

### Import into QueryLex

1. Go to **Create > Workflows**
2. Click **Import Workflow**
3. Upload `workflow.json`
4. **Important:** Select a dataset containing your legal documents
5. Enter your research question
6. Run the workflow

### Download

```bash
curl -O https://raw.githubusercontent.com/AndriusPetrenas/UltimateLegalAILibrary/main/workflows/legal-research/workflow.json
```

## Example

**Input:** "Quelles sont les conditions de validite d'une clause de non-concurrence en droit du travail francais?"

**Decomposition:**
1. "Quel est le regime juridique de la clause de non-concurrence en droit du travail francais, et quelles sont les definitions et principes fondamentaux applicables?"
2. "Quelles sont les conditions de validite cumulatives qu'une clause de non-concurrence doit remplir pour etre opposable au salarie?"
3. "Comment s'articulent les sanctions en cas de non-respect de ces conditions, et dans quelles circonstances le juge peut-il reviser ou annuler une telle clause?"

## Workflow Engine

This workflow uses the `legal_research` node type from the [QueryLex Workflow Engine](../workflow-engine/). See the engine documentation for details on how nodes are executed.

## Requirements

- GPT-4o API access
- A dataset with indexed legal documents (uses vector search)
- QueryLex platform or compatible workflow engine

## License

CC0 1.0 Universal - Public domain.
