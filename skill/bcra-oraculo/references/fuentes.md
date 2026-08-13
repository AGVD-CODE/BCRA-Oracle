# Fuentes oficiales y patrones de descarga

Este documento tiene las URLs exactas y **todas las trampas conocidas** para descargar la última versión de cada fuente. Leer antes de cada descarga. Las fuentes oficiales cambian formatos y nombres sin aviso; si algo falla, adaptarse leyendo el archivo descargado y ajustando el parseo.

## Índice
1. BCRA — Entidades Financieras (PDF): balance, indicadores, mora, cartera
2. BCRA — Información Adicional: tarjetas, cuentas, sucursales, cajeros, empleados
3. BCRA — Informe de Pagos Minoristas (XLSX): medios de pago
4. INDEC — IPC Nacional (XLS): inflación
5. Cómo determinar el último período disponible

---

## 1. BCRA — Entidades Financieras (PDF)

Contiene, por banco: balance completo, indicadores (ROE, ROA, apalancamiento, tasas, liquidez), y calidad de cartera (mora, cartera irregular, situaciones 1-5, previsiones).

**Frecuencia:** mensual.

**URL (patrón):**
```
https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/YYYYMMe.pdf
```
Donde `YYYYMM` es año y mes del dato. Ej: abril 2026 → `202604e.pdf`.

**Cómo descargar (el PDF pesa ~6MB, las herramientas de Drive fallan):**
```bash
wget -q "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202604e.pdf" -O /tmp/entidades.pdf
pdftotext -layout /tmp/entidades.pdf /tmp/entidades.txt
```
`pdftotext -layout` es importante: preserva la disposición en columnas del PDF, sin eso el parseo falla.

**Validar que descargó bien:** el PDF válido pesa varios MB. Si pesa muy poco o `wget` devuelve error 404, ese mes todavía no se publicó → probar el mes anterior.

**Página de referencia (para citar la fuente):**
`https://www.bcra.gob.ar/PublicacionesEstadisticas/Entidades_financieras.asp`

---

## 2. BCRA — Información Adicional

Tarjetas de crédito y débito, titulares, cuentas sueldo, cajas de ahorro, distribución geográfica de sucursales y cajeros, empleados.

**Frecuencia:** trimestral (marzo, junio, septiembre, diciembre).

Esta información viene en el mismo circuito de publicaciones del BCRA. Los datos de tarjetas y cuentas suelen estar en cuadros de "Información Adicional" dentro de las publicaciones de entidades. El extractor `consultar_adicional.py` sabe localizar estos cuadros en el texto extraído del PDF.

**Nota sobre períodos:** como es trimestral, el último dato disponible puede ser de un mes anterior al último dato mensual de balance/mora. Ej: si el balance llega a abril, las tarjetas pueden llegar a marzo. Aclararlo al responder.

---

## 3. BCRA — Informe de Pagos Minoristas (XLSX)

Volumen y monto de transferencias, débitos directos, cheques, ECHEQ, tarjetas, pagos con transferencia (PCT), etc. Serie histórica larga.

**Frecuencia:** mensual.

**URL (patrón):**
```
https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Informes/series-informe-mensual-pagos-minoristas-YYYY-MM.xlsx
```
Ej: junio 2026 → `series-informe-mensual-pagos-minoristas-2026-06.xlsx`.

**Cómo descargar (pesa ~170KB, funciona directo):**
```bash
wget -q "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Informes/series-informe-mensual-pagos-minoristas-2026-06.xlsx" -O /tmp/pagos.xlsx
```

**Ventaja:** un solo archivo trae la serie histórica completa (18+ meses), así que con el más reciente se obtiene todo.

**Trampa del slug:** la URL de la *página* del informe (no del archivo) alterna entre dos patrones:
```
https://www.bcra.gob.ar/publicaciones/informe-de-pagos-minoristas-MES-de-AAAA/
https://www.bcra.gob.ar/publicaciones/informe-mensual-de-pagos-minoristas-MES-de-AAAA/
```
Si se necesita la página (raramente), probar ambos. Para el dato, basta el XLSX de arriba.

**Página de referencia (para citar):**
`https://www.bcra.gob.ar/PublicacionesEstadisticas/Informe-mensual-pagos-minoristas.asp`

---

## 4. INDEC — IPC Nacional (XLS)

Inflación: nivel general, núcleo, regulados, estacional, bienes, servicios, 12 divisiones de la canasta, variación mensual e interanual.

**Frecuencia:** mensual.

**URL (patrón):**
```
https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_MM_YY.xls
```

**TRAMPA CRÍTICA — el nombre es el mes de PUBLICACIÓN, no del dato:**
El IPC de un mes se publica a mediados del mes siguiente. Entonces `MM_YY` es el mes en que se publicó el archivo, y el archivo contiene datos *hasta el mes anterior*.

- El IPC de **junio 2026** se publica en **julio 2026** → archivo `sh_ipc_07_26.xls` (contiene datos hasta junio).
- Para conseguir el dato más reciente, **probar desde el mes actual hacia atrás:**
  ```bash
  # Probar sh_ipc_08_26 (agosto), luego 07_26, etc.
  wget -q "https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_07_26.xls" -O /tmp/ipc.xls
  ```
- **Cómo saber si el archivo es válido:** el archivo con datos reales pesa **~2.3MB**. Los meses que todavía no se publicaron devuelven un **placeholder de ~36KB**. Verificar el tamaño:
  ```bash
  ls -la /tmp/ipc.xls  # si pesa ~36KB, es placeholder → probar el mes anterior
  ```

**Dependencia:** requiere `xlrd` para leer .xls antiguo:
```bash
pip install xlrd --break-system-packages
```

**Hojas del archivo:**
- `"Variación mensual IPC Nacional"` — variación mes a mes.
- `"Var. interanual IPC Nacional"` — variación contra el mismo mes del año anterior (últimos 12 meses).
- Fila 5 = fechas (formato serial de Excel). Series identificadas por etiqueta en la columna 0.

**Validación de referencia (para confirmar que se parsea bien):**
- Nov-25 mensual = 2,5%
- May-26 mensual = 2,1%
- 2024 completo (acumulado) = 117,7% (oficial: 117,8%)
- 2025 completo = 31,5%

**Página de referencia (para citar):**
`https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31`

---

## 5. Cómo determinar el último período disponible

Para cualquier fuente, la estrategia es la misma: **probar el período más reciente y retroceder hasta que la descarga sea válida.**

1. Partir del mes actual (o del mes de publicación esperado, en el caso del INDEC).
2. Intentar descargar.
3. Validar: ¿el archivo tiene el tamaño esperado? ¿`wget` no dio 404? ¿el contenido parsea?
4. Si no es válido, retroceder un mes y reintentar.
5. Al encontrar el válido, ese es el último período disponible. Usarlo y **decir en la respuesta a qué período corresponde.**

Nunca asumir el período: siempre verificar cuál es el último realmente publicado al momento de la consulta.

---

## Nota sobre restricciones de red

Si el entorno bloquea el acceso directo a `bcra.gob.ar` o `indec.gob.ar` (algunos entornos cloud devuelven 503), avisar al usuario que puede necesitar habilitar el acceso a esos dominios en la configuración de red, o descargar el archivo manualmente y subirlo. El sitio del BCU de Uruguay (`bcu.gub.uy`) da 503 consistente desde cloud; el BCRA e INDEC suelen funcionar directo.
