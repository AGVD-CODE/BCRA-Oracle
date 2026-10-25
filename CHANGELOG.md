# Changelog

Cambios de los skills `bcra-oraculo` (español) y `bcra-oracle-en` (inglés). Las versiones siguen [versionado semántico](https://semver.org/lang/es/) según la política de [`docs/CONTRATO.md`](docs/CONTRATO.md): un cambio en una firma pública de `bcra_comun.py`, en una clave de campo o en una clave del JSON de los scripts sube la versión mayor.

## [2.1.2] — 2026-10-25

Parche: no cambian firmas, claves de campo ni claves del JSON. Los skills que dependen de este lo usan sin cambios.

### Corregido

- **Trimestre recién cerrado en `consultar_panel.py`.** Es el mismo hueco que la 2.1.1 arregló en `consultar_historico.py`: un panel que terminaba en un cierre de trimestre (por ejemplo, `--desde 2019-12 --hasta 2019-12 --modo pdf`) dejaba vacíos los campos trimestrales (`pla`, `tit`, `emp`, …), porque el PDF de ese mes trae el trimestre en `---`. Ahora, si al último PDF le faltan esos datos, el panel lee también el PDF del mes siguiente. Si todavía no está publicado y la API tampoco los trae, lo dice en `avisos`.
- **Un vacío ya no borra un dato.** Al juntar PDF y API, una celda `---` de una fuente pisaba el valor que había traído otra. Ahora solo se pisan valores con valores.
- **PDF intermedios de entidades históricas.** Con `--historicas`, si fallaba la descarga de uno de los PDF que completan los últimos meses de una entidad fusionada, el script terminaba con error. Ahora lo anota en `faltantes` y sigue.
- **Aviso de supervivencia.** Con `--historicas` ya no avisa que "las fusionadas o cerradas no están" cuando sí están.

### Agregado

- `tools/verificar.py` controla la información trimestral de Galicia a 2019-12 también con `consultar_panel.py`.

## [2.1.1] — 2026-10-25

Parche: no cambian firmas, claves de campo ni claves del JSON. Los skills que dependen de este (como estratega-bancario desde su 1.1.0) lo usan sin cambios.

### Corregido

- **Historia de las entidades que cambiaron de nombre.** `paginas_entidad_pdf` buscaba la entidad por su nombre actual en el índice del PDF, así que `consultar_historico.py` no encontraba al Santander (antes Santander Río) en los PDF anteriores a junio de 2022 ni al BBVA (antes BBVA Francés) en los anteriores a diciembre de 2019. Ahora, si el nombre actual no está en el índice, ubica la entidad por su código: la primera página de cada entidad empieza con `CODIGO - NOMBRE`. Esa búsqueda lee el PDF entero (unos 2 s) y el resultado queda en la caché, junto al PDF. `consultar_panel.py` ya ubicaba las entidades por código y no cambia.
- **Trimestre recién cerrado en `consultar_historico.py`.** Pedir solo un mes de cierre de trimestre (`--desde 2019-12 --hasta 2019-12`) daba `null` en casi todos los campos trimestrales (`pla`, `tit`, `emp`, …), porque el PDF de ese mes trae el trimestre vacío. Ahora, si el último PDF leído es de un cierre de trimestre y le faltan esos datos, el script lee también el PDF del mes siguiente, que los completa. Si todavía no está publicado, la `nota` del campo lo dice.

### Agregado

- `tools/verificar.py` controla el Santander en 2021-12, el BBVA en 2018-12 y la información trimestral del Galicia a 2019-12 pidiendo solo ese mes.

## [2.1.0] — 2026-10-25

Agrega la construcción de paneles a la capa de datos. Compatible con la 2.0.0: no cambia ninguna firma, clave de campo ni clave del JSON existente.

### Por qué

- **Los skills de análisis necesitan muchas entidades × muchos meses.** Con `consultar_historico.py` eso es una llamada por entidad, y cada una vuelve a leer los PDF. estratega-bancario había resuelto esto con su propio script (`panel_bcra.py`), que importaba funciones internas del módulo. Ahora vive acá, en la capa de datos, y cualquier skill lo puede usar sin importar nada.
- **El contrato tiene que viajar con el skill.** Antes estaba solo en `docs/` del repositorio y no llegaba a donde el skill está instalado.

### Agregado

- `scripts/consultar_panel.py`: panel de muchas entidades × meses × campos en un CSV ancho (`periodo`, `codigo`, `entidad`, `tipo` y un campo por columna) y un JSON con la cobertura, las unidades y los avisos.
  - Siempre incluye los agregados oficiales: sistema, públicos, privados y 10 primeros privados.
  - Convierte cada PDF mensual una sola vez para todas las entidades: 5 años de los ~60 bancos en ~25 s, y 10 años de 25 bancos en ~50 s.
  - `--historicas` suma las entidades que reportaron en el período y ya no están vigentes, como Banco BMA (ex Itaú), código 259, o HSBC / Banco GGAL, código 150, con su último mes de dato, para armar series pro forma. Si una deja de reportar entre dos PDF del plan, baja los PDF intermedios para no perder sus últimos meses.
- `references/contrato.md` en los dos skills: el contrato (antes `docs/CONTRATO.md`, que ahora apunta acá). Suma `consultar_panel.py` a la sección 4 y describe cómo usa este skill estratega-bancario desde su 1.1.0.
- `tools/verificar.py`: valores de control de Galicia (abril de 2026) leídos con `consultar_panel.py`, y prueba en vivo del panel por API.

### Para los skills que dependen

Nada que cambiar. Para obtener paneles, pueden reemplazar código propio por `consultar_panel.py` y exigir `VERSION` ≥ 2.1.0.

## [2.0.0] — 2026-10-25

Reescritura completa. Es la versión que se usa en Claude y no se había subido al repositorio.

### Por qué

- **La v1 era lenta y frágil.** Cada pregunta descargaba el PDF mensual del BCRA (de 3,5 a 17 MB) con `wget`, lo convertía entero con `pdftotext` y buscaba el dato en el texto. Una pregunta simple tardaba lo que tardaba esa descarga.
- **La v1 necesitaba instalar paquetes** (`xlrd`, `openpyxl`) en entornos donde muchas veces no se puede.
- **El BCRA rediseñó su sitio.** La página que citaba la v1 (`PublicacionesEstadisticas/Entidades_financieras.asp`) hoy devuelve 404.
- **El XLS del IPC daba un mes de atraso.** Se nombra por mes de publicación y un mes futuro devuelve una página HTML: la regla de "probar desde el mes actual hacia atrás" se quedaba con el mes anterior.
- **La v1 no podía hacer rankings ni series largas** sin bajar y procesar decenas de PDF a mano.

### Cambió

- **Fuente principal: la API JSON del BCRA** (la de las páginas "Información de Entidades Financieras"). Responde en ~1 segundo con pocos KB por entidad y sección.
- **Historia desde 2014** con los PDF mensuales: se lee solo el índice y las 4 páginas de la entidad (~0,1 s), y un PDF cada 3 meses alcanza.
- **IPC desde el CSV del INDEC** (`serie_ipc_divisiones.csv`), con URL fija y siempre al día. Las acumuladas se calculan con el índice, como el INDEC (2024: 117,8 %).
- **Pagos minoristas:** el script busca por su cuenta el último XLSX publicado y lo lee con la biblioteca estándar (se comparó celda por celda con openpyxl: 0 diferencias).
- **Solo biblioteca estándar de Python 3.8+.** Ya no hacen falta `wget`, `xlrd` ni `openpyxl`. `pdftotext` (poppler) sigue haciendo falta, pero solo para la historia y la ficha institucional.
- **`SKILL.md` reescrito** alrededor de "un comando por pregunta", con la tabla de comandos, cómo leer la respuesta y las trampas que cambian la respuesta. Las referencias (`diccionario.md`, `fuentes.md`, `consultas.md` y sus versiones en inglés) se actualizaron a las fuentes nuevas.
- **Totales del sistema y de grupos** (sistema, públicos, privados, compañías financieras, 10 primeros privados) tal como los publica el BCRA, ya ponderados, en lugar de calcularlos sumando bancos.
- **`null` significa "sin dato publicado"**: el 0 y el 99999 que usa el BCRA como marcadores ya no se confunden con valores reales.

### Agregado

- `scripts/bcra_comun.py`: módulo compartido por todos los scripts, con descargas con reintentos y caché de 2 horas, resolución de nombres y alias, el catálogo `CAMPOS` (117 claves estables) y los parsers de la API y del PDF. Tiene la constante `VERSION`.
- `scripts/consultar_ranking.py`: ranking de las ~60 entidades por cualquier campo, cuota de mercado (`--participacion`), filtros por valor y por tamaño (`--entre-mayores`).
- `scripts/consultar_historico.py`: series mensuales de cualquier campo desde 2014.
- `consultar_entidad.py`: secciones de cartera por situación (1 a 5), cuentas sueldo, sucursales y cajeros por provincia y ficha institucional (presidente, gerente general, accionistas, auditor).
- `consultar_ipc.py`: rubros, núcleo, regulados, estacionales, bienes y servicios, regiones, acumuladas entre dos meses y ranking de divisiones.
- Errores siempre en JSON: `candidatos` si el nombre es ambiguo, `sugerencias_por_parecido` si no es una entidad financiera, `sin_acceso_red` si el entorno no llega a las fuentes.
- `tools/verificar.py`: corre los valores de control (`references/fuentes.md`, sección 6) y los checksums de la v1, y compara la API con el PDF.
- `docs/CONTRATO.md`: cómo construir otros skills sobre `bcra-oraculo`.
- `bcra-oracle-en.skill`: paquete del skill en inglés.

### Incompatible con la 1.0.0

- **Cambió la forma de llamar a los scripts.** En la v1 se descargaba el archivo a mano y se le pasaba al script (`consultar_entidad.py entidades.txt --periodo ... --banco ...`, `consultar_ipc.py ipc.xls`, `consultar_pagos.py pagos.xlsx`). En la v2 los scripts descargan solos y reciben la entidad o la serie (`consultar_entidad.py Galicia --campo irr_tot`).
- `consultar_entidad.py --todos` pasó a ser `consultar_ranking.py CAMPO --todos`.
- `consultar_pagos.py --hojas` pasó a ser `--series`, y `--hoja` ya no vuelca las filas crudas de la hoja: filtra la búsqueda por hoja.
- `consultar_entidad.py` y `consultar_ipc.py` ya no leen un archivo descargado a mano. Solo `consultar_pagos.py` lo acepta (`--archivo`).
- **Las claves de campo se mantienen:** las 31 de la v1 (`irr_tot`, `roa`, `bA`, `pla`, …) siguen con el mismo nombre y la misma unidad. La v2 agrega 86.

## [1.0.0] — 2026-08-12

Primera versión publicada. La versión en inglés (`bcra-oracle-en`) se agregó el 2026-10-20, con los mismos scripts.

- `SKILL.md` con el flujo "entender qué dato se pide → descargar la última versión → extraer → responder" y la regla de nunca inventar.
- `consultar_entidad.py`: extraía balance e indicadores de un banco, o de todos (`--todos`), del texto del PDF mensual de Entidades Financieras convertido con `pdftotext`.
- `consultar_ipc.py`: leía el XLS del IPC del INDEC (`sh_ipc_MM_YY.xls`) con `xlrd`.
- `consultar_pagos.py`: listaba y volcaba las hojas del XLSX de Pagos Minoristas con `openpyxl`.
- Referencias: `fuentes.md`, `diccionario.md` (31 campos) y `consultas.md`.
- Paquete `bcra-oraculo.skill`.

[2.1.2]: https://github.com/AGVD-CODE/BCRA-Oracle/releases/tag/v2.1.2
[2.1.1]: https://github.com/AGVD-CODE/BCRA-Oracle/releases/tag/v2.1.1
[2.1.0]: https://github.com/AGVD-CODE/BCRA-Oracle/releases/tag/v2.1.0
[2.0.0]: https://github.com/AGVD-CODE/BCRA-Oracle/releases/tag/v2.0.0
[1.0.0]: https://github.com/AGVD-CODE/BCRA-Oracle/tree/5577537
