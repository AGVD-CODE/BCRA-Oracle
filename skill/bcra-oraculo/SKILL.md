---
name: bcra-oraculo
description: Consulta en vivo datos oficiales del sistema financiero argentino (BCRA e INDEC) y responde con el dato, su período y la fuente. Usar SIEMPRE que el usuario pregunte por bancos o compañías financieras argentinas (mora o cartera irregular, situación de deudores, préstamos, depósitos, activo, patrimonio, resultados, ROE, ROA, apalancamiento, liquidez, tasas, tarjetas de crédito o débito, cajas de ahorro, cuentas sueldo, empleados, sucursales, cajeros, presidente o accionistas), por rankings o comparaciones entre entidades (qué banco tiene más X, top 5 de Z, cuota de mercado), por la evolución de un indicador, por totales del sistema financiero, por inflación del INDEC (IPC general, núcleo, rubros, acumulada) o por medios de pago (transferencias, tarjetas, cheques, ECHEQ, ticket promedio). Si el dato no está publicado, lo dice sin inventar. No arma dashboards.
compatibility: Requiere ejecución de código con Python 3.8+ y acceso de red a www.bcra.gob.ar y www.indec.gob.ar. pdftotext (poppler-utils) solo para series de más de 5 meses y para la ficha institucional.
---

# Oráculo del Sistema Financiero Argentino

Responde preguntas sobre el sistema financiero argentino con datos oficiales del BCRA y del INDEC obtenidos en el momento de la consulta. Los scripts de `scripts/` descargan la última publicación, extraen el dato y devuelven JSON con valor, período, unidad y fuente.

## Regla de oro: nunca inventar

- **Responder solo con datos que devolvió un script en esta sesión.** Nunca de memoria ni con estimaciones.
- **Si el dato no está publicado, decirlo.** "El BCRA no publica ese dato" vale más que un número aproximado.
- **Citar siempre período y fuente.** Ejemplo: "según el BCRA (Información de Entidades Financieras), a julio de 2026".
- **Separar dato directo de dato calculado.** Si hubo un cálculo (participación, variación, ticket promedio, cartera irregular por situaciones), decirlo y explicar la fórmula en una línea.
- **`null` en el JSON significa "sin dato publicado"**, nunca cero.

## Un comando por pregunta

Ejecutar desde la carpeta de este skill (las rutas son relativas a este archivo). Los scripts usan solo Python estándar: **no instalar nada**. Repetir una consulta en la misma sesión es instantáneo, porque los scripts guardan las descargas en caché durante 2 horas.

**Para preguntas comunes, no leer las referencias:** el comando está en esta tabla.

| La pregunta pide | Comando |
|---|---|
| Panorama de un banco | `python3 scripts/consultar_entidad.py Galicia` |
| Uno o varios datos de un banco | `python3 scripts/consultar_entidad.py Galicia --campo irr_tot pla roe` |
| Tarjetas, cuentas, plazos fijos, empleados | `python3 scripts/consultar_entidad.py Nacion --seccion adicional` |
| Sucursales y cajeros (por provincia) | `python3 scripts/consultar_entidad.py Macro --seccion sucursales --provincias` |
| Balance o resultados | `python3 scripts/consultar_entidad.py Santander --seccion balance` |
| Situación de deudores (situaciones 1 a 5) | `python3 scripts/consultar_entidad.py BBVA --seccion cartera` |
| Presidente, gerente general, accionistas, auditor | `python3 scripts/consultar_entidad.py Galicia --seccion ficha` |
| Total del sistema o de un grupo | `python3 scripts/consultar_entidad.py sistema --campo irr_tot pla` (grupos: `sistema`, `publicos`, `privados`, `companias`, `top10`) |
| Ranking o comparación entre entidades | `python3 scripts/consultar_ranking.py irr_tot --top 5` |
| Cuota de mercado | `python3 scripts/consultar_ranking.py pla --top 10 --participacion` |
| Cuántas entidades superan un umbral | `python3 scripts/consultar_ranking.py irr_tot --mayor-que 10` |
| Evolución reciente (hasta 5 períodos) | `python3 scripts/consultar_entidad.py Galicia --campo irr_tot --serie` |
| Evolución de 6 meses o más | `python3 scripts/consultar_historico.py Galicia --campo irr_tot --meses 12` |
| Panel de muchas entidades y meses en un CSV (para análisis o para otro skill) | `python3 scripts/consultar_panel.py --meses 24 --salida panel.csv` (`--top 20`, `--entidades Galicia Macro`, `--historicas` para sumar las entidades ya no vigentes) |
| Inflación del último mes (con rubros) | `python3 scripts/consultar_ipc.py` |
| Inflación de un mes, una serie o acumulada | `python3 scripts/consultar_ipc.py --mes 2026-06` · `--serie nucleo --meses 12` · `--acumulado 2026` · `--acumulado --desde 2025-07 --hasta 2026-06` |
| Qué rubro subió más | `python3 scripts/consultar_ipc.py --ranking-divisiones` |
| Medios de pago | `python3 scripts/consultar_pagos.py --buscar "tarjetas de crédito"` (agregar `--meses 12` para la serie; `--series` lista todo) |

Si la pregunta mezcla fuentes (por ejemplo, ticket promedio contra inflación), correr los comandos necesarios **en paralelo** y combinar los resultados.

### Campos más usados

Lista completa: `python3 scripts/consultar_entidad.py --campos` o `references/diccionario.md`.

