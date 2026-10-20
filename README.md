# Argentine Financial System Oracle · Oráculo del Sistema Financiero Argentino

> **Available in English and Spanish — Disponible en inglés y español**

A **Claude Skill** that answers questions about the Argentine financial system by querying live official sources from the **BCRA** and **INDEC**. Ask in natural language — *"How many credit cards does Banco Galicia have?"*, *"Which bank has the highest NPL?"*, *"What was June's inflation?"* — and the oracle fetches the figure from the official report, validates it is the latest version, extracts it, and responds citing the period and source.

Un **Skill de Claude** que responde preguntas sobre el sistema financiero argentino consultando en vivo las fuentes oficiales del **BCRA** y el **INDEC**. Preguntás en lenguaje natural —"¿cuántas tarjetas de crédito tiene el Banco Galicia?", "¿qué banco tiene más mora?", "¿cuál fue la inflación de junio?"— y el oráculo va a buscar el dato al reporte oficial, valida que sea la última versión disponible, lo extrae y te responde citando el período y la fuente.

---

## How it works / Cómo funciona

**It does not use cached data or model memory.** For each question it:

1. **Identifies** what data was requested and which official source holds it.
2. **Downloads the latest published report** from that source, at query time.
3. **Validates it is the most recent available version** (BCRA and INDEC reports are published with a lag and with filenames that change monthly; the oracle tries backwards until it finds the newest valid file).
4. **Extracts the exact figure** from the report using tested parsing scripts.
5. **Responds** with the figure, the period it covers, and the source.

Since each query involves downloading and processing an official report (some weighing several MB), **responses take as long as that download and extraction** — they are not instant. In return, you get real, verifiable official data, not an estimate.

**Most importantly: if the data does not exist in any report, the oracle says so.** It does not fabricate, approximate, or complete with general knowledge.

---

## What it can answer / Qué puede responder

Any indicator published in these official sources:

**BCRA — Financial Entities** (monthly): NPL and irregular portfolio, debt situations 1–5, provisions, balance sheet (assets, loans, deposits, equity), ratios (ROE, ROA, leverage, rates, liquidity).

**BCRA — Additional Information** (quarterly): credit and debit cards, savings accounts, payroll accounts, branches, ATMs, employees.

**BCRA — Retail Payments** (monthly): volume and amount of transfers, cards, direct debits, checks, ECHEQ, average ticket.

**INDEC — National CPI** (monthly): inflation (headline, core, regulated, seasonal), monthly and year-on-year change, basket divisions.

### Example questions / Ejemplos de preguntas

- "How many savings accounts does Banco Nación have?" / "¿Cuántas cajas de ahorro tiene el Banco Nación?"
- "Top 5 banks by NPL rate" / "Top 5 bancos por mora"
- "How did Galicia's NPL evolve over the last year?" / "¿Cómo evolucionó la mora del Galicia en el último año?"
- "Did the average credit card ticket beat inflation last month?" / "¿El ticket promedio de crédito le ganó a la inflación el último mes?"

See more examples in [`docs/EJEMPLOS.md`](docs/EJEMPLOS.md).

---

## Installation / Instalación

### Requirements / Requisitos
A Claude environment with **code execution** enabled (Claude's analysis tool, Claude Code, or Cowork). The oracle needs to run downloads (`wget`) and Python parsing scripts. Without it, Claude can read the instructions but cannot fetch data.

### Steps / Pasos

1. Download the skill file: **`bcra-oraculo.skill`** (in this repository).
2. Install it in Claude:
   - On **claude.ai**: Settings → Skills → upload the file.
   - On **Claude Code / Cowork**: follow your environment's skill installation instructions.
3. Done. In any new conversation (with the analysis tool active), ask anything about the Argentine financial system and the skill activates automatically — **in whichever language you use**.

> On first run, if a Python library is missing, the skill installs it automatically (`xlrd`, `openpyxl`).

---

## Repository structure / Estructura del repositorio

```
BCRA-Oracle/
├── README.md
├── LICENSE
├── skill/
│   ├── bcra-oraculo/            → Spanish skill (Skill en español)
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── fuentes.md
│   │   │   ├── diccionario.md
│   │   │   └── consultas.md
│   │   └── scripts/
│   │       ├── consultar_entidad.py
│   │       ├── consultar_ipc.py
│   │       ├── consultar_pagos.py
│   │       └── requirements.txt
│   └── bcra-oracle-en/          → English skill (Skill en inglés)
│       ├── SKILL.md
│       ├── references/
│       │   ├── sources.md
│       │   ├── dictionary.md
│       │   └── queries.md
│       └── scripts/             → same scripts as Spanish version
├── docs/
│   └── EJEMPLOS.md
└── bcra-oraculo.skill           → packaged skill, ready to install
```

---

## Limitations / Limitaciones

- **Only answers what is in the sources.** Exchange rates, stocks, rates from other countries, news: out of scope.
- **Requires code execution.** Does not work in a Claude environment without the analysis tool.
- **Official sources change without notice.** The BCRA and INDEC sometimes modify formats or filenames. When that happens, extraction may need an adjustment; the skill gives Claude the context to adapt, but it is not infallible.
- **No dashboards.** This project only queries and answers data.

---

## Official sources / Fuentes oficiales

- BCRA — Financial Entities / Entidades Financieras: https://www.bcra.gob.ar/PublicacionesEstadisticas/Entidades_financieras.asp
- BCRA — Retail Payments / Pagos Minoristas: https://www.bcra.gob.ar/PublicacionesEstadisticas/Informe-mensual-pagos-minoristas.asp
- INDEC — CPI / IPC: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31

---

## License / Licencia

MIT — see [LICENSE](LICENSE). Free to use, modify and redistribute, keeping the copyright notice.

## Author / Autor

Alejandro Vaamonde

---

*This project is not affiliated with or endorsed by the BCRA, INDEC, or Anthropic. It queries public data from official sources.*

*Este proyecto no está afiliado ni respaldado por el BCRA, el INDEC ni Anthropic. Consulta datos públicos de fuentes oficiales.*
