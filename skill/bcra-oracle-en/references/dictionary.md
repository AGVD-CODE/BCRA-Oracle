# Data dictionary

What each field returned by the scripts means, which section it belongs to, its unit and its frequency. Field keys are the same in every script (`consultar_entidad.py`, `consultar_ranking.py`, `consultar_historico.py`). The scripts' own descriptions are in Spanish: `python3 scripts/consultar_entidad.py --campos`.

## How to read the data

- **Direct figure:** taken as published.
- **Calculated figure:** derived from direct figures by the script or by the answer. Calculated fields say "(CALCULADO)" in their description. When answering, explain the formula.
- **`null`:** the source does not publish the figure (empty cell or "---"). It is never zero. The BCRA shows 0 as an empty cell and uses 99999 as a "not applicable" marker: the scripts turn both into `null`.
- **Period "YYYY-MM":** the month the figure refers to (not the publication month).

## Frequency and lag

| Section | Frequency | Periods returned by the API | Usual lag |
|---|---|---|---|
| `indicadores`, `balance`, `cartera` | monthly | last 2 Decembers + last 3 months | about 3 months |
| `remuneraciones` (payroll accounts) | monthly | last 2 Decembers + last 3 months | about 3 months |
| `sucursales` | snapshot at the update month | latest only | about 3 months |
| `adicional` (cards, accounts, employees) | quarterly | last 3 Decembers + last 2 quarters | about 4 months |

For more history than the API returns, `consultar_historico.py` reads the monthly PDFs (each holds 3 consecutive months plus 2 Decembers).

---

## Ratios (`indicadores`, BCRA · monthly)

Published already calculated by the BCRA. The official ratio code is in parentheses. The PDF also gives, for each ratio, the value for the entity's institutional group, the top 10 private banks and the whole system (`consultar_historico.py` returns them under `referencias` when present).

| Field | What it is | Unit |
|---|---|---|
| `apalancamiento` | Leverage: assets / equity (C1) | times |
| `perdida_s2a5` | Potential loss on portfolio in categories 2 to 5 (C2) | % |
| `perdida_s3a5` | Potential loss on portfolio in categories 3 to 5 (C3) | % |
| `irr_tot` | Total NPL: irregular portfolio / total financing (A9) | % |
| `irr_priv` | Private-sector irregular portfolio (A11) | % |
| `part_com` | Share of commercial portfolio in private sector (A12) | % |
| `part_cons` | Share of consumer portfolio in private sector (A13) | % |
| `prev_irr` | Coverage: provisions / total irregular portfolio (A14) | % |
| `irr_cons` | Consumer NPL: private-sector consumer irregular portfolio (A16) | % |
| `irr_com` | Commercial NPL: private-sector commercial irregular portfolio (A17) | % |
| `exc_prev` | Minimum-provision position, private non-financial sector (A21) | % |
| `part_venc` | Weight of past-due private-sector portfolio (AG3) | % |
| `efectivo_activo` | Cash and bank deposits / assets (AG29) | % |
| `absorc_gastos` | Administrative expenses absorbed by business volume (E1) | % |
| `margen_rent_gastos` | Operating profitability margin / structural expenses (E2) | % |
| `roe` | ROE: annual return on equity (R1) | % |
| `roe_ord` | Ordinary return on equity (R2) | % |
| `tasa_prest` | Implicit rate on total loans (R8) | % |
| `tasa_dep` | Implicit rate on total deposits (R9) | % |
| `gpers_gadm` | Personnel expenses / administrative expenses (R17) | % |
| `roa` | ROA: return on assets (RG1) | % |
| `margen_fin_activo` | Financial margin over assets (RG2_II) | % |
| `roa_inco` | Loan-loss charges / assets (RG3) | % |
| `result_serv_activo` | Service results / assets (RG4_II) | % |
| `roa_adm` | Administrative expenses / assets (RG5) | % |
| `roa_aig` | ROA before income tax (RG15) | % |
| `liq_amplia` | Liquidity: listed securities, call, LELIQ and LEFI, net (L1) | % |
| `liq_tit_cot` | Liquidity with listed securities (L8_II) | % |
| `liq_bcra` | Liquidity: LELIQ, repos and LEFI net of BCRA reverse repos (L9) | % |
| `dep_empleado` | Deposits per employee (E4) | millions of pesos |
| `fin_empleado` | Financing per employee (E5) | millions of pesos |