- **Mora y calidad de cartera (mensual, %):** `irr_tot` mora total · `irr_cons` consumo · `irr_com` comercial · `irr_priv` sector privado · `prev_irr` cobertura con previsiones · `tf_s1`…`tf_s5` situaciones · `tf_irregular` situaciones 3+4+5.
- **Rentabilidad y otros indicadores (mensual):** `roe` · `roa` · `apalancamiento` (veces) · `tasa_prest` · `tasa_dep` · `liq_tit_cot` · `dep_empleado`.
- **Balance (mensual, millones de pesos):** `bA` activo · `bPr` préstamos · `bDe` depósitos · `bPN` patrimonio neto · `bCA` saldo en cajas de ahorro · `bPF` plazos fijos · `bRes` resultado acumulado del ejercicio.
- **Información adicional (trimestral, cantidades):** `pla` tarjetas de crédito · `tit` titulares · `deb` tarjetas de débito · `cah` cajas de ahorro · `cc` cuentas corrientes · `emp` empleados.
- **Mensual, cantidades:** `remu` cuentas sueldo · `sucursales` · `cajeros`.

## Cómo leer la respuesta del script

- `datos.<campo>.valor` y `.periodo` ("YYYY-MM"): el dato y el mes al que corresponde.
- `candidatos`: el nombre es ambiguo. Preguntar al usuario cuál quiere, mostrando los candidatos.
- `sugerencias_por_parecido` con error "no figura en la nómina": la entidad no es un banco ni una compañía financiera registrada (por ejemplo, una billetera virtual). Decirlo. No elegir una sugerencia por cuenta propia.
- `sin_dato_publicado` o `sin_dato_en_el_periodo`: el BCRA no publica ese dato para esa entidad. Decirlo.
- `sin_acceso_red: true`: el entorno no llega a las fuentes. Pedir al usuario que habilite el acceso de red a `www.bcra.gob.ar` y `www.indec.gob.ar` en la configuración de ejecución de código, o que suba el archivo. Nunca responder de memoria.
- Error "Falta pdftotext": solo afecta a `consultar_historico.py` y a `--seccion ficha`. Si el entorno lo permite, instalarlo (`apt-get install -y poppler-utils`). Si no, avisar que esa consulta no está disponible y ofrecer los 5 períodos de `--serie`.

## Formato de respuesta

Dar el dato con su unidad, el período y la fuente. Si es calculado, agregar cómo se calculó.

> El Banco Galicia tenía **4.930.958 tarjetas de crédito** (plásticos) a **junio de 2026**, según la Información de Entidades Financieras del BCRA.

> Galicia concentra el **12,9 %** de las tarjetas de crédito del sistema a junio de 2026 (4,93 millones de 38,1 millones). *Participación calculada sobre el total del sistema financiero.*

> El BCRA no publica la cantidad de clientes por banco. Lo más cercano que publica es la cantidad de cajas de ahorro (10.607.086 en Galicia a junio de 2026) y de titulares de tarjetas de crédito.

*(Los números de estos ejemplos son reales a la fecha indicada; en cada consulta usar los que devuelva el script.)*

## Trampas que cambian la respuesta

- **Los períodos difieren por sección.** Balance, indicadores, mora, sucursales y cuentas sueldo son mensuales. Tarjetas, cuentas y empleados son trimestrales: su último período puede ser anterior. Si una respuesta mezcla datos, dar el período de cada uno.
- **Unidades.** El balance está en millones de pesos corrientes (40.325.296,7 millones = 40,3 billones de pesos; en Argentina, 1 billón = 1 millón de millones). La situación de deudores también está en millones. Indicadores y mora en %.
- **Valores nominales.** Para comparar montos en el tiempo, avisar que no están ajustados por inflación. Si hace falta, ajustar con `consultar_ipc.py` y aclararlo como cálculo.
- **Rankings de mora.** Los bancos chicos o de nicho suelen encabezarlos. Si la pregunta busca relevancia sistémica, usar `--entre-mayores 20` u ofrecerlo.
- **Historia:** `consultar_historico.py` llega hasta 2014 con todos los campos. Para 2011-2013 faltan los indicadores de mora; antes de 2011 no hay historia. Solo funciona con entidades vigentes hoy; las que cambiaron de nombre (Santander Río, BBVA Francés) se encuentran igual.
- **"Sistema"** incluye bancos y compañías financieras. Los rankings usan solo bancos (públicos y privados), salvo que se pida `--grupo todas` o `--grupo companias`.
- **Alias.** "Provincia" es el Banco de la Provincia de Buenos Aires. "Nación" es el Banco de la Nación Argentina. "Naranja X" es Naranja Digital Compañía Financiera. Ante cualquier otra duda, el script devuelve candidatos.

## Qué NO hace

- No arma dashboards, gráficos ni HTML: solo consulta y responde.
- No responde sobre datos fuera de estas fuentes: dólar, acciones, plazos fijos de pizarra o noticias. Decir "eso no está en las fuentes que consulto (BCRA e INDEC)".
- No inventa. Ver la regla de oro.

## Referencias (leer solo si hace falta)

- `references/diccionario.md`: todos los campos, unidades, frecuencia y qué cálculos se pueden hacer. Leer si la pregunta usa un concepto que no está en la lista de arriba.
- `references/consultas.md`: recetas para preguntas analíticas, de evolución, cruzadas y de "dato inexistente".
- `references/fuentes.md`: URLs, formato de cada fuente, trampas conocidas y cómo adaptarse si el BCRA o el INDEC cambian algo. Leer solo si un script falla.
- `references/contrato.md`: qué puede usar otro skill de este (funciones, scripts, formato de salida y política de versiones). Leer si se construye un skill encima de este.
