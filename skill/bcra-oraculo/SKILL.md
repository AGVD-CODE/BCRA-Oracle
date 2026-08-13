---
name: bcra-oraculo
description: Consulta datos oficiales del sistema financiero argentino (BCRA e INDEC) para responder preguntas puntuales y analíticas. Usar SIEMPRE que el usuario pregunte por indicadores de bancos argentinos como tarjetas de crédito o débito, cajas de ahorro, cuentas, depósitos, préstamos, mora o cartera irregular, sucursales, cajeros, empleados, ROE, ROA, apalancamiento, balance, o por inflación del INDEC, o por comparaciones y rankings entre entidades (qué banco tiene más X, cómo evolucionó Y, top 5 de Z). El skill descarga el último reporte disponible de la fuente oficial, valida que sea la versión más reciente, extrae el dato real y responde citando período y fuente. Si el dato no existe en ningún reporte, responde que no se dispone del dato, sin inventar. No arma dashboards ni archivos HTML, solo consulta y responde.
---

# Oráculo del Sistema Financiero Argentino

Este skill responde preguntas sobre el sistema financiero argentino yendo a buscar el dato **real** a las fuentes oficiales (BCRA e INDEC), en el momento de la consulta. No usa datos cacheados ni de memoria: para cada pregunta descarga el último reporte publicado, valida que sea la versión más reciente disponible, extrae el dato exacto y responde.

## Regla de oro: nunca inventar

Esta es la regla más importante del skill y no admite excepciones:

- **Solo responder con datos extraídos de una fuente oficial en esta misma sesión.** Nunca responder de memoria, ni con conocimiento general, ni con estimaciones.
- **Si el dato no está en los reportes, decir explícitamente que no se dispone del dato.** No aproximar, no completar, no "dar una idea". Una respuesta honesta de "el BCRA no publica ese dato" vale más que un número inventado.
- **Siempre citar el período del dato y la fuente.** Ej: "según el informe de Entidades Financieras del BCRA a marzo 2026". Esto hace la respuesta verificable.
- **Distinguir dato directo de dato calculado.** Si la pregunta requiere un cálculo (peso de mercado, ranking, variación), aclararlo y explicar brevemente cómo se calculó.
- **Ante la duda sobre si un número es real o recordado, no usarlo.** Volver a la fuente.

## Flujo para responder una pregunta

### 1. Entender qué dato se pide y en qué fuente vive

Identificar qué indicador pide la pregunta y mapearlo a su fuente. El mapa completo está en `references/diccionario.md`, pero a grandes rasgos:

| Tema de la pregunta | Fuente | Reporte |
|---|---|---|
| Tarjetas de crédito/débito, cajas de ahorro, cuentas sueldo, sucursales, cajeros, empleados | BCRA | Información Adicional (Entidades) |
| Mora, cartera irregular, situaciones 1-5, previsiones, calidad de cartera | BCRA | Entidades Financieras (PDF) |
| Balance: activo, préstamos, depósitos, patrimonio | BCRA | Entidades Financieras (PDF) |
| Indicadores: ROE, ROA, apalancamiento, tasas, liquidez | BCRA | Entidades Financieras (PDF) |
| Volumen y monto de pagos, transferencias, ticket promedio, cheques, ECHEQ | BCRA | Informe de Pagos Minoristas (XLSX) |
| Inflación, IPC, variación de precios, canasta, divisiones | INDEC | IPC Nacional (XLS) |

Leer `references/fuentes.md` para las URLs exactas y las trampas de descarga (críticas — ver abajo).

### 2. Descargar la última versión disponible

**Este paso es obligatorio en cada consulta.** No asumir que un archivo descargado antes sigue vigente. Descargar la fuente correspondiente y **validar que sea la más reciente** siguiendo las reglas de `references/fuentes.md`.

Trampas críticas que el skill debe manejar (detalle completo en `references/fuentes.md`):
- **INDEC:** el archivo se nombra por el **mes de publicación**, no por el mes del dato. El IPC de junio se publica en julio → archivo `sh_ipc_07_26.xls`. Probar desde el mes actual hacia atrás hasta encontrar el archivo válido (~2.3MB; los meses futuros dan un placeholder de ~36KB).
- **BCRA PDF grande (>5MB):** las herramientas de Drive fallan. Usar `wget` directo + `pdftotext -layout`.
- **BCRA Pagos:** el slug de la URL alterna entre dos patrones; probar ambos.

Para saber cuál es el último período disponible, probar el mes más reciente y retroceder hasta que la descarga sea válida.

### 3. Extraer el dato con los scripts

