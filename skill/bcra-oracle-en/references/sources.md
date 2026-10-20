# Official sources and download patterns

This document contains the exact URLs and **all known pitfalls** for downloading the latest version of each source. Read before every download. Official sources change formats and file names without notice; if something fails, adapt by reading the downloaded file and adjusting the parsing.

## Index
1. BCRA — Financial Entities (PDF): balance sheet, ratios, NPL, portfolio quality
2. BCRA — Additional Information: cards, accounts, branches, ATMs, employees
3. BCRA — Monthly Retail Payments Report (XLSX): payment instruments
4. INDEC — National CPI (XLS): inflation
5. How to determine the latest available period

---

## 1. BCRA — Financial Entities (PDF)

Contains, per bank: full balance sheet, ratios (ROE, ROA, leverage, rates, liquidity), and portfolio quality (NPL, irregular portfolio, situations 1–5, provisions).

**Frequency:** monthly.

**URL (pattern):**
```
https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/YYYYMMe.pdf
```
Where `YYYYMM` is the year and month of the data. E.g.: April 2026 → `202604e.pdf`.

**How to download (the PDF weighs ~6 MB — Drive tools fail):**
```bash
wget -q "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202604e.pdf" -O /tmp/entidades.pdf
pdftotext -layout /tmp/entidades.pdf /tmp/entidades.txt
```
`pdftotext -layout` is critical: it preserves the column layout of the PDF; without it parsing fails.

**Validate the download:** a valid PDF weighs several MB. If it is very small or `wget` returns a 404 error, that month has not been published yet → try the previous month.

**Reference page (for citing the source):**
`https://www.bcra.gob.ar/PublicacionesEstadisticas/Entidades_financieras.asp`

---

## 2. BCRA — Additional Information

Credit and debit cards, cardholders, payroll accounts, savings accounts, geographic distribution of branches and ATMs, employees.

**Frequency:** quarterly (March, June, September, December).

This information is in the same BCRA publication circuit as the Financial Entities report. Cards and account data are typically found in "Additional Information" tables within the extracted text. The extractor `consultar_adicional.py` knows how to locate these tables.

**Note on periods:** because it is quarterly, the latest available data may be from an earlier month than the latest monthly balance/NPL data. E.g.: if the balance sheet goes up to April, cards may only go up to March. Clarify this when responding.

---

## 3. BCRA — Monthly Retail Payments Report (XLSX)

Volume and amount of transfers, direct debits, checks, ECHEQ, cards, payment-by-transfer (PCT/QR), etc. Long historical series.

**Frequency:** monthly.

**URL (pattern):**
```
https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Informes/series-informe-mensual-pagos-minoristas-YYYY-MM.xlsx
```
E.g.: June 2026 → `series-informe-mensual-pagos-minoristas-2026-06.xlsx`.

**How to download (~170 KB, works directly):**
```bash
wget -q "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Informes/series-informe-mensual-pagos-minoristas-2026-06.xlsx" -O /tmp/pagos.xlsx
```

**Advantage:** a single file carries the full historical series (18+ months), so downloading the most recent one gives everything.

**Slug pitfall:** the *page* URL (not the file URL) for the report alternates between two patterns:
```
https://www.bcra.gob.ar/publicaciones/informe-de-pagos-minoristas-MES-de-AAAA/
https://www.bcra.gob.ar/publicaciones/informe-mensual-de-pagos-minoristas-MES-de-AAAA/
```
If the page is needed (rarely), try both. For the data, the XLSX URL above is sufficient.

**Reference page (for citing):**
`https://www.bcra.gob.ar/PublicacionesEstadisticas/Informe-mensual-pagos-minoristas.asp`

---

## 4. INDEC — National CPI (XLS)

Inflation: headline, core, regulated, seasonal, goods, services, 12 basket divisions, monthly and year-on-year variation.

**Frequency:** monthly.

**URL (pattern):**
```
https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_MM_YY.xls
```

**CRITICAL PITFALL — the filename uses the PUBLICATION month, not the data month:**
The CPI for a given month is published in the middle of the following month. So `MM_YY` is the month the file was published, and the file contains data *up to the previous month*.

- The **June 2026** CPI is published in **July 2026** → file `sh_ipc_07_26.xls` (contains data through June).
- To get the most recent data, **try from the current month backwards:**
  ```bash
  # Try sh_ipc_08_26 (August), then 07_26, etc.
  wget -q "https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_07_26.xls" -O /tmp/ipc.xls
  ```
- **How to tell if the file is valid:** a real data file weighs **~2.3 MB**. Months not yet published return a **~36 KB placeholder**. Check the size:
  ```bash
  ls -la /tmp/ipc.xls  # if ~36 KB, it's a placeholder → try the previous month
  ```

**Dependency:** requires `xlrd` to read the legacy .xls format:
```bash
pip install xlrd --break-system-packages
```

**Sheets in the file:**
- `"Variación mensual IPC Nacional"` — month-on-month variation.
- `"Var. interanual IPC Nacional"` — year-on-year variation (last 12 months).
- Row 5 = dates (Excel serial format). Series identified by label in column 0.

**Validation reference (to confirm parsing works):**
- Nov-25 monthly = 2.5%
- May-26 monthly = 2.1%
- Full 2024 (cumulative) = 117.7% (official: 117.8%)
- Full 2025 = 31.5%

**Reference page (for citing):**
`https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31`

---

## 5. How to determine the latest available period

For any source, the strategy is the same: **try the most recent period and work backwards until a valid download is found.**

1. Start from the current month (or the expected publication month, in the INDEC case).
2. Attempt the download.
3. Validate: does the file have the expected size? Did `wget` avoid a 404? Does the content parse?
4. If not valid, go back one month and retry.
5. Once valid, that is the latest available period. Use it and **state the period in the response.**

Never assume the period: always verify which one is actually the latest published at query time.

---

## Note on network restrictions

If the environment blocks direct access to `bcra.gob.ar` or `indec.gob.ar` (some cloud environments return 503), inform the user that they may need to enable access to those domains in the network configuration, or download the file manually and upload it. The BCRA and INDEC sites generally work with direct access.
