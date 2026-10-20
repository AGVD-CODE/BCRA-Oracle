# Data dictionary

What each indicator is, which source it comes from, its unit, and how it is calculated (when applicable). Use this to map user questions to the correct data.

## How to read this dictionary

- **Direct data:** comes as-is from the official report. Extract and respond.
- **Calculated data:** derived from one or more direct data points. When responding, clarify the formula.

---

## Balance sheet (source: BCRA Financial Entities, PDF · monthly)

All values in **millions of current Argentine pesos**. Direct data.

| Field | What it is |
|---|---|
| `bA` | Total assets |
| `bEf` | Cash and liquid assets |
| `bTi` | Securities |
| `bPr` | Loans (total financings) |
| `bP` | Total liabilities |
| `bDe` | Total deposits |
| `bCC` | Checking account deposits |
| `bCA` | Savings account deposits |
| `bPF` | Time deposits (fixed-term) |
| `bPN` | Net equity (shareholders' equity) |

**Display conversion:** values are in millions. To convert to pesos, multiply by 1,000,000.

---

## Financial ratios (source: BCRA Financial Entities, PDF · monthly)

Direct data, already calculated by the BCRA. In percentage unless noted otherwise.

| Field | What it is |
|---|---|
| `roe` | Return on equity |
| `roa` | Return on assets |
| `apalancamiento` | Leverage: assets / equity (multiple) |
| `tasa_prest` | Average interest rate on loans |
| `tasa_dep` | Average interest rate on deposits |
| `margen_fin_activo` | Net interest margin over assets |
| `absorc_gastos` | Administrative expense absorption ratio |
| `liq_tit_cot` | Liquidity in listed securities |
| `dep_empleado` | Deposits per employee |

---

## NPL and portfolio quality (source: BCRA Financial Entities, PDF · monthly)

NPL indicators (`irr_*`) are **monthly**. Situation-by-situation breakdown (`cart`) is **quarterly**. Clarify this difference in period when responding.

### NPL indicators (monthly)
| Field | What it is |
|---|---|
| `irr_tot` | **Overall NPL rate**: irregular portfolio / total financings (%). The plain "NPL" or "bad loan ratio". |
| `irr_priv` | Private sector NPL |
| `irr_com` | Commercial portfolio NPL (corporate) |
| `irr_cons` | Consumer portfolio NPL (retail) |
| `prev_irr` | Provisions / irregular portfolio (%) = coverage ratio. >100% means excess reserves. |
| `exc_prev` | Provision surplus or deficit |

**What irregular portfolio means:** financings in situation 3, 4, and 5 (overdue more than 90 days) as a share of total.

### Situation breakdown (quarterly)
The BCRA classifies each loan into 5 situations based on days past due:

| Situation | Name | Days past due |
|---|---|---|
| 1 | Normal | Current or <31 days |
| 2 | Low risk / special watch | 31–90 days |
| 3 | Substandard / medium risk | 90–180 days |
| 4 | High insolvency risk | 180 days – 1 year |
| 5 | Loss / irrecoverable | >1 year |

Fields: `tf_s1`..`tf_s5` (total financings per situation, %), and broken down into commercial (`com_s1`..`com_s5`) and consumer (`con_s1`..`con_s5`). `tf_total` = total. `prev` = provisions held.

**Irregular portfolio = s3 + s4 + s5.** Performing portfolio = s1 + s2.

---

## Cards and accounts (source: BCRA Additional Information · quarterly)

Direct data. Absolute counts (units).

| Field | What it is |
|---|---|
| `pla` | Credit card plastics issued |
| `tit` | Credit card holders |
| `deb` | Debit cards |
| `cah` | Savings accounts |
| `emp` | Bank employees |
| `remu` | Payroll / social security accounts |

### Calculated indicators for cards/accounts
| Calculation | Formula |
|---|---|
| Market share (cards) | bank cards / system total × 100 |
| Additional cards per holder | credit card plastics / card holders |
| Cards per savings account | debit cards / savings accounts |
| Average balance per savings account | savings account balance (bCA × 1M) / number of savings accounts |

---

## Geographic and institutional distribution (source: BCRA Additional Information)

Direct data.

| Data | What it is |
|---|---|
| Branches | number of branches, with breakdown by province |
| ATMs | number of automated teller machines |
| Chairman / CEO | executive officers of the entity |
| Employees | headcount |

---

## Payment instruments (source: BCRA Retail Payments, XLSX · monthly)

Direct data. For each instrument: number of transactions and total amount.

| Instrument | What it covers |
|---|---|
| Transfers (push/pull) | Immediate transfers initiated by payer or payee |
| PCT | Payment by transfer (QR, etc.) |
| Credit / debit cards | Purchases |
| Direct debit | Automatic debits |
| Checks / ECHEQ | Physical and electronic checks |
| ATMs | Cash withdrawals |

### Calculated indicator for payments
| Calculation | Formula |
|---|---|
| Average ticket | total amount / number of transactions |

---

## Inflation (source: INDEC National CPI, XLS · monthly)

Direct data. In percentage.

| Series | What it is |
|---|---|
| Headline | Monthly inflation (month-on-month CPI change) |
| Year-on-year / last 12 months | Change versus the same month of the prior year |
| Core | Market prices (excluding regulated and seasonal) — underlying inflation |
| Regulated | Prices set or authorized by the government (utilities, transport, fuel) |
| Seasonal | Prices that vary by season (fresh produce, tourism, clothing) |
| Goods / Services | Breakdown by type |
| Divisions (12) | Basket categories: Food, Housing, Health, Transport, etc. |

### Calculated inflation indicators
| Calculation | Formula |
|---|---|
| Year-to-date cumulative | product of (1 + monthly/100) for each month of the year, minus 1 |
| Cumulative between two dates | chained product of monthly changes over the interval |

---

## System-level aggregates (calculated)

To answer questions about "the system" as a whole, aggregate all banks. **Always use weighted averages, never simple averages.**

| System indicator | How it is calculated |
|---|---|
| System NPL rate | sum(irr_tot × bank loans) / sum(total loans) |
| Consumer/commercial system NPL | same, using irr_cons / irr_com |
| System ROE | weighted by equity or assets |
| Bank market weight | bank assets / total system assets |
| System coverage ratio | weight prev_irr by the irregular portfolio (loans × irr_tot/100), not by total loans — otherwise banks with no NPL distort the result |

---

## Entity identification

Names vary across reports. Search flexibly: ignore case, accents, and suffixes like "S.A.", "S.A.U.". Common cases and their codes:

| User says | Name in report | Code |
|---|---|---|
| Galicia | BANCO DE GALICIA Y BUENOS AIRES S.A.U. | 7 |
| Nación / Nacion | BANCO DE LA NACION ARGENTINA | 11 |
| Provincia / Bapro | BANCO DE LA PROVINCIA DE BUENOS AIRES | — |
| Santander | BANCO SANTANDER ARGENTINA S.A. | — |
| Macro | BANCO MACRO S.A. | — |
| BBVA | BANCO BBVA ARGENTINA S.A. | — |
| Ualá / Uala | UALA BANK S.A.U. | — |
| Brubank | BRUBANK S.A.U. | — |

**Variants requiring explicit mapping:**
- `BANCO DE SERVICIOS FINANCIEROS CARREFOUR SAU` → code 332 (sometimes appears as just "Servicios Financieros").
- `BANK OF CHINA LIMITED SUCURSAL BUENOS AIRES` → code 131.

**Pages that are NOT banks** in the PDF (ignore): those for Compañías Financieras (finance companies). In the analyzed report they appeared around pages 307 and 311, but this may vary — identify them by the "Compañías Financieras" header and do not confuse them with banks.

If the name is ambiguous (multiple candidates) or does not exist, ask the user or list the closest matches. Never assume.

---

## Validation checksums (Banco Galicia, code 7)

To confirm extraction is working correctly, verify these known values for Galicia (at the periods indicated). If they do not match, the parsing has changed and must be reviewed before responding.

- System: 59 banks, total assets ≈ 313.8 trillion pesos (April 2026).
- Galicia April 2026: roa=0.04 · leverage=4.3 · tasa_prest=32.4 · irr_tot=8.09 · irr_cons=16.17 · irr_com=3.32
- Galicia balance sheet: bA=36,704,435.9M · bCA=12,339,200.7M
- Galicia March 2026 (quarterly): pla=4,383,666 · tit=3,094,662 · deb=7,533,250 · cah=10,316,472 · emp=6,025
- Galicia portfolio situations: s1=89.16 · s3=2.62 · s4=4.62 · s5=0.85
- Galicia institutional: branches=321 · ATMs=976 · chairman=BOURDIEU GASTON · CEO=RIVAS DIEGO