Usar el extractor correspondiente en `scripts/`:
- `consultar_entidad.py` — indicadores, balance, mora y cartera de un banco (o de todos) desde el PDF del BCRA.
- `consultar_adicional.py` — tarjetas, cuentas, sucursales, cajeros, empleados desde Información Adicional.
- `consultar_pagos.py` — medios de pago desde el XLSX del BCRA.
- `consultar_ipc.py` — inflación desde el XLS del INDEC.
- `consultar_ranking.py` — para preguntas analíticas que recorren todos los bancos.

Cada script recibe la fuente ya descargada y devuelve los datos parseados. Ver `references/consultas.md` para el detalle de cómo invocarlos y cómo resolver cada tipo de pregunta.

### 4. Responder

Formato de respuesta:
- **El dato**, con su unidad.
- **El período** al que corresponde.
- **La fuente** oficial.
- Si es calculado, **cómo se calculó**.

**Ejemplo de respuesta a dato directo:**
> El Banco Galicia tenía **4.383.666 plásticos de crédito** emitidos a **marzo 2026**, según la Información Adicional de Entidades Financieras del BCRA.

**Ejemplo de respuesta a dato calculado:**
> El Banco Galicia representa el **9,3%** de las tarjetas de débito del sistema a marzo 2026 (7,5M de tarjetas del banco sobre 81,7M del sistema). *Peso de mercado calculado sobre el total de las 45 entidades que reportan tarjetas de débito.*

**Ejemplo de dato inexistente:**
> El BCRA no publica la cantidad de clientes por sucursal en sus informes de Entidades Financieras. El dato disponible más cercano es la cantidad de sucursales (321 para Galicia a marzo 2026) y de empleados (6.025), pero no la relación clientes/sucursal.

## Tipos de preguntas

### Puntuales (un banco, un indicador)
"¿Cuántas cajas de ahorro tiene el Banco Nación?" → descargar la fuente, extraer el dato de ese banco, responder.

### Analíticas (comparaciones, rankings, evolución)
"¿Qué banco tiene más mora?", "¿top 5 por sucursales?", "¿cómo evolucionó la mora de Galicia en el último año?" → estas requieren recorrer **todos** los bancos o **varios períodos**. Usar `consultar_ranking.py`. Avisar al usuario que puede tardar un poco más porque procesa el reporte completo. Detalle en `references/consultas.md`.

### Cruzadas (mezclan fuentes)
"¿El ticket promedio de crédito le ganó a la inflación en el último mes?" → descargar Pagos (BCRA) e IPC (INDEC), extraer ambos, comparar. Aclarar que son dos fuentes distintas con posibles rezagos distintos.

## Identificación de bancos

Los nombres varían entre reportes. Usar el mapeo de `references/diccionario.md` (sección "Identificación de entidades"). Casos frecuentes:
- El usuario dice "Galicia" → "BANCO DE GALICIA Y BUENOS AIRES S.A.U." (código 7).
- "Nación" → "BANCO DE LA NACION ARGENTINA" (código 11).
- "Provincia" → "BANCO DE LA PROVINCIA DE BUENOS AIRES".
- Variantes con acentos, "S.A.", "S.A.U.", sucursales, etc. Buscar de forma flexible (sin distinguir mayúsculas/acentos) y, si hay ambigüedad, preguntar al usuario cuál de los candidatos quiere.

Si el banco no existe en el reporte, decirlo: "No encuentro una entidad con ese nombre en el informe del BCRA. Las entidades disponibles son: [listar las más parecidas]."

## Qué NO hace este skill

- **No arma dashboards ni archivos HTML.** Si el usuario pide un dashboard, aclarar que este skill solo consulta y responde datos; para el dashboard existe un skill/proyecto distinto.
- **No responde sobre datos fuera de las fuentes.** Cotización del dólar, acciones, tasas de otros países, noticias: fuera de alcance. Responder "eso no está en las fuentes que consulto (BCRA e INDEC)".
- **No inventa.** Ver la regla de oro.

## Requisitos del entorno

Este skill necesita un entorno con ejecución de código (`wget`, `python3` con `xlrd`/`openpyxl`, `pdftotext`). Sin eso, puede leer las instrucciones pero no ejecutar las descargas ni las extracciones. Instalar dependencias si faltan:
```bash
pip install xlrd openpyxl --break-system-packages
```

## Archivos de referencia

- `references/fuentes.md` — URLs oficiales, patrones de descarga y todas las trampas conocidas. **Leer siempre antes de descargar.**
- `references/diccionario.md` — qué es cada campo, en qué fuente vive, unidades, cómo se calcula, e identificación de entidades. **Leer para mapear la pregunta al dato.**
- `references/consultas.md` — recetas para resolver cada tipo de pregunta (puntual, analítica, cruzada), con ejemplos.
