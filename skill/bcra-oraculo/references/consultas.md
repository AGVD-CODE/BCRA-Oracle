# Recetas de consulta

Cómo resolver cada tipo de pregunta con el menor número de comandos. Los ejemplos de respuesta usan datos reales a la fecha indicada. En cada consulta, usar siempre los números que devuelva el script.

## Flujo general

1. Identificar el indicador y la entidad, el grupo o la fuente (`SKILL.md` tiene la tabla de comandos; `diccionario.md`, todos los campos).
2. Correr **un** comando por fuente. Si hay varias fuentes, correrlas en paralelo.
3. Revisar el JSON: `candidatos` (preguntar), `sin_dato_publicado` (decirlo), `sin_acceso_red` (pedir acceso), `null` (no publicado).
4. Responder con dato, unidad, período y fuente. Si hubo un cálculo, explicarlo.

---

## Tipo 1: un banco, uno o varios datos

**Pregunta:** "¿Cuántas tarjetas de crédito tiene el Galicia, cuántas cajas de ahorro y cuál es su mora?"

```bash
python3 scripts/consultar_entidad.py Galicia --campo pla cah irr_tot
```

Los períodos pueden diferir: tarjetas y cajas son trimestrales, la mora es mensual.

> Banco Galicia, según el BCRA (Información de Entidades Financieras):
> - **Tarjetas de crédito:** 4.930.958 plásticos (junio de 2026).
> - **Cajas de ahorro:** 10.607.086 cuentas (junio de 2026).
> - **Mora:** 9,13 % de cartera irregular sobre financiaciones (julio de 2026).

---

## Tipo 2: ranking o comparación

**Pregunta:** "¿Qué banco tiene más mora?" o "¿Top 5 por sucursales?"

```bash
python3 scripts/consultar_ranking.py irr_tot --top 5
python3 scripts/consultar_ranking.py sucursales --top 5
```

Tarda 2 a 4 segundos (consulta las 60 entidades bancarias en paralelo). El JSON incluye `valor_sistema_financiero` como referencia y la lista de entidades sin dato.

> Los 5 bancos con mayor mora a julio de 2026, según el BCRA:
> 1. Banco de Servicios Financieros (Carrefour): 50,16 %
> 2. Banco Sáenz: 48,70 %
> 3. Banco Columbia: 27,80 %
> 4. Banco Sucrédito Regional: 23,45 %
> 5. Banco Rioja: 23,27 %
>
> La mora del sistema financiero es 7,18 %. *Son bancos chicos, con cartera mayormente de consumo.*

**Relevancia sistémica.** Si la pregunta apunta a los bancos que importan, usar `--entre-mayores 20` (ranking solo entre los 20 de mayor activo) u ofrecerlo como segunda lectura:

```bash
python3 scripts/consultar_ranking.py irr_tot --entre-mayores 10 --top 5
```

**Cuota de mercado:** `--participacion` agrega el porcentaje sobre el total del sistema (solo para montos y cantidades).

**Umbral:** "¿Cuántos bancos tienen mora mayor al 10 %?" → `consultar_ranking.py irr_tot --mayor-que 10`. El campo `filtro_valor.entidades_que_cumplen` da la cantidad.

**Menor a mayor:** `--asc` (por ejemplo, el ROE más bajo).

**Compañías financieras o todo el sistema:** `--grupo companias` o `--grupo todas`.

---

## Tipo 3: evolución en el tiempo

**Hasta 5 períodos** (2 últimos diciembres y 3 últimos meses): un solo comando, ~1 segundo.

```bash
python3 scripts/consultar_entidad.py Galicia --campo irr_tot --serie
```

**Seis meses o más:** PDF mensual, un archivo cada 3 meses. Tarda unos segundos más: avisar al usuario.

```bash
python3 scripts/consultar_historico.py Galicia --campo irr_tot --meses 12
```

> Mora del Banco Galicia (cartera irregular sobre financiaciones), según el BCRA:
> feb-26: 7,65 % · mar-26: 7,68 % · abr-26: 8,09 % · may-26: 8,94 % · jun-26: 8,30 % · jul-26: 9,13 %.
> Subió 1,48 puntos en el período.

La variación de montos es nominal. Para hablar de crecimiento real, ajustar con la inflación del mismo tramo (tipo 4).

---

## Tipo 4: cruza fuentes

**Pregunta:** "¿El ticket promedio con tarjeta de crédito le ganó a la inflación el último mes?"

Correr en paralelo:

```bash
python3 scripts/consultar_pagos.py --buscar "tarjetas de crédito" --hoja Tarjetas
python3 scripts/consultar_ipc.py --mes 2026-07
```

Usar **el mismo mes** en las dos fuentes: el último mes de pagos (`mes` en el JSON) suele estar atrasado respecto del IPC. Pedir el IPC de ese mes con `--mes`.

