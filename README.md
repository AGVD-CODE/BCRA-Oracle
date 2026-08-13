# Oráculo del Sistema Financiero Argentino

Un **Skill de Claude** que responde preguntas sobre el sistema financiero argentino consultando en vivo las fuentes oficiales del **BCRA** y el **INDEC**. Preguntás en lenguaje natural —"¿cuántas tarjetas de crédito tiene el Banco Galicia?", "¿qué banco tiene más mora?", "¿cuál fue la inflación de junio?"— y el oráculo va a buscar el dato al reporte oficial, valida que sea la última versión disponible, lo extrae y te responde citando el período y la fuente.

## Cómo funciona (importante: no es cacheado ni instantáneo)

Este oráculo **no usa datos guardados ni conocimiento previo del modelo**. Para cada pregunta:

1. **Identifica** qué dato pedís y en qué fuente oficial vive.
2. **Descarga el último reporte publicado** de esa fuente, en el momento de la consulta.
3. **Valida que sea la versión más reciente disponible** (los reportes del BCRA e INDEC se publican con rezago y con nombres que cambian mes a mes; el oráculo prueba hacia atrás hasta encontrar el archivo válido más nuevo).
4. **Extrae el dato exacto** del reporte con scripts de parsing probados.
5. **Responde** con el dato, el período al que corresponde y la fuente.

Como cada consulta implica descargar y procesar un reporte oficial (algunos de varios MB), **las respuestas tardan lo que tarda esa descarga y extracción** — no son instantáneas. A cambio, son datos oficiales reales y verificables, no una estimación.

**Y lo más importante: si el dato no existe en ningún reporte, el oráculo lo dice.** No inventa, no aproxima, no completa con conocimiento general. Una respuesta de "el BCRA no publica ese dato" es preferible a un número inventado.

## Qué puede responder

Cualquier indicador que esté en estas tres fuentes oficiales:

**BCRA — Entidades Financieras** (mensual): mora y cartera irregular, situaciones de deuda 1 a 5, previsiones, balance (activo, préstamos, depósitos, patrimonio), indicadores (ROE, ROA, apalancamiento, tasas, liquidez).

**BCRA — Información Adicional** (trimestral): tarjetas de crédito y débito, cajas de ahorro, cuentas sueldo, sucursales, cajeros, empleados.

**BCRA — Pagos Minoristas** (mensual): volumen y monto de transferencias, tarjetas, débitos directos, cheques, ECHEQ, ticket promedio.

**INDEC — IPC Nacional** (mensual): inflación (nivel general, núcleo, regulados, estacional), variación mensual e interanual, divisiones de la canasta.

### Tipos de preguntas

- **Puntuales:** "¿Cuántas cajas de ahorro tiene el Banco Nación?"
- **Analíticas / rankings:** "¿Cuáles son los 5 bancos con más mora?", "¿los 3 más grandes por activo?"
- **De evolución:** "¿Cómo evolucionó la mora del Galicia en el último año?"
- **Cruzadas:** "¿El ticket promedio de crédito le ganó a la inflación el último mes?"

## Instalación

### Requisitos
- Tener **Claude** con un entorno de **ejecución de código** activado (la herramienta de análisis, Claude Code, o Cowork). El oráculo necesita poder ejecutar descargas (`wget`) y scripts de Python. Sin eso, tiene las instrucciones pero no puede ir a buscar los datos.

### Pasos
1. Descargá el archivo del Skill: **`bcra-oraculo.skill`** (está en este repositorio).
2. Instalalo en tu Claude:
   - En **claude.ai**: Configuración → Skills → subir el archivo.
   - En **Claude Code / Cowork**: seguí las instrucciones de instalación de skills de tu entorno.
3. Listo. En cualquier conversación nueva (con la herramienta de análisis activada), preguntá lo que quieras sobre el sistema financiero argentino y el Skill se activa solo.

> La primera vez, si falta alguna librería de Python, el Skill instala lo necesario (`xlrd`, `openpyxl`) automáticamente.

## Ejemplo de uso

**Vos:** ¿Cuántas tarjetas de crédito tiene el Banco Galicia, cuántas cajas de ahorro y cuál es su mora?

**Claude (con el oráculo):**
> El Banco Galicia, según los datos del BCRA:
> - **Tarjetas de crédito:** 4.383.666 plásticos emitidos (Información Adicional, marzo 2026).
> - **Cajas de ahorro:** 10.316.472 cuentas (Información Adicional, marzo 2026).
> - **Mora:** 8,09% de cartera irregular (Entidades Financieras, abril 2026).

Ver más ejemplos en [`docs/EJEMPLOS.md`](docs/EJEMPLOS.md).

## Estructura del repositorio

```
Oraculo-sistema_financiero/
├── README.md                    → este archivo
├── LICENSE                      → licencia MIT
├── skill/
│   └── bcra-oraculo/            → el Skill (esto es lo que se instala)
│       ├── SKILL.md             → instrucciones maestras del oráculo
│       ├── references/          → fuentes, diccionario de datos, recetas de consulta
│       └── scripts/             → extractores de cada fuente
├── docs/
│   └── EJEMPLOS.md              → catálogo de preguntas de ejemplo
└── bcra-oraculo.skill           → el Skill empaquetado, listo para instalar
```

## Limitaciones

- **Solo responde lo que está en las fuentes.** Cotización del dólar, acciones, tasas de otros países, noticias: fuera de alcance.
- **Requiere ejecución de código.** No funciona en un Claude sin la herramienta de análisis.
- **Las fuentes oficiales cambian sin aviso.** El BCRA y el INDEC a veces modifican formatos o nombres de archivos. Cuando eso pasa, la extracción puede requerir un ajuste; el Skill le da a Claude el contexto para adaptarse, pero no es infalible.
- **No arma dashboards.** Este proyecto solo consulta y responde datos. (Existe un proyecto hermano para generar dashboards.)

## Fuentes oficiales

- BCRA — Entidades Financieras: https://www.bcra.gob.ar/PublicacionesEstadisticas/Entidades_financieras.asp
- BCRA — Pagos Minoristas: https://www.bcra.gob.ar/PublicacionesEstadisticas/Informe-mensual-pagos-minoristas.asp
- INDEC — IPC: https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31

## Licencia

MIT — ver [LICENSE](LICENSE). Podés usar, modificar y redistribuir este código libremente, manteniendo el aviso de copyright.

## Autor

Alejandro Vaamonde

---

*Este proyecto no está afiliado ni respaldado por el BCRA, el INDEC ni Anthropic. Consulta datos públicos de fuentes oficiales.*
