# Query recipes

How to solve each type of question with as few commands as possible. The example answers use real data as of the stated date. In each query, always use the numbers the script returns.

## General flow

1. Identify the indicator and the entity, group or source (`SKILL.md` has the command table; `dictionary.md`, every field).
2. Run **one** command per source. With several sources, run them in parallel.
3. Check the JSON: `candidatos` (ask), `sin_dato_publicado` (say so), `sin_acceso_red` (ask for access), `null` (not published).
4. Answer with figure, unit, period and source. If there was a calculation, explain it.

---

## Type 1: one bank, one or more figures

**Question:** "How many credit cards does Galicia have, how many savings accounts, and what is its NPL?"

```bash
python3 scripts/consultar_entidad.py Galicia --campo pla cah irr_tot
```

Periods may differ: cards and accounts are quarterly, NPL is monthly.

> Banco Galicia, according to the BCRA (Financial Entities Information):
> - **Credit cards:** 4,930,958 plastics (June 2026).
> - **Savings accounts:** 10,607,086 accounts (June 2026).
> - **NPL:** 9.13% irregular portfolio over total financing (July 2026).

---

## Type 2: ranking or comparison

**Question:** "Which bank has the highest NPL?" or "Top 5 by branches?"

```bash
python3 scripts/consultar_ranking.py irr_tot --top 5
python3 scripts/consultar_ranking.py sucursales --top 5
```

Takes 2 to 4 seconds (queries the 60 banks in parallel). The JSON includes `valor_sistema_financiero` (system value) as a reference and the list of entities without data.

> The 5 banks with the highest NPL as of July 2026, according to the BCRA:
> 1. Banco de Servicios Financieros (Carrefour): 50.16%
> 2. Banco Sáenz: 48.70%
> 3. Banco Columbia: 27.80%
> 4. Banco Sucrédito Regional: 23.45%
> 5. Banco Rioja: 23.27%
>
> The financial system's NPL is 7.18%. *These are small banks with mostly consumer portfolios.*

**Systemic relevance.** If the question is about the banks that matter, use `--entre-mayores 20` (ranking only among the 20 largest by assets) or offer it as a second view:

```bash
python3 scripts/consultar_ranking.py irr_tot --entre-mayores 10 --top 5
```

**Market share:** `--participacion` adds the share of the system total (only for amounts and counts).

**Threshold:** "How many banks have NPL above 10%?" → `consultar_ranking.py irr_tot --mayor-que 10`. The field `filtro_valor.entidades_que_cumplen` gives the count.

**Lowest first:** `--asc` (for example, the lowest ROE).

**Finance companies or the whole system:** `--grupo companias` or `--grupo todas`.

---

## Type 3: evolution over time

**Up to 5 periods** (last 2 Decembers and last 3 months): one command, about 1 second.

```bash
python3 scripts/consultar_entidad.py Galicia --campo irr_tot --serie
```

**Six months or more:** monthly PDF, one file every 3 months. Takes a few more seconds: tell the user.

```bash
python3 scripts/consultar_historico.py Galicia --campo irr_tot --meses 12
```

> Banco Galicia NPL (irregular portfolio over financing), according to the BCRA:
> Feb-26: 7.65% · Mar-26: 7.68% · Apr-26: 8.09% · May-26: 8.94% · Jun-26: 8.30% · Jul-26: 9.13%.
> Up 1.48 points over the period.

Changes in amounts are nominal. To talk about real growth, adjust for inflation over the same span (type 4).

---

## Type 4: across sources

**Question:** "Did the average credit-card ticket beat inflation last month?"

Run in parallel:

```bash
python3 scripts/consultar_pagos.py --buscar "tarjetas de crédito" --hoja Tarjetas
python3 scripts/consultar_ipc.py --mes 2026-07
```

Use **the same month** in both sources: the latest payments month (`mes` in the JSON) usually lags the CPI. Ask for that month's CPI with `--mes`.

> In July 2026, the average credit-card purchase ticket rose 4.43% over June (from ARS 60,274 to ARS 62,945), while July inflation was 2.1% (INDEC). The ticket grew faster than prices: about 2.3% in real terms.
>
> *Average ticket = amount / number of transactions (BCRA, Retail Payments). Real change = 1.0443 / 1.021 − 1 (own calculation). Nominal amounts.*

