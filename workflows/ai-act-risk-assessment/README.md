# AI Act Risk Assessment

Classify any AI system under the EU AI Act (Regulation 2024/1689) through a guided conversational workflow. Get a structured risk classification and detailed compliance obligations.

**No dataset required.** The workflow includes a built-in knowledge base covering the full AI Act — definitions, prohibited practices, high-risk criteria, transparency obligations, GPAI rules, penalties, and deadlines.

## How It Works

```
User describes AI system --> [Smart Interview + Classification] --> Risk Assessment + Obligations
                                  (your selected model)
```

The workflow operates in **3 phases**, all handled by a single conversational node:

### Phase 1 — Smart Interview
Describe your AI system in plain language. The model reads your description and maps it against the full AI Act methodology. If anything is unclear that would change the legal outcome, it asks targeted questions (max 3-5). If your description is detailed enough, it skips straight to classification.

### Phase 2 — Classification
A structured 9-step assessment:

| Step | What it checks |
|------|---------------|
| 1 | Is it an AI system? (Art. 3(1)) |
| 2 | Is the AI Act applicable? (Art. 2 scope + exemptions) |
| 3 | Organization's role (Provider/Deployer/Importer/Distributor) |
| 4.1 | Prohibited practices screen (all 8 Art. 5 categories) |
| 4.2 | High-risk Pathway 1 — Annex I safety component |
| 4.3 | High-risk Pathway 2 — Annex III areas (8 categories) |
| 4.4 | Art. 6(3) filter — can high-risk be downgraded? |
| 5-8 | Deadlines, Transparency (Art. 50), GPAI (Art. 53-55), FRIA (Art. 27) |
| 9 | Final classification: Prohibited / High-Risk / Limited Risk / Minimal Risk |

Borderline cases get dual-scenario analysis with a conservative working assumption.

### Phase 3 — Obligations Report
After receiving your classification, ask for obligations to get:
- All applicable articles organized by role
- FRIA & governance requirements
- Regulatory interplay (GDPR, Product Liability Directive, DSA)
- Priority actions ranked 1-5 with deadlines
- Key enforcement dates

## No Dataset Required

This workflow includes an **embedded AI Act knowledge base** (compressed XML reference) covering:
- Art. 3 definitions (AI system, provider, deployer)
- Art. 2 scope and exemptions
- Art. 5 prohibited practices (all 8 categories with exceptions)
- Art. 6 + Annex I/III high-risk criteria
- Art. 50 transparency obligations
- Art. 53-55 GPAI rules
- Penalty tiers (up to 35M EUR / 7% turnover)
- Full timeline (Feb 2025 through Aug 2027)
- Detailed obligations for providers, deployers, GPAI, and universal duties

The model combines this reference with its training data. **Optionally**, if you have AI Act legal sources enabled or a dataset containing AI Act text, the workflow will retrieve relevant passages for more precise citations.

## Usage

### Import into QueryLex

1. Go to **Create > Workflows**
2. Click **Import Workflow**
3. Upload `workflow.json`
4. Describe your AI system (e.g., "We are developing a CV screening tool that ranks job applicants for a French company")
5. The workflow will interview you, classify your system, and provide obligations on request

### Download

```bash
curl -O https://raw.githubusercontent.com/AndriusPetrenas/UltimateLegalAILibrary/main/workflows/ai-act-risk-assessment/workflow.json
```

## Example

**Input:** "We are building a chatbot for our bank that uses GPT-4o to answer customer questions about their accounts and suggest financial products. Deployed in France."

**Phase 1:** The model may ask 2-3 targeted questions — e.g., does the chatbot make autonomous decisions about credit? Are the suggestions personalized based on customer financial data?

**Phase 2 output:** Structured classification covering all 9 steps, ending with something like:

> **FINAL CLASSIFICATION: LIMITED RISK** 🟡
>
> **Maximum penalty exposure:** 15M EUR or 3% of annual worldwide turnover

**Phase 3 output:** Full obligations report with Art. 50 transparency duties, AI literacy requirements (Art. 4), GPAI provider verification, and priority action items.

## Requirements

- Any LLM supported by QueryLex (GPT-4o, Claude, etc.)
- No dataset required
- No API keys beyond your LLM provider

## License

CC0 1.0 Universal - Public domain.
