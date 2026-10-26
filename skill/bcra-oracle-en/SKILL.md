---
name: bcra-oracle-en
description: Queries live official data on the Argentine financial system (BCRA and INDEC) and answers with the figure, its period and the source. Use ALWAYS when the user asks about Argentine banks or finance companies (non-performing loans, debtor classification, loans, deposits, assets, equity, results, ROE, ROA, leverage, liquidity, rates, credit or debit cards, savings accounts, payroll accounts, employees, branches, ATMs, chairman or shareholders), rankings or comparisons between entities (which bank has the most X, top 5 by Z, market share), how an indicator evolved, financial-system totals, INDEC inflation (headline, core, basket divisions, cumulative CPI) or payment instruments (transfers, cards, checks, ECHEQ, average ticket). If the figure is not published, it says so instead of making it up. Does not build dashboards.
compatibility: Requires code execution with Python 3.8+ and network access to www.bcra.gob.ar and www.indec.gob.ar. pdftotext (poppler-utils) is only needed for series longer than 5 periods and for the institutional profile.
---

# Oracle of the Argentine Financial System

Answers questions about the Argentine financial system with official BCRA and INDEC data fetched at query time. The scripts in `scripts/` download the latest publication, extract the figure and return JSON with value, period, unit and source.

The scripts are shared with the Spanish version, so **command options and JSON keys are in Spanish**. Answer the user in their language. The key words you will see: `valor` value, `periodo` period ("YYYY-MM"), `unidad` unit, `desc` description, `datos` data, `fuente` source, `serie` series, `candidatos` candidates, `sin_dato_publicado` not published, `sin_acceso_red` no network access, `millones de pesos` millions of pesos, `cantidad` count.

## Golden rule: never fabricate

- **Only answer with data a script returned in this session.** Never from memory or with estimates.
- **If the figure is not published, say so.** "The BCRA does not publish that figure" is worth more than an approximate number.
- **Always cite period and source.** Example: "according to the BCRA (Financial Entities Information), as of July 2026".
- **Separate direct from calculated figures.** If there was a calculation (market share, change, average ticket, irregular portfolio from debtor categories), say so and explain the formula in one line.
- **`null` in the JSON means "not published"**, never zero.

## One command per question

Run from this skill's folder (paths are relative to this file). The scripts only use standard Python: **do not install anything**. Repeating a query in the same session is instant, because the scripts cache downloads for 2 hours.

**For common questions, do not read the references:** the command is in this table.

| The question asks for | Command |
|---|---|
| Overview of a bank | `python3 scripts/consultar_entidad.py Galicia` |
| One or more figures of a bank | `python3 scripts/consultar_entidad.py Galicia --campo irr_tot pla roe` |
| Cards, accounts, time deposits, employees | `python3 scripts/consultar_entidad.py Nacion --seccion adicional` |
| Branches and ATMs (by province) | `python3 scripts/consultar_entidad.py Macro --seccion sucursales --provincias` |
| Balance sheet or income statement | `python3 scripts/consultar_entidad.py Santander --seccion balance` |
| Debtor classification (categories 1 to 5) | `python3 scripts/consultar_entidad.py BBVA --seccion cartera` |
| Chairman, CEO, shareholders, auditor | `python3 scripts/consultar_entidad.py Galicia --seccion ficha` |
| System or group totals | `python3 scripts/consultar_entidad.py sistema --campo irr_tot pla` (groups: `sistema` whole system, `publicos` public, `privados` private, `companias` finance companies, `top10` top 10 private banks) |
| Ranking or comparison between entities | `python3 scripts/consultar_ranking.py irr_tot --top 5` |
| Market share | `python3 scripts/consultar_ranking.py pla --top 10 --participacion` |
| How many entities exceed a threshold | `python3 scripts/consultar_ranking.py irr_tot --mayor-que 10` |
| Recent evolution (up to 5 periods) | `python3 scripts/consultar_entidad.py Galicia --campo irr_tot --serie` |
| Evolution over 6 months or more | `python3 scripts/consultar_historico.py Galicia --campo irr_tot --meses 12` |
| Panel of many entities and months in one CSV (for analysis or for another skill) | `python3 scripts/consultar_panel.py --meses 24 --salida panel.csv` (`--top 20`, `--entidades Galicia Macro`, `--historicas` to add entities that no longer exist) |
| Last month's inflation (with divisions) | `python3 scripts/consultar_ipc.py` |
| Inflation for a month, a series or cumulative | `python3 scripts/consultar_ipc.py --mes 2026-06` · `--serie nucleo --meses 12` · `--acumulado 2026` · `--acumulado --desde 2025-07 --hasta 2026-06` |
| Which basket division rose the most | `python3 scripts/consultar_ipc.py --ranking-divisiones` |
| Payment instruments | `python3 scripts/consultar_pagos.py --buscar "tarjetas de crédito"` (search text is in Spanish; add `--meses 12` for the series; `--series` lists everything) |

If the question mixes sources (for example, average ticket against inflation), run the needed commands **in parallel** and combine the results.