**System NPL versus inflation:** NPL is a percentage (compared in points) and inflation is a price change. They are not directly comparable. Explain this and offer both series.

---

## Type 5: system or group totals

**Question:** "What is the average NPL of the system?" or "How many credit cards are there in total?"

```bash
python3 scripts/consultar_entidad.py sistema --campo irr_tot pla
```

The BCRA publishes the aggregate already weighted. Do not average entities by hand. Other groups: `publicos`, `privados`, `companias`, `top10`.

> The financial system's NPL is 7.18% as of July 2026, and there are 38,112,006 credit cards issued as of June 2026 (BCRA). *The system includes banks and finance companies.*

---

## Type 6: authorities and institutional data

**Question:** "Who is the chairman of Banco Macro?"

```bash
python3 scripts/consultar_entidad.py Macro --seccion ficha
```

Comes from the monthly PDF (needs `pdftotext`). Returns directors (`directivos`, with `cargo` role and `nombre` name: PRESIDENTE chairman, VICEPRESIDENTE vice-chairman, GERENTE GENERAL CEO, SINDICO statutory auditor), shareholders (`accionistas`), external auditor, tax ID (CUIT), head office and website. Cite the PDF month: authorities change.

---

## Type 7: inflation

| Question | Command |
|---|---|
| "What was last month's inflation?" | `consultar_ipc.py` |
| "And June's?" | `consultar_ipc.py --mes 2026-06` |
| "Year-to-date inflation?" | `consultar_ipc.py --acumulado 2026` |
| "Inflation over the last 12 months?" | `consultar_ipc.py` (`interanual` field of the headline) |
| "What was core inflation?" | `consultar_ipc.py` (Núcleo row) or `--serie nucleo --meses 6` |
| "Which division rose the most?" | `consultar_ipc.py --ranking-divisiones` |
| "How much did housing rise in 12 months?" | `consultar_ipc.py --serie vivienda --meses 12` (year-on-year of the latest month) |
| "Inflation between July 2025 and June 2026?" | `consultar_ipc.py --acumulado --desde 2025-07 --hasta 2026-06` |

If the user asks for a month INDEC has not yet published, the script says so and gives the latest available.

---

## Type 8: the data does not exist

Answer honestly and offer the closest figure, saying it is not exactly what was asked.

| Question | Answer |
|---|---|
| New customers of a bank | The BCRA does not publish customer additions. Closest: savings accounts (`cah`) and cardholders (`tit`), quarterly. |
| A bank's profit for the month | Results are published accumulated since the start of the fiscal year (`bRes`). One month's result is the difference between two accumulated figures of the same fiscal year: say it is a calculation. |
| A bank's time-deposit rate today | Not in these sources. `tasa_dep` is the period's average implicit rate, not the posted rate. |
| Exchange rate, stocks, news | Outside the sources (BCRA Financial Entities Information, Retail Payments and INDEC CPI). |
| Data on a digital wallet as an entity | Not on the financial-entity list. Aggregate payment accounts are in `consultar_pagos.py --buscar "cuentas de pago"`. |

---

## Ambiguity

- **Ambiguous bank:** the script returns `candidatos`. Ask, showing the list. Never pick one on your own.
- **No period given:** use the latest available and say which one.
- **Ambiguous indicator:** "accounts" may mean savings accounts (`cah`), checking accounts (`cc`) or payroll accounts (`remu`); "deposits" may mean the balance (`bDe`) or the number of accounts. Say which one you answer, or ask.

## Performance (measured in October 2026, with a good connection)

| Query | Time |
|---|---|
| One bank, any section (`consultar_entidad.py`) | ~1-2 s |
| Ranking of 60 banks (`consultar_ranking.py`) | ~2-4 s |
| Inflation (`consultar_ipc.py`) | ~2-3 s |
| Payments (`consultar_pagos.py`) | ~2-4 s |
| 12-month history (`consultar_historico.py`, 4 PDFs) | ~3-10 s depending on the connection |
| Institutional profile (PDF) | ~2-6 s depending on the connection |
| Repeating any query in the same session | instant (2-hour cache) |
