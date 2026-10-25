# Official sources and known pitfalls

The scripts already handle everything below. Read this document only if a script fails or a source has changed. URLs and formats were verified in October 2026.

## Contents
1. BCRA: Financial Entities Information API (main source)
2. BCRA: monthly Financial Entities Information PDF (history and profile)
3. BCRA: Monthly Retail Payments Report (XLSX)
4. INDEC: National CPI (CSV)
5. Network access
6. Control values to check that parsing still works
7. If a source changes

---

## 1. BCRA: Financial Entities Information API

This is the JSON API behind the "Información de Entidades Financieras" pages on www.bcra.gob.ar. It answers in about 1 second with a few KB per entity and section. `consultar_entidad.py` and `consultar_ranking.py` use it.

| Section | Endpoint (`https://www.bcra.gob.ar/api/endpoints/...`) | Parameters |
|---|---|---|
| Entity list | `nomina-entidades.php` | `action=nomina_AAA00&lang=es` |
| Ratios | `indicadores-economicos.php` | `action=indicadores&category=00007&lang=es` |
| Financial statements | `entidades-financieras-estados-contables.php` | `category=00007&lang=es` |
| Debtor classification | `entidades-financieras-situacion-deudores.php` | `category=00007&lang=es` |
| Structure (additional info, payroll accounts, branches) | `entidades-financieras-informacion-estructura.php` | `category=00007&detalle=1&detalle_sub=&lang=es` |

- `category` is the 5-digit BCRA code (Galicia = `00007`) or a group: `AAA00` financial system, `AAA10` public, `AAA20` private, `AAA30` finance companies, `AAA50` top 10 private banks.
- Each response includes `fecha_actualizacion` (month of the latest information) and 5 period columns.

**Pitfalls:**
- **Different units per section.** Financial statements in **thousands** of pesos (the script converts to millions). Debtor classification in **millions**. Ratios in %.
- **0 means "no data".** The BCRA website shows 0 as an empty cell, and the PDF shows "---". Ratios also use **99999** as a "not applicable" marker. The scripts turn both into `null`. Without this filter, a consumer-NPL ranking would put an entity with 99999% first.
- **Truncated names.** The entity list cuts names at 40 characters, some endpoints at 35.
- **Quarterly additional information with zeros.** A newly published quarter may be incomplete: some rows are 0 (turned into `null`).

**Pages to cite** (replace `00007` with the entity code):
- Ratios: `https://www.bcra.gob.ar/entidades-financieras-indicadores-economicos/?bco=00007&tipo=1`
- Financial statements: `https://www.bcra.gob.ar/entidades-financieras-estados-contables?bco=00007&tipo=1`
- Debtor classification: `https://www.bcra.gob.ar/entidades-financieras-situacion-deudores?bco=00007&tipo=1`
- Structure: `https://www.bcra.gob.ar/entidades-financieras-informacion-estructura?bco=00007&tipo=1&Tit=1`
- System total: `https://www.bcra.gob.ar/total-del-sistema-financiero/`

The old page `https://www.bcra.gob.ar/PublicacionesEstadisticas/Entidades_financieras.asp` returns 404. Do not cite it.

---

## 2. BCRA: monthly Financial Entities Information PDF

`https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/YYYYMMe.pdf` (July 2026: `202607e.pdf`).

Used by `consultar_historico.py` (series longer than 5 periods) and `consultar_entidad.py --seccion ficha` (directors, shareholders, auditor, contact details, which the API does not publish).

- **Variable size:** 3.5 to 17 MB depending on the month, with the same structure (387 pages).
- **Structure:** index on pages 5-6, then 4 pages per entity: (1) profile and locations, (2) financial statements in millions, (3) ratios with reference columns (institutional group, top 10, system), (4) additional information, payroll accounts and debtor classification. Each entity's first line is `CODE - NAME` (for example `00007 - BANCO DE GALICIA...`).
- **Speed:** the script reads the index and converts only the entity's 4 pages with `pdftotext -layout -f N -l M` (~0.1 s), not the whole document (~5 s).
- **Coverage:** each PDF holds the last 3 months plus the last 2 Decembers. 12 months need 4 PDFs (one every 3 months).
- **Available history (tested in October 2026):** complete since 2014. For 2011-2013, balance sheet, additional information and ROE are read, but not the NPL ratios: the BCRA used different codes then (for example, A11 was "commercial irregular portfolio"). The script checks each ratio's title and does not report those that do not match, so a value is never attributed to the wrong ratio. For 2010 and earlier, the PDF index has another format and cannot be read.
- **Revisions:** a month's value can change between PDF editions. If several downloaded PDFs include the same month, the script uses the most recent one.
- **Month not yet published:** the server answers 404 with an HTML page. The script checks that the file starts with `%PDF`.
- **Page numbering:** the page printed in the index and the file page differ by 0 to 3 depending on the month. The script looks for the page that starts with the entity code. For groups, it measures that difference with an entity in the same PDF.
- **Renamed entities:** the index uses the name at the time (Santander Río, BBVA Francés). If the current name is not in the index, the script looks for the entity code across the whole document: about 2 s the first time, and the result is cached.