### Most used fields

Full list: `python3 scripts/consultar_entidad.py --campos` or `references/dictionary.md`.

- **NPL and portfolio quality (monthly, %):** `irr_tot` total NPL · `irr_cons` consumer · `irr_com` commercial · `irr_priv` private sector · `prev_irr` provision coverage · `tf_s1`…`tf_s5` debtor categories · `tf_irregular` categories 3+4+5.
- **Profitability and other ratios (monthly):** `roe` · `roa` · `apalancamiento` leverage (times) · `tasa_prest` lending rate · `tasa_dep` deposit rate · `liq_tit_cot` liquidity · `dep_empleado` deposits per employee.
- **Balance sheet (monthly, millions of pesos):** `bA` assets · `bPr` loans · `bDe` deposits · `bPN` equity · `bCA` savings-account balances · `bPF` time deposits · `bRes` year-to-date result · `bIrrec` write-offs (uncollectible loans moved off the balance sheet).
- **Additional information (quarterly, counts):** `pla` credit cards · `tit` cardholders · `deb` debit cards · `cah` savings accounts · `cc` checking accounts · `emp` employees.
- **Monthly, counts:** `remu` payroll accounts · `sucursales` branches · `cajeros` ATMs.

## How to read the script output

- `datos.<field>.valor` and `.periodo` ("YYYY-MM"): the figure and the month it refers to.
- `candidatos`: the name is ambiguous. Ask the user which one they mean, showing the candidates.
- `sugerencias_por_parecido` with the error "no figura en la nómina" (not on the list): the entity is not a registered bank or finance company (for example, a digital wallet). Say so. Do not pick a suggestion on your own.
- `sin_dato_publicado` or `sin_dato_en_el_periodo`: the BCRA does not publish that figure for that entity. Say so.
- `sin_acceso_red: true`: the environment cannot reach the sources. Ask the user to allow network access to `www.bcra.gob.ar` and `www.indec.gob.ar` in their code-execution settings, or to upload the file. Never answer from memory.
- Error "Falta pdftotext" (pdftotext missing): only affects `consultar_historico.py` and `--seccion ficha`. If the environment allows it, install it (`apt-get install -y poppler-utils`). If not, say that query is not available and offer the 5 periods from `--serie`.

## Answer format

Give the figure with its unit, the period and the source. If calculated, add how it was derived.

> Banco Galicia had **4,930,958 credit cards** (plastics) as of **June 2026**, according to the BCRA Financial Entities Information.

> Galicia holds **12.9%** of the system's credit cards as of June 2026 (4.93 million out of 38.1 million). *Market share calculated over the whole financial system.*

> The BCRA does not publish the number of customers per bank. The closest figures it publishes are savings accounts (10,607,086 at Galicia as of June 2026) and credit-card holders.

*(The numbers in these examples are real as of the stated date; in each query use the ones the script returns.)*

## Pitfalls that change the answer

- **Periods differ by section.** Balance sheet, ratios, NPL, branches and payroll accounts are monthly. Cards, accounts and employees are quarterly: their latest period may be earlier. If an answer mixes figures, give each one's period.
- **Units.** The balance sheet is in millions of current pesos (40,325,296.7 million = 40.3 trillion pesos). Debtor classification amounts are also in millions. Ratios and NPL are in %.
- **Nominal values.** When comparing amounts over time, warn that they are not inflation-adjusted. If needed, adjust with `consultar_ipc.py` and label it as a calculation.
- **NPL rankings.** Small or niche banks usually top them. If the question is about systemic relevance, use `--entre-mayores 20` (only among the 20 largest by assets) or offer it.
- **History:** `consultar_historico.py` goes back to 2014 with every field. For 2011-2013 the NPL ratios are missing; there is no history before 2011. It only works for entities that exist today; renamed ones (Santander Río, BBVA Francés) are found too.
- **"Sistema"** includes banks and finance companies. Rankings only include banks (public and private) unless `--grupo todas` or `--grupo companias` is used.
- **Aliases.** "Provincia" is Banco de la Provincia de Buenos Aires. "Nación" is Banco de la Nación Argentina. "Naranja X" is Naranja Digital Compañía Financiera. For any other doubt, the script returns candidates.

## What this skill does NOT do

- No dashboards, charts or HTML: it only queries and answers.
- No data outside these sources: exchange rates, stocks, posted time-deposit rates or news. Say "that is not in the sources I query (BCRA and INDEC)".
- No fabrication. See the golden rule.

## References (read only if needed)

- `references/dictionary.md`: every field, unit, frequency and which calculations are possible. Read it if the question uses a concept not listed above.
- `references/queries.md`: recipes for analytical, evolution, cross-source and "data does not exist" questions.
- `references/sources.md`: URLs, the format of each source, known pitfalls and how to adapt if the BCRA or INDEC change something. Read it only if a script fails.
- `references/contrato.md` (in Spanish): what another skill can use from this one (functions, scripts, output format and versioning policy). Read it when building a skill on top of this one.