**"NPL" (mora) on its own = `irr_tot`.** The irregular portfolio is financing in categories 3, 4 and 5 (more than 90 days past due).

---

## Balance sheet and results (`balance`, BCRA · monthly)

Millions of current pesos (the API publishes thousands and the script divides by 1,000; the PDF is already in millions). Results (`bRes`, `bIF`, `bGA`, etc.) are **accumulated since the start of the fiscal year**, not for the month. For the full balance sheet with original line names: `consultar_entidad.py X --seccion balance --filas`.

| Field | What it is | Unit |
|---|---|---|
| `bA` | Total assets | millions of pesos |
| `bEf` | Cash and deposits in banks | millions of pesos |
| `bTi` | Public and private securities | millions of pesos |
| `bPr` | Loans (net of provisions) | millions of pesos |
| `bPr_priv` | Loans to the private non-financial sector and non-residents | millions of pesos |
| `bAdel` | Loans: overdrafts | millions of pesos |
| `bDoc` | Loans: promissory notes and discounted documents | millions of pesos |
| `bHip` | Loans: mortgages | millions of pesos |
| `bPrend` | Loans: secured (pledge) loans | millions of pesos |
| `bPers` | Loans: personal loans | millions of pesos |
| `bPrev` | Loan-loss provisions (negative) | millions of pesos |
| `bP` | Total liabilities | millions of pesos |
| `bDe` | Total deposits | millions of pesos |
| `bDe_priv` | Deposits from the private non-financial sector and non-residents | millions of pesos |
| `bCC` | Private checking-account deposits | millions of pesos |
| `bCA` | Private savings-account deposits | millions of pesos |
| `bPF` | Private time deposits and term investments | millions of pesos |
| `bPN` | Equity | millions of pesos |
| `bRes` | Comprehensive result accumulated in the fiscal year to date | millions of pesos |
| `bIF` | Financial income, year to date | millions of pesos |
| `bEgF` | Financial expenses, year to date (negative) | millions of pesos |
| `bInc` | Loan-loss charge, year to date (negative) | millions of pesos |
| `bIS` | Service income, year to date | millions of pesos |
| `bES` | Service expenses, year to date (negative) | millions of pesos |
| `bGA` | Administrative expenses, year to date (negative) | millions of pesos |
| `bRM` | Monetary result (inflation adjustment), year to date | millions of pesos |
| `bIG` | Income tax, year to date | millions of pesos |

---

## Debtor classification (`cartera`, BCRA · monthly)

Amounts in millions of pesos. Percentages over the total of each portfolio.

| Field | What it is | Unit |
|---|---|---|
| `tf_total` | Total financing and guarantees granted | millions of pesos |
| `prev` | Loan-loss provisions set aside | millions of pesos |
| `com_total` | Commercial portfolio | millions of pesos |
| `con_total` | Consumer or housing portfolio | millions of pesos |
| `cac_total` | Commercial portfolio treated as consumer | millions of pesos |
| `tf_s1` | Financing in category 1: normal | % |
| `tf_s2` | Financing in category 2: special monitoring / low risk | % |
| `tf_s3` | Financing in category 3: troubled / medium risk | % |
| `tf_s4` | Financing in category 4: high insolvency risk | % |
| `tf_s5` | Financing in category 5: unrecoverable | % |
| `tf_irregular` | Irregular portfolio = categories 3+4+5 (CALCULATED) | % |
| `tf_garant` | Financing with preferred guarantees A and B | % |
| `com_part` | Commercial portfolio / total financing | % |
| `con_part` | Consumer portfolio / total financing | % |
| `cac_part` | Commercial-treated-as-consumer portfolio / total financing | % |
| `com_garant` | Commercial portfolio with preferred guarantees A and B | % |
| `con_garant` | Consumer portfolio with preferred guarantees A and B | % |
| `cac_garant` | Commercial-as-consumer portfolio with preferred guarantees A and B | % |
| `com_s1`…`com_s5` | Commercial portfolio in category 1 to 5 | % |
| `con_s1`…`con_s5` | Consumer or housing portfolio in category 1 to 5 | % |
| `cac_s1`…`cac_s5` | Commercial-treated-as-consumer portfolio in category 1 to 5 | % |

