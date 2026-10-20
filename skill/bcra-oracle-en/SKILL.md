---
name: bcra-oracle-en
description: Query official Argentine financial system data (BCRA and INDEC) to answer specific and analytical questions. Use ALWAYS when the user asks about Argentine bank indicators such as credit/debit cards, savings accounts, deposits, loans, non-performing loans (NPL), branches, ATMs, employees, ROE, ROA, leverage, balance sheet, or INDEC inflation figures, or comparisons and rankings between financial entities (which bank has the most X, how did Y evolve, top 5 by Z). The skill downloads the latest available official report, validates it is the most recent version, extracts the real data and responds citing the period and source. If the data does not exist in any report, it states so — it never fabricates. Does not produce dashboards or HTML files, only queries and answers.
---

# Oracle of the Argentine Financial System

This skill answers questions about the Argentine financial system by fetching **real** data from official sources (BCRA and INDEC) at query time. It does not use cached data or model memory: for each question it downloads the latest published report, validates it is the most recent available version, extracts the exact figure and responds.

## Golden rule: never fabricate

This is the skill's most important rule and admits no exceptions:

- **Only respond with data extracted from an official source in this same session.** Never answer from memory, general knowledge, or estimates.
- **If the data is not in the reports, explicitly state that it is unavailable.** Do not approximate, fill in, or "give a ballpark". An honest "the BCRA does not publish that figure" is worth more than a made-up number.
- **Always cite the data's period and source.** E.g.: "according to the BCRA Financial Entities report for March 2026". This makes the answer verifiable.
- **Distinguish direct data from calculated data.** If the question requires a calculation (market share, ranking, variation), say so and briefly explain how it was derived.
- **When in doubt whether a number is real or remembered, do not use it.** Go back to the source.

## Flow for answering a question

### 1. Identify what data is requested and where it lives

Map the indicator in the question to its source. The full map is in `references/dictionary.md`, but broadly:

| Question topic | Source | Report |
|---|---|---|
| Credit/debit cards, savings accounts, payroll accounts, branches, ATMs, employees | BCRA | Additional Information (Entities) |
| NPL, irregular portfolio, situations 1–5, provisions, portfolio quality | BCRA | Financial Entities (PDF) |
| Balance sheet: assets, loans, deposits, equity | BCRA | Financial Entities (PDF) |
| Ratios: ROE, ROA, leverage, rates, liquidity | BCRA | Financial Entities (PDF) |
| Volume and amount of payments, transfers, average ticket, checks, ECHEQ | BCRA | Monthly Retail Payments Report (XLSX) |
| Inflation, CPI, price changes, basket, divisions | INDEC | National CPI (XLS) |

Read `references/sources.md` for exact URLs and download pitfalls (critical — see below).

### 2. Download the latest available version

**This step is mandatory for every query.** Do not assume a previously downloaded file is still current. Download the corresponding source and **validate it is the most recent** by following the rules in `references/sources.md`.

Critical pitfalls the skill must handle (full detail in `references/sources.md`):
- **INDEC:** the file is named by its **publication month**, not by the data month. The June CPI is published in July → file `sh_ipc_07_26.xls`. Try from the current month backwards until a valid file is found (~2.3 MB; future months return a ~36 KB placeholder).
- **BCRA large PDF (>5 MB):** Drive tools fail. Use `wget` directly + `pdftotext -layout`.
- **BCRA Payments:** the URL slug alternates between two patterns; try both.

To find the latest available period, try the most recent month and work backwards until the download succeeds.

### 3. Extract the data with the scripts

Use the corresponding extractor in `scripts/`:
- `consultar_entidad.py` — ratios, balance sheet, NPL and portfolio quality for one bank (or all) from the BCRA PDF.
- `consultar_adicional.py` — cards, accounts, branches, ATMs, employees from Additional Information.
- `consultar_pagos.py` — payment instruments from the BCRA XLSX.
- `consultar_ipc.py` — inflation from the INDEC XLS.
- `consultar_ranking.py` — for analytical questions that scan all banks.

Each script receives the already-downloaded source and returns parsed data. See `references/queries.md` for how to call them and how to resolve each question type.

### 4. Respond

Response format:
- **The figure**, with its unit.
- **The period** it refers to.
- **The official source**.
- If calculated, **how it was derived**.

**Example — direct figure:**
> Banco Galicia had **4,383,666 credit card plastics** issued as of **March 2026**, according to the BCRA Additional Information on Financial Entities.

**Example — calculated figure:**
> Banco Galicia holds a **9.3% market share** of debit cards as of March 2026 (7.5M bank cards out of 81.7M system-wide). *Market share calculated over the total of the 45 entities that report debit cards.*

**Example — unavailable data:**
> The BCRA does not publish the number of customers per branch in its Financial Entities reports. The closest available figures are branch count (321 for Galicia as of March 2026) and employees (6,025), but not the customers-per-branch ratio.

## Question types

### Point queries (one bank, one indicator)
"How many savings accounts does Banco Nación have?" → download the source, extract the figure for that bank, respond.

### Analytical queries (comparisons, rankings, trends)
"Which bank has the highest NPL?", "Top 5 by branch count?", "How did Galicia's NPL evolve over the past year?" → these require iterating over **all** banks or **multiple periods**. Use `consultar_ranking.py`. Warn the user it may take a bit longer since it processes the full report. Details in `references/queries.md`.

### Cross-source queries (mixing sources)
"Did the average credit card ticket beat inflation last month?" → download Payments (BCRA) and CPI (INDEC), extract both, compare. Note that they are two different sources and may have different publication lags.

## Bank identification

Names vary across reports. Use the mapping in `references/dictionary.md` (section "Entity identification"). Common cases:
- User says "Galicia" → "BANCO DE GALICIA Y BUENOS AIRES S.A.U." (code 7).
- "Nación" → "BANCO DE LA NACION ARGENTINA" (code 11).
- "Provincia" → "BANCO DE LA PROVINCIA DE BUENOS AIRES".
- Variants with accents, "S.A.", "S.A.U.", branches, etc. Search flexibly (case- and accent-insensitive); if ambiguous, ask the user which candidate they mean.

If the bank does not exist in the report, say so: "I cannot find an entity with that name in the BCRA report. The most similar entities are: [list]."

## What this skill does NOT do

- **No dashboards or HTML files.** If the user asks for a dashboard, clarify that this skill only queries and answers data; a separate skill/project handles dashboards.
- **No data outside the sources.** Exchange rates, stocks, rates from other countries, news: out of scope. Respond "that is not in the sources I query (BCRA and INDEC)".
- **No fabrication.** See the golden rule.

## Environment requirements

This skill requires a code-execution environment (`wget`, `python3` with `xlrd`/`openpyxl`, `pdftotext`). Without it, Claude can read the instructions but cannot execute downloads or extractions. Install dependencies if missing:
```bash
pip install xlrd openpyxl --break-system-packages
```

## Reference files

- `references/sources.md` — official URLs, download patterns, and all known pitfalls. **Read before every download.**
- `references/dictionary.md` — what each field is, which source it comes from, units, how it is calculated, and entity identification. **Read to map questions to data.**
- `references/queries.md` — recipes for resolving each question type (point, analytical, cross-source), with examples.