> En julio de 2026, el ticket promedio de las compras con tarjeta de crédito subió 4,43 % contra junio (de $60.274 a $62.945), y la inflación de julio fue 2,1 % (INDEC). El ticket creció más que los precios: unos 2,3 % en términos reales.
>
> *Ticket promedio = monto / cantidad de operaciones (BCRA, Pagos Minoristas). Variación real = 1,0443 / 1,021 − 1 (cálculo propio). Montos nominales.*

**Mora del sistema contra inflación:** la mora es un porcentaje (se compara en puntos) y la inflación es una variación de precios. No son comparables directamente. Explicarlo y ofrecer las dos series.

---

## Tipo 5: totales del sistema o de un grupo

**Pregunta:** "¿Cuál es la mora promedio del sistema?" o "¿Cuántas tarjetas de crédito hay en total?"

```bash
python3 scripts/consultar_entidad.py sistema --campo irr_tot pla
```

El BCRA publica el agregado ya ponderado. No promediar entidades a mano. Otros grupos: `publicos`, `privados`, `companias`, `top10`.

> La mora del sistema financiero es 7,18 % a julio de 2026 y hay 38.112.006 tarjetas de crédito emitidas a junio de 2026 (BCRA). *El sistema incluye bancos y compañías financieras.*

---

## Tipo 6: autoridades y datos institucionales

**Pregunta:** "¿Quién es el presidente del Banco Macro?"

```bash
python3 scripts/consultar_entidad.py Macro --seccion ficha
```

Viene del PDF mensual (necesita `pdftotext`). Devuelve directivos, accionistas, auditor externo, CUIT, casa matriz y web. Citar el mes del PDF: las autoridades cambian.

---

## Tipo 7: inflación

| Pregunta | Comando |
|---|---|
| "¿Cuál fue la inflación del último mes?" | `consultar_ipc.py` |
| "¿Y la de junio?" | `consultar_ipc.py --mes 2026-06` |
| "¿Cuánto acumula en el año?" | `consultar_ipc.py --acumulado 2026` |
| "¿Inflación de los últimos 12 meses?" | `consultar_ipc.py` (campo `interanual` del nivel general) |
| "¿Cuánto fue la núcleo?" | `consultar_ipc.py` (fila Núcleo) o `--serie nucleo --meses 6` |
| "¿Qué rubro subió más?" | `consultar_ipc.py --ranking-divisiones` |
| "¿Cuánto subió Vivienda en 12 meses?" | `consultar_ipc.py --serie vivienda --meses 12` (interanual del último mes) |
| "¿Inflación entre julio de 2025 y junio de 2026?" | `consultar_ipc.py --acumulado --desde 2025-07 --hasta 2026-06` |

Si piden un mes que el INDEC todavía no publicó, el script lo dice e informa el último disponible.

---

## Tipo 8: el dato no existe

Responder con honestidad y ofrecer lo más cercano, aclarando que no es exactamente lo pedido.

| Pregunta | Respuesta |
|---|---|
| Clientes nuevos de un banco | El BCRA no publica altas de clientes. Lo más cercano: cajas de ahorro (`cah`) y titulares de tarjeta (`tit`), trimestrales. |
| Ganancia de un banco en el mes | Los resultados se publican acumulados desde el inicio del ejercicio (`bRes`). El resultado de un mes sale de restar dos acumulados del mismo ejercicio: aclararlo como cálculo. |
| Tasa de plazo fijo de un banco hoy | No está en estas fuentes. `tasa_dep` es la tasa implícita promedio del período, no la tasa de pizarra. |
| Cotización del dólar, acciones, noticias | Fuera de las fuentes (BCRA Información de Entidades, Pagos Minoristas e INDEC IPC). |
| Datos de una billetera virtual como entidad | No figura en la nómina de entidades financieras. Las cuentas de pago agregadas están en `consultar_pagos.py --buscar "cuentas de pago"`. |

---

## Ambigüedad

- **Banco ambiguo:** el script devuelve `candidatos`. Preguntar mostrando la lista. Nunca elegir por cuenta propia.
- **Período no especificado:** usar el último disponible y decir cuál es.
- **Indicador ambiguo:** "cuentas" puede ser cajas de ahorro (`cah`), cuentas corrientes (`cc`) o cuentas sueldo (`remu`); "depósitos" puede ser el saldo (`bDe`) o la cantidad de cuentas. Aclarar cuál se responde o preguntar.

## Rendimiento (medido en octubre de 2026, con buena conexión)

| Consulta | Tiempo |
|---|---|
| Un banco, cualquier sección (`consultar_entidad.py`) | ~1-2 s |
| Ranking de 60 bancos (`consultar_ranking.py`) | ~2-4 s |
| Inflación (`consultar_ipc.py`) | ~2-3 s |
| Pagos (`consultar_pagos.py`) | ~2-4 s |
| Historia de 12 meses (`consultar_historico.py`, 4 PDF) | ~3-10 s según la conexión |
| Ficha institucional (PDF) | ~2-6 s según la conexión |
| Repetir cualquier consulta en la misma sesión | instantáneo (caché de 2 horas) |