| Category | Name | Days past due |
|---|---|---|
| 1 | Normal | up to 31 days |
| 2 | Special monitoring / low risk | 31 to 90 days |
| 3 | Troubled / medium risk | 90 to 180 days |
| 4 | High insolvency risk | 180 days to 1 year |
| 5 | Unrecoverable | over 1 year |

Days past due are the reference for the consumer or housing portfolio. The commercial portfolio is classified mainly by the debtor's repayment capacity.

`tf_irregular` (c3 + c4 + c5) is calculated from the debtor-classification table. It may differ slightly from `irr_tot`, which the BCRA computes on a different base. For "NPL", use `irr_tot`.

---

## Additional information (`adicional`, BCRA · quarterly)

Counts (units).

| Field | What it is | Unit |
|---|---|---|
| `cc` | Checking accounts | count |
| `cah` | Savings accounts | count |
| `cah_social` | Social-assistance savings accounts | count |
| `cprev` | Pension accounts | count |
| `pf_ind` | Time-deposit operations, individuals | count |
| `pf_emp` | Time-deposit operations, companies | count |
| `op_hip` | Mortgage loan operations | count |
| `op_prend` | Secured (pledge) loan operations | count |
| `op_otros` | Other loan operations | count |
| `emp` | Staff (employees) | count |
| `tit` | Credit-card holders | count |
| `pla` | Credit cards (plastics) | count |
| `deb` | Debit cards | count |

## Payroll accounts (`remuneraciones`, BCRA · monthly)

| Field | What it is | Unit |
|---|---|---|
| `remu` | Payroll accounts: accounts receiving salary deposits | count |
| `remu_emp` | Companies paying salaries by bank deposit | count |

## Branches and ATMs (`sucursales`, BCRA · snapshot at the update month)

| Field | What it is | Unit |
|---|---|---|
| `sucursales` | Total branches = full + specific-purpose + mobile (CALCULATED) | count |
| `suc_plenas` | Full-service branches | count |
| `suc_especificas` | Specific-purpose branches | count |
| `suc_moviles` | Mobile branches | count |
| `dep_automatizadas` | Automated service points | count |
| `cajeros` | ATMs | count |
| `terminales` | Self-service terminals | count |
| `puestos_promocion` | Promotion desks | count |
| `agencias` | Complementary financial-service agencies | count |
| `suc_exterior` | Branches abroad | count |
| `of_representacion` | Representative offices abroad | count |

`--provincias` adds the breakdown by province with the same keys.

---

## Common calculations (always state them when answering)

| Calculation | Formula | How to get it |
|---|---|---|
| Market share | entity value / system total × 100 | `consultar_ranking.py FIELD --participacion` |
| Plastics per cardholder | `pla` / `tit` | `consultar_entidad.py X --campo pla tit` |
| Debit cards per savings account | `deb` / `cah` | same |
| Average savings-account balance | `bCA` × 1,000,000 / `cah` | note that `bCA` is monthly and `cah` quarterly: use the same month |
| Change between periods | (final / initial − 1) × 100; for % ratios, difference in points | `--serie` or `consultar_historico.py` |
| Real (inflation-adjusted) change | (1 + nominal change) / (1 + inflation over the period) − 1 | combine with `consultar_ipc.py --acumulado --desde ... --hasta ...` |
| Average ticket | amount / number of transactions | `consultar_pagos.py` calculates it |
| Cumulative inflation | final index / index of the month before the start − 1 | `consultar_ipc.py --acumulado` |

**System totals:** do not add up or average entities by hand. Use the `sistema` group (or `publicos`, `privados`, `companias`, `top10`), which the BCRA publishes already aggregated and weighted. If an aggregate the BCRA does not publish is needed (for example, "banks only" for a % ratio), weight it by the relevant base (NPL by loans, ROE by equity) and say it is your own calculation.

---

## Inflation (INDEC · national CPI · monthly)

In %. `consultar_ipc.py` returns the monthly change, the year-on-year change and the year-to-date cumulative change. Output labels are in Spanish (`mensual` monthly, `interanual` year-on-year, `acumulada` cumulative).

