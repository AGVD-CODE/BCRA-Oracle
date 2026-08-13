# Diccionario de datos

Qué es cada indicador, en qué fuente vive, su unidad y cómo se calcula (si es calculado). Usar para mapear la pregunta del usuario al dato correcto.

## Cómo leer este diccionario

- **Dato directo:** viene tal cual del reporte oficial. Se extrae y se responde.
- **Dato calculado:** se deriva de uno o más datos directos. Al responderlo, aclarar la fórmula.

---

## Balance (fuente: BCRA Entidades, PDF · mensual)

Todos en **millones de pesos corrientes**. Dato directo.

| Campo | Qué es |
|---|---|
| `bA` | Activo total |
| `bEf` | Efectivo y disponibilidades |
| `bTi` | Títulos |
| `bPr` | Préstamos (financiaciones totales) |
| `bP` | Pasivo total |
| `bDe` | Depósitos totales |
| `bCC` | Depósitos en cuenta corriente |
| `bCA` | Depósitos en caja de ahorro |
| `bPF` | Depósitos a plazo fijo |
| `bPN` | Patrimonio neto |

**Conversión para mostrar:** los valores están en millones. Para pasarlos a pesos, multiplicar por 1.000.000.

---

## Indicadores (fuente: BCRA Entidades, PDF · mensual)

Dato directo, ya vienen calculados por el BCRA. En porcentaje salvo aclaración.

| Campo | Qué es |
|---|---|
| `roe` | Retorno sobre patrimonio neto |
| `roa` | Retorno sobre activo |
| `apalancamiento` | Activo / patrimonio (veces) |
| `tasa_prest` | Tasa de interés promedio de préstamos |
| `tasa_dep` | Tasa de interés promedio de depósitos |
| `margen_fin_activo` | Margen financiero sobre activo |
| `absorc_gastos` | Absorción de gastos administrativos |
| `liq_tit_cot` | Liquidez en títulos cotizables |
| `dep_empleado` | Depósitos por empleado |

---

## Mora y calidad de cartera (fuente: BCRA Entidades, PDF · mensual)

Los indicadores de mora (`irr_*`) son **mensuales**. La distribución por situación (`cart`) es **trimestral**. Aclarar esta diferencia de período al responder.

### Indicadores de mora (mensual)
| Campo | Qué es |
|---|---|
| `irr_tot` | **Mora total**: cartera irregular / financiaciones totales (%). La "mora" a secas. |
| `irr_priv` | Mora del sector privado |
| `irr_com` | Mora de la cartera comercial (empresas) |
| `irr_cons` | Mora de la cartera de consumo (personas) |
| `prev_irr` | Previsiones / cartera irregular (%) = cobertura. >100% = reservas de sobra. |
| `exc_prev` | Exceso o defecto de previsiones |

**Qué es la cartera irregular:** las financiaciones en situación 3, 4 y 5 (atraso mayor a 90 días) sobre el total.

### Distribución por situación (trimestral)
El BCRA clasifica cada préstamo en 5 situaciones según días de atraso:

| Situación | Nombre | Atraso |
|---|---|---|
| 1 | Normal | al día o <31 días |
| 2 | Riesgo bajo / seguimiento especial | 31-90 días |
| 3 | Con problemas / riesgo medio | 90-180 días |
| 4 | Alto riesgo de insolvencia | 180 días-1 año |
| 5 | Irrecuperable | +1 año |

Campos: `tf_s1`..`tf_s5` (total financiaciones por situación, %), y desagregado en comercial (`com_s1`..`com_s5`) y consumo (`con_s1`..`con_s5`). `tf_total` = total. `prev` = previsiones constituidas.

**Cartera irregular = s3 + s4 + s5.** Cartera sana = s1 + s2.

---

## Tarjetas y cuentas (fuente: BCRA Información Adicional · trimestral)

Dato directo. Cantidades absolutas (unidades).

| Campo | Qué es |
|---|---|
| `pla` | Plásticos de crédito emitidos (tarjetas de crédito) |
| `tit` | Titulares de tarjetas de crédito |
| `deb` | Tarjetas de débito |
| `cah` | Cajas de ahorro |
| `emp` | Empleados de la entidad |
| `remu` | Cuentas sueldo / de la seguridad social |

### Datos calculados sobre tarjetas/cuentas
| Cálculo | Fórmula |
|---|---|
| Peso de mercado (tarjetas) | tarjetas del banco / total del sistema × 100 |
| Adicionales por titular | plásticos de crédito / titulares |
| Tarjetas por caja | tarjetas de débito / cajas de ahorro |
| Depósito promedio por caja | saldo en cajas de ahorro (bCA × 1M) / cantidad de cajas |

---

## Distribución geográfica e institucional (fuente: BCRA Información Adicional)

Dato directo.

| Dato | Qué es |
|---|---|
| Sucursales | cantidad de filiales, con desglose por provincia |
| Cajeros (ATM) | cantidad de cajeros automáticos |
| Presidente / gerente general | autoridades de la entidad |
| Empleados | dotación de personal |

