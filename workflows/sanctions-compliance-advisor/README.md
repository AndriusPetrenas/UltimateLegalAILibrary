# Sanctions Compliance Advisor (V3 — Deep Analysis)

Multi-node sanctions compliance pipeline covering EU, US (OFAC), UK (OFSI), and UN sanctions regimes. Designed for complex fact patterns involving ownership chains, designated entities, or multi-jurisdictional exposure.

**No dataset required.** The pipeline uses real-time web search, a built-in sanctions provisions database, and entity screening tools.

## How It Works

```
User describes scenario --> [Intake Questions] --> [Preprocessing] --> [Theory Analysis x N] --> [Synthesis]
                              (optional)           (parallel)           (concurrent)              (final report)
```

The pipeline operates in multiple stages:

### Stage 1 — Intake Questionnaire (Optional)
Analyzes the user's fact pattern and generates targeted clarification questions. Users can answer, skip, or the system auto-skips if the description is detailed enough.

### Stage 2 — Preprocessing
- Detects countries, entities, sectors, and transaction types
- Identifies applicable sanctions regimes
- Queries the provisions database for relevant legal bases

### Stage 3 — Concurrent Theory Analysis
For each relevant provision (up to 16+), runs parallel analysis threads:
- Maps legal elements against the fact pattern
- Checks for exemptions and licenses
- Evaluates ownership cascade (50% rule)
- Performs real-time web search for recent developments
- Dual-model evaluation for borderline cases

### Stage 4 — Synthesis
- Aggregates all theory results
- Produces a structured compliance determination
- Generates actionable recommendations
- Cites specific articles and provisions

## Coverage

| Jurisdiction | Programs | Examples |
|-------------|----------|---------|
| EU | Country-specific + thematic | Russia (833/2014), Syria, Iran, Belarus, Dual-Use (2021/821) |
| US (OFAC) | SDN, SSI, sectoral | Russia/Ukraine, Iran, DPRK, Cuba, counterterrorism |
| UK (OFSI) | Country + thematic | Russia, Syria, counterterrorism, cyber |
| UN | Security Council resolutions | DPRK, Iran, Libya, Somalia |

## Real-Time Tools

The pipeline uses several tools during analysis:
- **Web Search** — checks for recent sanctions updates, amendments, and delistings
- **Provisions Database** — queries indexed sanctions regulations for exact article text
- **Entity Screening** — checks names against sanctions lists (when configured)

## Usage

### In QueryLex

1. Go to **Create > Workflows**
2. Select **Sanctions Compliance Advisor**
3. Describe your scenario (e.g., "We want to export industrial pumps to a company in Dubai that is 60% owned by a Russian national listed on the EU sanctions list")
4. Answer intake questions if prompted (or click Skip)
5. Receive a structured compliance determination

### Example

**Input:** "A French company wants to sell luxury goods worth €500,000 to a trading company registered in Turkey. The Turkish company's majority shareholder is a Russian oligarch who was designated under EU Council Regulation 269/2014 in March 2022."

**Output:** Structured analysis covering:
- EU 269/2014 asset freeze (designated person control via ownership cascade)
- EU 833/2014 luxury goods prohibition (Art. 3h)
- Potential circumvention concerns (Art. 12 of 833/2014)
- OFAC SDN implications if US nexus exists
- Recommended compliance actions

## Requirements

- LLM with large context window (GPT-4.1 recommended)
- No dataset required
- OpenAI API key (for default model)
- Internet access (for web search tool)

## License

CC0 1.0 Universal - Public domain.
