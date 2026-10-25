# Argentine Financial System Oracle · Oráculo del Sistema Financiero Argentino

> **Available in English and Spanish — Disponible en inglés y español**

A **Claude Skill** that answers questions about the Argentine financial system by querying live official sources from the **BCRA** and **INDEC**. Ask in natural language — *"How many credit cards does Banco Galicia have?"*, *"Top 5 banks by NPL"*, *"How did Galicia's NPL evolve since 2020?"*, *"What was June's inflation?"* — and the oracle fetches the figure from the official publication, extracts it, and responds citing the period and source.

Un **Skill de Claude** que responde preguntas sobre el sistema financiero argentino consultando en vivo las fuentes oficiales del **BCRA** y el **INDEC**. Preguntás en lenguaje natural —"¿cuántas tarjetas de crédito tiene el Banco Galicia?", "top 5 de bancos por mora", "¿cómo evolucionó la mora del Galicia desde 2020?", "¿cuál fue la inflación de junio?"— y el oráculo va a buscar el dato a la publicación oficial, lo extrae y te responde citando el período y la fuente.

It is also the **data layer** for other skills: analysis skills can import its module and get every figure with stable keys, without parsing the sources again. See [Building on this skill](#building-on-this-skill--para-construir-sobre-este-skill).

También es la **capa de datos** de otros skills: un skill de análisis puede importar su módulo y obtener cada dato con claves estables, sin volver a parsear las fuentes. Ver [Para construir sobre este skill](#building-on-this-skill--para-construir-sobre-este-skill).

---

## What's new in v2 / Qué cambió en la v2

Version 2.0.0 is a full rewrite. In short:

- **Official BCRA JSON API** as the main source: about one second per query, instead of downloading and converting a 3.5–17 MB PDF for each question.
- **History back to 2014** from the monthly "Información de Entidades Financieras" PDFs (`consultar_historico.py`).
- **Rankings and market share** across the ~60 banks (`consultar_ranking.py`), and **system and group totals** as published by the BCRA.
- **Python standard library only.** No `wget`, `xlrd` or `openpyxl`; `pdftotext` is needed only for history and the institutional profile.
- **A shared module, `scripts/bcra_comun.py`**, with stable field keys and a version number (`VERSION`), documented in [`references/contrato.md`](skill/bcra-oraculo/references/contrato.md).
- **INDEC CPI from the official CSV**, with a fixed URL that is always up to date (the old XLS lagged one month).
- **Control values** that can be checked with `python3 tools/verificar.py`.
- **New in 2.1.0: panels for other skills.** `consultar_panel.py` builds many entities × many months in one CSV (5 years of the ~60 banks in about 25 s), including entities that no longer exist (`--historicas`) for pro-forma series. The contract now ships inside the skill (`references/contrato.md`).

La versión 2.0.0 es una reescritura completa. En resumen:

- **API JSON oficial del BCRA** como fuente principal: alrededor de un segundo por consulta, en lugar de descargar y convertir un PDF de 3,5 a 17 MB en cada pregunta.
- **Historia desde 2014** con los PDF mensuales "Información de Entidades Financieras" (`consultar_historico.py`).
- **Rankings y cuotas de mercado** entre los ~60 bancos (`consultar_ranking.py`), y **totales del sistema y de grupos** tal como los publica el BCRA.
- **Solo biblioteca estándar de Python.** Sin `wget`, `xlrd` ni `openpyxl`; `pdftotext` solo hace falta para la historia y la ficha institucional.
- **Un módulo compartido, `scripts/bcra_comun.py`**, con claves de campo estables y número de versión (`VERSION`), documentado en [`references/contrato.md`](skill/bcra-oraculo/references/contrato.md).
- **IPC del INDEC desde el CSV oficial**, con URL fija y siempre al día (el XLS anterior daba un mes de atraso).
- **Valores de control** que se comprueban con `python3 tools/verificar.py`.
- **Nuevo en la 2.1.0: paneles para otros skills.** `consultar_panel.py` arma muchas entidades × muchos meses en un CSV (5 años de los ~60 bancos en unos 25 s). Con `--historicas` incluye las entidades que ya no existen, para armar series pro forma. El contrato ahora viaja dentro del skill (`references/contrato.md`).

Details, reasons and incompatible changes / Detalle, motivos y cambios incompatibles: [`CHANGELOG.md`](CHANGELOG.md).

---

## How it works / Cómo funciona

**It does not use cached data or model memory.** For each question, Claude runs one of the skill's scripts, which:

1. **Resolves** the bank, group or series that was asked for (with aliases such as "Nación" or "Provincia"; if the name is ambiguous, it returns the candidates).
2. **Queries the latest publication** of the right source: the BCRA API for current data, the monthly PDFs for history, the INDEC CSV for inflation, the BCRA XLSX for retail payments.
3. **Returns JSON** with the figure, its period, its unit and the source, which Claude uses to answer.

Downloads are cached for 2 hours, so repeating a question in the same session is instant.

**Most importantly: if the data does not exist in any publication, the oracle says so.** It does not fabricate, approximate, or complete with general knowledge. `null` means "not published", never zero.

**No usa datos guardados ni la memoria del modelo.** En cada pregunta, Claude corre uno de los scripts del skill, que:

1. **Resuelve** el banco, el grupo o la serie pedida (con alias como "Nación" o "Provincia"; si el nombre es ambiguo, devuelve los candidatos).
2. **Consulta la última publicación** de la fuente que corresponde: la API del BCRA para los datos vigentes, los PDF mensuales para la historia, el CSV del INDEC para la inflación y el XLSX del BCRA para los pagos minoristas.
3. **Devuelve JSON** con el dato, su período, su unidad y la fuente, y Claude responde con eso.

Las descargas quedan en caché 2 horas: repetir una pregunta en la misma sesión es instantáneo.

**Lo más importante: si el dato no existe en ninguna publicación, el oráculo lo dice.** No inventa, no aproxima y no completa con conocimiento general. `null` significa "no publicado", nunca cero.

---

## What it can answer / Qué puede responder

**BCRA — Financial Entities / Entidades Financieras** (monthly / mensual, history since 2014 / historia desde 2014): NPL and irregular portfolio, debtor situations 1–5, provisions, balance sheet and results (assets, loans, deposits, equity), ratios (ROE, ROA, leverage, rates, liquidity), payroll accounts, branches and ATMs by province / mora y cartera irregular, situación de deudores 1 a 5, previsiones, balance y resultados (activo, préstamos, depósitos, patrimonio), indicadores (ROE, ROA, apalancamiento, tasas, liquidez), cuentas sueldo, sucursales y cajeros por provincia.

**BCRA — Additional Information / Información Adicional** (quarterly / trimestral): credit and debit cards, cardholders, savings and checking accounts, fixed-term deposits, employees / tarjetas de crédito y débito, titulares, cajas de ahorro y cuentas corrientes, plazos fijos, empleados.

**BCRA — Institutional profile / Ficha institucional** (monthly PDF / PDF mensual): chairman, general manager, shareholders, auditor / presidente, gerente general, accionistas, auditor.

**BCRA — Retail Payments / Pagos Minoristas** (monthly / mensual, since 2017 / desde 2017): volume and amount of transfers, cards, direct debits, checks, ECHEQ, average ticket / cantidad y monto de transferencias, tarjetas, débitos automáticos, cheques, ECHEQ, ticket promedio.

**INDEC — National CPI / IPC Nacional** (monthly / mensual): headline, core, regulated, seasonal, goods and services, 12 basket divisions, 7 regions, cumulative inflation between any two months / nivel general, núcleo, regulados, estacionales, bienes y servicios, 12 divisiones, 7 regiones, inflación acumulada entre dos meses cualesquiera.

### Example questions / Ejemplos de preguntas

- "How many savings accounts does Banco Nación have?" / "¿Cuántas cajas de ahorro tiene el Banco Nación?"
- "Top 5 banks by NPL, among the 20 largest" / "Top 5 de bancos por mora, entre los 20 más grandes"
- "Galicia's market share in credit cards" / "Cuota de mercado del Galicia en tarjetas de crédito"
- "How did Galicia's NPL evolve over the last 24 months?" / "¿Cómo evolucionó la mora del Galicia en los últimos 24 meses?"
- "Who is the chairman of Banco Macro?" / "¿Quién es el presidente del Banco Macro?"
- "Did the average credit card ticket beat inflation last month?" / "¿El ticket promedio de crédito le ganó a la inflación el último mes?"

See more examples in / Más ejemplos en [`docs/EJEMPLOS.md`](docs/EJEMPLOS.md).

---

## Installation / Instalación

### Requirements / Requisitos

- A Claude environment with **code execution** (claude.ai with code execution enabled, Claude Code, or Cowork).
- **Network access to `www.bcra.gob.ar` and `www.indec.gob.ar`.** Many code-execution environments only allow a list of domains: add these two (or allow all domains) in the code-execution settings. Without access, the skill tells the user instead of answering from memory.
- **Python 3.8+, nothing to install:** the scripts use only the standard library.
- **Optional: `pdftotext`** (poppler) for histories longer than 5 periods and for the institutional profile: `brew install poppler` (macOS) or `apt-get install -y poppler-utils` (Debian/Ubuntu).

- Un entorno de Claude con **ejecución de código** (claude.ai con ejecución de código activada, Claude Code o Cowork).
- **Acceso de red a `www.bcra.gob.ar` y `www.indec.gob.ar`.** Muchos entornos solo permiten una lista de dominios: agregar estos dos (o permitir todos) en la configuración de ejecución de código. Sin acceso, el skill lo avisa en lugar de responder de memoria.
- **Python 3.8+, sin instalar nada:** los scripts usan solo la biblioteca estándar.
- **Opcional: `pdftotext`** (poppler) para series de más de 5 períodos y para la ficha institucional: `brew install poppler` (macOS) o `apt-get install -y poppler-utils` (Debian/Ubuntu).

### Steps / Pasos

1. Download the package for your language from the [latest release](https://github.com/AGVD-CODE/BCRA-Oracle/releases/latest) (or from the root of this repository) / Descargá el paquete de tu idioma desde la [última release](https://github.com/AGVD-CODE/BCRA-Oracle/releases/latest) (o desde la raíz de este repositorio):
   - **`bcra-oraculo.skill`**: Spanish / español.
   - **`bcra-oracle-en.skill`**: English / inglés.

   A `.skill` file is a ZIP with the skill folder inside. If an upload form only accepts `.zip`, rename it / Un `.skill` es un ZIP con la carpeta del skill adentro. Si un formulario solo acepta `.zip`, renombralo.
2. Install it / Instalalo:
   - **claude.ai:** enable code execution and network access in the settings, then upload the file in the Skills section / activá la ejecución de código y el acceso de red en la configuración, y subí el archivo en la sección de Skills.
   - **Claude Code:** unzip it into your skills folder / descomprimilo en tu carpeta de skills:
     ```bash
     unzip bcra-oraculo.skill -d ~/.claude/skills/
     ```
3. Ask anything about the Argentine financial system in a new conversation. The skill activates on its own, **in whichever language you use** / Preguntá lo que quieras sobre el sistema financiero argentino en una conversación nueva. El skill se activa solo, **en el idioma en que preguntes**.

---

## Repository structure / Estructura del repositorio

```
BCRA-Oracle/
├── README.md
├── CHANGELOG.md                 → versions and changes / versiones y cambios
├── LICENSE
├── skill/
│   ├── bcra-oraculo/            → Spanish skill / skill en español
│   │   ├── SKILL.md
│   │   ├── references/
│   │   │   ├── diccionario.md   → every field key / todas las claves de campo
│   │   │   ├── fuentes.md       → sources, pitfalls, control values / fuentes, trampas, valores de control
│   │   │   ├── consultas.md     → query recipes / recetas de consulta
│   │   │   └── contrato.md      → how to build other skills on top / cómo construir otros skills encima
│   │   └── scripts/
│   │       ├── bcra_comun.py    → shared module (data layer) / módulo compartido (capa de datos)
│   │       ├── consultar_entidad.py
│   │       ├── consultar_ranking.py
│   │       ├── consultar_historico.py
│   │       ├── consultar_panel.py → many entities × months, CSV / muchas entidades × meses, CSV
│   │       ├── consultar_ipc.py
│   │       ├── consultar_pagos.py
│   │       └── requirements.txt
│   └── bcra-oracle-en/          → English skill / skill en inglés
│       ├── SKILL.md
│       ├── references/          → dictionary.md, sources.md, queries.md, contrato.md
│       └── scripts/             → same scripts as the Spanish version / los mismos scripts que en español
├── tools/
│   └── verificar.py             → runs the control values / corre los valores de control
├── docs/
│   ├── CONTRATO.md              → points to references/contrato.md / apunta a references/contrato.md
│   ├── EJEMPLOS.md              → example questions / ejemplos de preguntas
│   └── PUBLICAR_EN_GITHUB.md
├── bcra-oraculo.skill           → Spanish package, ready to install / paquete en español, listo para instalar
└── bcra-oracle-en.skill         → English package / paquete en inglés
```

The scripts are identical in both languages / Los scripts son idénticos en los dos idiomas.

---

## Verification / Verificación

```bash
python3 tools/verificar.py
```

Runs the control values from closed publications (Galicia in the April 2026 PDF, INDEC CPI: cumulative 2024 = 117.8 %, 2025 = 31.5 %, …), compares the API with the PDF and checks that the seven scripts work. It prints OK or FALLA for each check. It needs network access and `pdftotext`.

Corre los valores de control de publicaciones cerradas (Galicia en el PDF de abril de 2026, IPC del INDEC: acumulada 2024 = 117,8 %, 2025 = 31,5 %, …), compara la API con el PDF y comprueba que funcionen los siete scripts. Informa OK o FALLA por cada comprobación. Necesita red y `pdftotext`.

---

## Building on this skill / Para construir sobre este skill

`bcra-oraculo` is meant to be the data layer of other skills. Its module `scripts/bcra_comun.py` exposes functions (`resolver`, `consultar`, `pdf_entidades`, `normalizar_pdf`, …), a catalog of 117 stable field keys (`CAMPOS`) and a version number. Another skill can either import it, when both skills are installed side by side, or include a copy that states which version it took. For many entities over time it can simply run `consultar_panel.py` and read its CSV.

**[`references/contrato.md`](skill/bcra-oraculo/references/contrato.md)** documents the public functions with their inputs and outputs, the exceptions, the JSON returned by the scripts, the field keys and the versioning policy: any change to a signature or a key bumps the major version and is recorded in the [`CHANGELOG.md`](CHANGELOG.md).

`bcra-oraculo` está pensado como la capa de datos de otros skills. Su módulo `scripts/bcra_comun.py` expone funciones (`resolver`, `consultar`, `pdf_entidades`, `normalizar_pdf`, …), un catálogo de 117 claves de campo estables (`CAMPOS`) y un número de versión. Otro skill puede importarlo, si los dos están instalados uno al lado del otro, o incluir una copia que diga qué versión tomó. Para muchas entidades en el tiempo, alcanza con correr `consultar_panel.py` y leer su CSV.

**[`references/contrato.md`](skill/bcra-oraculo/references/contrato.md)** documenta las funciones públicas con sus entradas y salidas, las excepciones, el JSON que devuelven los scripts, las claves de los campos y la política de versiones: todo cambio en una firma o una clave sube la versión mayor y queda registrado en el [`CHANGELOG.md`](CHANGELOG.md).

---

## Related projects / Proyectos relacionados

- **[Banking-Metrics-Analyst](https://github.com/AGVD-CODE/Banking-Metrics-Analyst)** (`estratega-bancario`): a strategic-analysis skill for Argentine banks built on this data layer. It compares many entities over time, crosses them with macro data and turns the findings into sized business opportunities, with charts. Since its 1.1.0 it uses the installed `bcra-oraculo` (≥ 2.1, same major version) with a version check instead of a copy. / Skill de análisis estratégico de bancos argentinos construido sobre esta capa de datos. Compara muchas entidades en el tiempo, las cruza con la macro y convierte los hallazgos en oportunidades de negocio dimensionadas, con gráficos. Desde su 1.1.0 usa el `bcra-oraculo` instalado (2.1 o posterior, misma versión mayor) con control de versión, en lugar de una copia.

---

## Limitations / Limitaciones

- **Only answers what is in the sources.** Exchange rates, stocks, rates from other countries, board rates for fixed-term deposits, news: out of scope.
- **Requires code execution and network access** to `www.bcra.gob.ar` and `www.indec.gob.ar`.
- **History:** complete since 2014; for 2011–2013 the NPL ratios are missing (the BCRA used other codes); nothing before 2011. Only for entities that exist today.
- **Official sources change without notice.** When the BCRA or INDEC change a format or a URL, extraction may need an adjustment. `tools/verificar.py` detects it, and the skill gives Claude the context to adapt, but it is not infallible.
- **No dashboards.** This project only queries and answers data.

- **Solo responde lo que está en las fuentes.** Dólar, acciones, tasas de otros países, tasas de pizarra de plazo fijo, noticias: fuera de alcance.
- **Requiere ejecución de código y acceso de red** a `www.bcra.gob.ar` y `www.indec.gob.ar`.
- **Historia:** completa desde 2014; en 2011-2013 faltan los indicadores de mora (el BCRA usaba otros códigos); antes de 2011, nada. Solo para entidades vigentes hoy.
- **Las fuentes oficiales cambian sin aviso.** Cuando el BCRA o el INDEC cambian un formato o una URL, la extracción puede necesitar un ajuste. `tools/verificar.py` lo detecta, y el skill le da a Claude el contexto para adaptarse, pero no es infalible.
- **No arma dashboards.** Este proyecto solo consulta y responde datos.

---

## Official sources / Fuentes oficiales

- BCRA — Financial Entities / Entidades Financieras: https://www.bcra.gob.ar/total-del-sistema-financiero/ (per entity / por entidad: `https://www.bcra.gob.ar/entidades-financieras-indicadores-economicos/?bco=00007&tipo=1`)
- BCRA — Retail Payments / Pagos Minoristas: https://www.bcra.gob.ar/informe-de-pagos-minoristas/
- INDEC — CPI / IPC: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31

---

## License / Licencia

MIT — see [LICENSE](LICENSE). Free to use, modify and redistribute, keeping the copyright notice.

## Author / Autor

Alejandro Vaamonde

---

*This project is not affiliated with or endorsed by the BCRA, INDEC, or Anthropic. It queries public data from official sources.*

*Este proyecto no está afiliado ni respaldado por el BCRA, el INDEC ni Anthropic. Consulta datos públicos de fuentes oficiales.*
