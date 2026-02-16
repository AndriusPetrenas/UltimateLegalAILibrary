# French Contract Generator

Generate complete French-law-aware contracts from a brief description. Supports NDA, Service Agreements, and CDI (employment contracts).

## How It Works

```
User Brief --> [Classify Contract Type] --> [Generate French Contract] --> Complete Document
                  (gpt-4o-mini)                (gpt-4o)
```

**Step 1 - Classification:** Analyzes the user's brief to identify contract type, party types, sector, and key elements. Outputs structured JSON.

**Step 2 - Generation:** Uses the classification to generate a complete contract in French legal language with:
- Numbered articles (1, 2, 3...)
- `[A COMPLETER]` placeholders for variable data (names, addresses, amounts, dates)
- Legal references (e.g., Article 1231-5 du Code civil)
- Convention "bis" for inserted articles (5bis, 9bis)

## Supported Contract Types

| Type | Key Clauses |
|------|-------------|
| **NDA** | Parties, Definitions, Confidentiality obligations, IP, Duration, Return/destruction, Remedies |
| **Service Agreement** | Definitions, Services, Duration, Financials, Mutual obligations, IP, Liability, Termination |
| **CDI (Employment)** | Position, Compensation, Trial period, Working hours, Leave, Non-compete, Confidentiality |

## Output Format

The generated contract includes:
1. **Structure Summary** - Article count and key sections
2. **Complete Contract** - Full document with numbered articles
3. **Customization Guide** - Explanation of each `[A COMPLETER]` field
4. **Contract Strengths** - 3-5 highlights

## Usage

### Import into QueryLex

1. Go to **Create > Workflows**
2. Click **Import Workflow**
3. Upload `workflow.json`
4. Enter your brief (e.g., "NDA entre deux societes informatiques basees a Paris")
5. Run the workflow

### Download

```bash
curl -O https://raw.githubusercontent.com/AndriusPetrenas/UltimateLegalAILibrary/main/workflows/french-contract-generator/workflow.json
```

## Example

**Input:** "NDA entre une startup tech et un prestataire freelance pour un projet d'application mobile"

**Output:** Complete NDA with 12+ articles, all standard French NDA clauses, `[A COMPLETER]` markers for names, SIRET numbers, addresses, duration, and penalty amounts.

## Requirements

- GPT-4o-mini API access (classification step)
- GPT-4o API access (generation step)
- No dataset required

## License

CC0 1.0 Universal - Public domain.
