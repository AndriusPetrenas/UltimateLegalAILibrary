# Sanctions Advisor (Classic — Single Agent)

Single-agent sanctions screening with real-time web search and tool use. Best for straightforward screening questions, quick designation checks, or simple compliance queries.

For complex fact patterns with ownership chains or multi-jurisdictional exposure, use the [Sanctions Compliance Advisor (V3)](../sanctions-compliance-advisor/) instead.

**No dataset required.** Uses real-time web search and a built-in sanctions provisions database.

## How It Works

```
User describes scenario --> [Single Agent Loop] --> Compliance Determination
                            (web search + DB tools + entity screening)
```

A single LLM agent with access to tools:
- **Web Search** — real-time sanctions list lookups and recent updates
- **Provisions Database** — queries indexed sanctions regulations
- **Entity Screening** — checks names against sanctions lists

The agent reasons through the scenario, uses tools as needed, and produces a compliance determination in a single conversational response.

## Usage

### In QueryLex

1. Go to **Create > Workflows**
2. Select **Sanctions Advisor (Classic)**
3. Ask your question (e.g., "Is it legal to ship medical equipment to Iran?")
4. Get a direct answer with citations

## Requirements

- LLM with tool-use support (GPT-4.1 recommended)
- No dataset required
- OpenAI API key (for default model)

## License

CC0 1.0 Universal - Public domain.