| Series (`--serie`) | What it is |
|---|---|
| `nivel` | Headline: "inflation" |
| `nucleo` | Core: excludes regulated and seasonal items |
| `regulados` | Regulated prices or prices with a high tax component (utilities, fuel, transport) |
| `estacional` | Seasonal items (fruit, vegetables, clothing, tourism) |
| `bienes`, `servicios` | Goods and services |
| `01`…`12` or Spanish name | Divisions: alimentos (food), bebidas alcohólicas, prendas (clothing), vivienda (housing and utilities), equipamiento, salud (health), transporte, comunicación, recreación, educación, restaurantes, bienes y servicios varios |

Regions (`--region`): Nacional (default), GBA, Pampeana, Noreste, Noroeste, Cuyo, Patagonia.

## Payment instruments (BCRA · Retail Payments · monthly)

Number of transactions and nominal amount in pesos (or in the currency the series states). `consultar_pagos.py --series` lists every series in the latest file. Search with Spanish names. Main ones:

| Sheet | Series |
|---|---|
| Cheques | Cleared checks, paper checks, ECHEQ (pesos and dollars), bounced checks, bounced for insufficient funds |
| Transferencias de fondos | Instant push and pull transfers, transfer payments (interoperable QR), high-value, batch |
| Series push apertura | Push transfers by channel (ATM, corporate e-banking, home banking, mobile banking) |
| Tarjetas | Credit cards (`tarjetas de crédito`), debit cards (pesos and dollars), prepaid cards |
| TC Modalidad de pago | Credit-card purchases in one payment and in installments |
| Tarjeta de credito por canal | e-commerce, POS+QR, direct debit, other |
| Transporte | Prepaid transport cards, QR rides |
| Resto | Direct debits, instant debit (DEBIN), cash withdrawals, ATM deposits, cleared time deposits, MEP, MiPyME electronic credit invoice (FCEM), active POS |
| Cuentas de pago y fondos invert | Payment accounts with balance (wallets) and balances invested in funds |

Each sheet has its own lag: the latest month can differ by series.

---

## Entity identification

The scripts match names ignoring case and accents, ignore "Banco", "S.A.", "S.A.U." and accept the BCRA code. Frequent aliases:

| The user says | Entity | Code |
|---|---|---|
| Galicia | Banco de Galicia y Buenos Aires S.A. | 7 |
| Nación, BNA | Banco de la Nación Argentina | 11 |
| Provincia, Bapro | Banco de la Provincia de Buenos Aires | 14 |
| ICBC | Industrial and Commercial Bank of China (Argentina) | 15 |
| Citi | Citibank N.A. | 16 |
| BBVA, Francés | Banco BBVA Argentina S.A. | 17 |
| Bancor, Córdoba | Banco de la Provincia de Córdoba S.A. | 20 |
| Supervielle | Banco Supervielle S.A. | 27 |
| Ciudad | Banco de la Ciudad de Buenos Aires | 29 |
| Patagonia | Banco Patagonia S.A. | 34 |
| Hipotecario | Banco Hipotecario S.A. | 44 |
| Santander | Banco Santander Argentina S.A. | 72 |
| Credicoop | Banco Credicoop Cooperativo Limitado | 191 |
| Macro | Banco Macro S.A. | 285 |
| Comafi | Banco Comafi S.A. | 299 |
| BICE | Banco de Inversión y Comercio Exterior | 300 |
| BIND, Industrial | Banco Industrial S.A. | 322 |
| Santa Fe | Nuevo Banco de Santa Fe S.A. | 330 |
| Carrefour, Servicios Financieros | Banco de Servicios Financieros (Carrefour) | 332 |
| Ualá | Ualá Bank S.A.U. | 384 |
| Brubank | Brubank S.A.U. | 143 |
| Naranja X | Naranja Digital Compañía Financiera S.A. | 45030 |
| Reba | Reba Compañía Financiera S.A. | 45072 |

Groups: `sistema` (whole financial system: banks and finance companies), `publicos`, `privados`, `companias` (finance companies), `top10` (top 10 private banks).

If the name matches several entities, the script returns `candidatos`: ask the user. If it matches none, the entity is not a bank or finance company on the BCRA list (digital wallets and other payment providers are not): say so.