---

## Medios de pago (fuente: BCRA Pagos Minoristas, XLSX · mensual)

Dato directo. Por cada medio: cantidad de operaciones y monto.

| Medio | Qué incluye |
|---|---|
| Transferencias (push/pull) | transferencias inmediatas iniciadas por el pagador o el cobrador |
| PCT | pagos con transferencia (QR, etc.) |
| Tarjetas de crédito / débito | compras |
| Débito directo | débitos automáticos |
| Cheques / ECHEQ | cheques físicos y electrónicos |
| Cajeros | extracciones |

### Dato calculado sobre pagos
| Cálculo | Fórmula |
|---|---|
| Ticket promedio | monto total / cantidad de operaciones |

---

## Inflación (fuente: INDEC IPC Nacional, XLS · mensual)

Dato directo. En porcentaje.

| Serie | Qué es |
|---|---|
| Nivel general | inflación del mes (variación mensual del IPC) |
| Interanual / últimos 12 meses | variación contra el mismo mes del año anterior |
| Núcleo | precios de mercado (sin regulados ni estacionales) — inflación de fondo |
| Regulados | precios fijados/autorizados por el Estado (tarifas, transporte, combustibles) |
| Estacional | precios que varían por época (frutas/verduras, turismo, indumentaria) |
| Bienes / Servicios | apertura por tipo |
| Divisiones (12) | rubros de la canasta: Alimentos, Vivienda, Salud, Transporte, etc. |

### Datos calculados sobre inflación
| Cálculo | Fórmula |
|---|---|
| Acumulada del año | producto de (1 + mensual/100) de los meses del año, menos 1 |
| Acumulada entre dos fechas | producto encadenado de las variaciones mensuales del tramo |

---

## Indicadores agregados del sistema (calculados)

Para responder "el sistema" en su conjunto, se agregan todos los bancos. **Siempre ponderar, nunca promediar simple.**

| Indicador del sistema | Cómo se calcula |
|---|---|
| Mora del sistema | suma(irr_tot × préstamos del banco) / suma(préstamos) |
| Mora de consumo/comercial del sistema | ídem con irr_cons / irr_com |
| ROE del sistema | ponderado por patrimonio o activo |
| Peso de un banco | activo del banco / activo total del sistema |
| Cobertura del sistema | ponderar prev_irr por la cartera irregular (préstamos × irr_tot/100), no por préstamos totales — si no, los bancos sin mora distorsionan |

---

## Identificación de entidades

Los nombres varían entre reportes. Buscar de forma flexible: ignorar mayúsculas, acentos, y sufijos como "S.A.", "S.A.U.". Casos frecuentes y sus códigos:

| El usuario dice | Nombre en el reporte | Código |
|---|---|---|
| Galicia | BANCO DE GALICIA Y BUENOS AIRES S.A.U. | 7 |
| Nación | BANCO DE LA NACION ARGENTINA | 11 |
| Provincia / Bapro | BANCO DE LA PROVINCIA DE BUENOS AIRES | — |
| Santander | BANCO SANTANDER ARGENTINA S.A. | — |
| Macro | BANCO MACRO S.A. | — |
| BBVA | BANCO BBVA ARGENTINA S.A. | — |
| Ualá | UALA BANK S.A.U. | — |
| Brubank | BRUBANK S.A.U. | — |

**Variantes que requieren mapeo explícito:**
- `BANCO DE SERVICIOS FINANCIEROS CARREFOUR SAU` → código 332 (a veces aparece como "Servicios Financieros" a secas).
- `BANK OF CHINA LIMITED SUCURSAL BUENOS AIRES` → código 131.

**Páginas que NO son bancos** en el PDF (ignorar): las de Compañías Financieras. En el reporte que analizamos estaban en las páginas 307 y 311, pero puede variar — identificarlas por el encabezado "Compañías Financieras" y no confundirlas con bancos.

Si el nombre es ambiguo (varios candidatos) o no existe, preguntar al usuario o listar los candidatos más parecidos. Nunca asumir.

---

## Checksums de validación (Banco Galicia, código 7)

Para confirmar que la extracción funciona, verificar estos valores conocidos de Galicia (a los períodos indicados). Si no coinciden, el parseo cambió y hay que revisarlo antes de responder.

- Sistema: 59 bancos, activo total ≈ 313,8 billones de pesos (abril 2026).
- Galicia abril 2026: roa=0,04 · apalancamiento=4,3 · tasa_prest=32,4 · irr_tot=8,09 · irr_cons=16,17 · irr_com=3,32
- Galicia balance: bA=36.704.435,9M · bCA=12.339.200,7M
- Galicia marzo 2026 (trimestral): pla=4.383.666 · tit=3.094.662 · deb=7.533.250 · cah=10.316.472 · emp=6.025
- Galicia cartera (situaciones): s1=89,16 · s3=2,62 · s4=4,62 · s5=0,85
- Galicia institucional: sucursales=321 · ATMs=976 · presidente=BOURDIEU GASTON · gerente=RIVAS DIEGO