**Pitfalls:**
- **Merged columns.** Sometimes two numbers are separated by a single space. The parser reads values token by token from the end of the line. If a row has fewer values than periods, it drops the row instead of guessing.
- **Millions without separator.** Older PDFs print `1477.466,3` instead of `1.477.466,3`. The parser accepts both.
- **Side text.** The entity name runs vertically in the margin and mixes into some lines. It is ignored.
- **Incomplete recent quarter.** In a given month's PDF, the latest "Información adicional" quarter may be mostly "---". The next month's PDF fills it in: if the last PDF read is from a quarter-end month and that data is missing, `consultar_historico.py` and `consultar_panel.py` also read the next month's PDF.
- **Requires `pdftotext`** (poppler-utils package). It is not a pip package.

---

## 3. BCRA: Monthly Retail Payments Report (XLSX)

`https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Informes/series-informe-mensual-pagos-minoristas-YYYY-MM.xlsx` (~170 KB). One file holds the full series since 2017.

- **The latest file has no fixed date.** The script tries the last 6 months in parallel and keeps the most recent valid XLSX (starts with `PK`). HEAD requests do not work: the server answers 200 even when the file does not exist.
- **Structure:** 9 sheets. Each has 1 to 3 header rows (with merged cells), a `Fecha` row and quantity / amount column pairs. "TC Modalidad de pago" has the quantity/amount row below `Fecha`. "Tarjeta de credito por canal" puts the amount in a column with a different title ("POS+QR Monto"). "Cuentas de pago y fondos invert" has two tables side by side, each with its own `Fecha` column. The script handles all three.
- **Different lag per sheet:** for example, transfers through August and cards through July in the same edition.
- **No dependencies:** the script reads the XLSX with the standard library's `zipfile` and `xml`. It was checked cell by cell against openpyxl (11,258 cells, 0 differences).

Page to cite: `https://www.bcra.gob.ar/informe-de-pagos-minoristas/`

---

## 4. INDEC: National CPI (CSV)

`https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv` (~1.2 MB, `;` separator, decimal comma, Latin-1 encoding).

- **Fixed URL, always up to date.** No need to guess the file name.
- **Columns:** `Codigo; Descripcion; Clasificador; Periodo (YYYYMM); Indice_IPC; v_m_IPC; v_i_a_IPC; Region`. Includes headline, 12 divisions, core, regulated, seasonal, goods and services, for 7 regions.
- **Cumulative figures:** computed from the index (final index / index of the month before the start − 1), which reproduces the official figure. Chaining rounded monthly changes is off by a tenth (2024: 117.7% chained versus 117.8% official).

**The XLS pitfall (why the skill moved to CSV):** the XLS `sh_ipc_MM_YY.xls` is named by publication month, and a future month returns a ~36 KB placeholder page. In October 2026, `sh_ipc_10_26.xls` was still that page even though the CSV already had September's figure. The "try from the current month backwards" rule was a month behind.

File with more detail (by region and product): `serie_ipc_aperturas.csv`, in the same folder.

Page to cite: `https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31`

---

## 5. Network access

The scripts need outbound access to `www.bcra.gob.ar` and `www.indec.gob.ar`. Many code-execution environments only allow listed domains. If a script answers `sin_acceso_red: true`:

1. Ask the user to add those domains to the allowed-domain list (or enable full network access) in their code-execution settings, and to ask again.
2. Alternatively, the user can download the file (PDF, XLSX or CSV) and upload it. `consultar_pagos.py` accepts `--archivo`.
3. Never answer from memory in the meantime.

---

## 6. Control values

To confirm parsing still works. These are closed publications: they do not change.

**April 2026 PDF (`202604e.pdf`), Banco Galicia (code 7), April 2026:**
`irr_tot` = 8.09 · `irr_cons` = 16.17 · `irr_com` = 3.32 · `roa` = 0.04 · `apalancamiento` = 4.3 · `tasa_prest` = 32.4 · `bA` = 36,704,435.9 · `bCA` = 12,339,200.7

```bash
python3 scripts/consultar_historico.py Galicia --campo irr_tot bA --desde 2026-04 --hasta 2026-04
```

**INDEC, national headline:** November 2025 monthly = 2.5 · May 2026 monthly = 2.1 · cumulative 2024 = 117.8 · cumulative 2025 = 31.5.

```bash
python3 scripts/consultar_ipc.py --acumulado 2024
```

**API versus PDF:** in July 2026, all 34,255 values shared by the API and the PDF were compared for the 73 entities. All matched except 4: amounts below 0.05 million that the PDF shows as "---" and the API as a minimal value.

`python3 tools/verificar.py`, at the repository root, runs these checks.

---

## 7. If a source changes

The BCRA and INDEC change formats and URLs without notice (the BCRA site changed its design and URLs: the page cited by the previous version of this skill now returns 404). If a script fails:

1. Read the error: it says which URL failed and why.
2. Open the source's citation page and look for the new link or format.
3. If the URL changed, update the constant at the top of the script (`API`, `PDF_ENTIDADES` in `bcra_comun.py`; `URL` in `consultar_pagos.py` and `consultar_ipc.py`).
4. If the format changed, inspect the downloaded file and adapt the parsing. Check against the control values before answering.
5. If it cannot be solved, tell the user the source changed and the figure cannot be obtained right now. Do not answer with an unverified value.
