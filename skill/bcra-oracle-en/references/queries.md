# Query recipes

How to resolve each question type, with concrete examples. The scripts in `scripts/` handle the extraction; this document explains when to use each one and how to compose the response.

## General flow (always)

1. Identify the indicator(s) and their source (see `dictionary.md`).
2. Download the latest version of the source(s) (see `sources.md`).
3. Validate against checksums if applicable.
4. Extract with the corresponding script.
5. Respond with figure + period + source. If it does not exist, say so.

---

## Type 1 — Point query (one bank, one or more indicators)

**Example:** "How many credit cards does Banco Galicia have? And savings accounts? What is its NPL rate?"

Recipe:
1. Resolve "Galicia" → code 7 (see dictionary, Entity identification).
2. Credit cards and savings accounts → Additional Information (quarterly). Download and run `consultar_adicional.py`.
3. NPL → Entities PDF (monthly). Run `consultar_entidad.py`.
4. Respond with all three figures, each with its own period (they may differ — cards as of March, NPL as of April):

> Banco Galicia, according to BCRA data:
> - **Credit cards:** 4,383,666 plastics issued (Additional Information, March 2026).
> - **Savings accounts:** 10,316,472 accounts (Additional Information, March 2026).
> - **NPL rate:** 8.09% irregular portfolio (Financial Entities, April 2026).

---

## Type 2 — Analytical query: ranking / comparison

**Example:** "Which bank has the highest NPL?" / "Top 5 by branch count?" / "The 3 largest banks by assets?"

These require iterating over **all** banks in the report. Use `consultar_ranking.py`, which extracts the requested indicator for all entities and sorts them.

Recipe:
1. Warn the user it may take a bit longer (processes the full report, not a single bank).
2. Download the corresponding source.
3. Run `consultar_ranking.py` with the requested indicator.
4. Respond with the ranking, stating the period and, if applicable, filtering out irrelevant entities (e.g., exclude finance companies if the question is about banks only).

> The 5 banks with the highest NPL rate (irregular portfolio), as of April 2026, according to the BCRA:
> 1. Banco de Servicios Financieros — 50.5%
> 2. Banco Sáenz — 37.7%
> 3. Banco Sucrédito Regional — 24.8%
> 4. Banco Rioja — 22.8%
> 5. Ualá Bank — 22.1%
>
> *Sorted by irregular portfolio as a share of total financings. Note: some are niche banks with mostly consumer portfolios.*

**Caution with NPL rankings:** small and niche banks tend to top these lists. If the question is about systemic relevance, offer each bank's market weight as well, or filter by minimum size — but only if the user asks, or if adding context prevents a misleading reading.

---

## Type 3 — Trend query (one bank/indicator, multiple periods)

**Example:** "How did Banco Galicia's NPL evolve over the past year?"

Requires multiple periods. Two approaches depending on the source:
- **Payments and CPI:** a single file contains the full historical series → download one file and extract the full series.
- **Entities (NPL, balance sheet):** each month is a separate PDF → download multiple PDFs (one per period). Warn the user this takes longer. Download the months in the requested range and extract the indicator from each.

Recipe for Galicia NPL over the past year:
1. Determine which months are available over the past year.
2. For each month, download the Entities PDF and extract `irr_tot` for Galicia.
3. Present the series:

> Banco Galicia NPL rate (irregular portfolio) — recent months, BCRA:
> - Dec-25: 6.9%
> - Jan-26: 7.7%
> - Feb-26: 7.7%
> - Mar-26: 7.7%
> - Apr-26: 8.1%
>
> NPL rose from 6.9% to 8.1% over the period.

---

## Type 4 — Cross-source query (mixing sources)

**Example:** "Did the average credit card ticket beat inflation last month?"

Combines two sources. Download both, extract, compare. Note that they are different sources with potentially different publication lags.

Recipe:
1. Average credit ticket → Payments (BCRA XLSX). Extract amount/transactions for the latest month and the prior month; calculate the ticket change.
2. Monthly inflation → CPI (INDEC XLS) for the same month.
3. Compare:

> In [month], the average credit card purchase ticket changed +X% while inflation was +Y% (INDEC). The ticket [grew more/less] than prices that month.
>
> *Average ticket = total amount / number of transactions (BCRA, Retail Payments). Inflation = month-on-month CPI change, headline (INDEC). Both sources may have different publication lags — verify that the periods align.*

---

## Type 5 — Data does not exist

**Example:** "How many new customers did Bank X add last month?"

The BCRA does not publish new customer additions. Respond honestly:

> The BCRA does not publish new customer figures by bank in its reports. The closest available data are the number of savings accounts and credit card holders, but not net customer additions per period.

Never fabricate or estimate. If there is a *nearby* figure that could be useful, offer it while clarifying it is not exactly what was requested.

---

## Handling ambiguity

- **Ambiguous bank name:** if "Banco Provincia" could be Buenos Aires or another province, list the candidates and ask.
- **Period not specified:** use the latest available and state it. If the user wants a different period, they can ask.
- **Ambiguous indicator:** "accounts" may refer to savings accounts, checking accounts, or payroll accounts. If unclear, state which one is being answered, or ask.

## Performance

- **Point query on one bank:** one download (fast for XLSX/XLS, slower for the ~6 MB PDF).
- **Analytical query (ranking):** one download + processing all banks.
- **Trend query on Financial Entities:** multiple downloads (one PDF per month). The slowest type — warn the user.
- **Within the same session:** reuse already-downloaded files for the same period instead of downloading again.
