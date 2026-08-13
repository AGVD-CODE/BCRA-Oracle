# Recetas de consulta

Cómo resolver cada tipo de pregunta, con ejemplos concretos. Los scripts de `scripts/` hacen la extracción; este documento explica cuándo usar cada uno y cómo componer la respuesta.

## Flujo general (siempre)

1. Identificar el/los indicador(es) y su fuente (ver `diccionario.md`).
2. Descargar la última versión de la(s) fuente(s) (ver `fuentes.md`).
3. Validar contra checksums si aplica.
4. Extraer con el script correspondiente.
5. Responder con dato + período + fuente. Si no existe, decirlo.

---

## Tipo 1 — Consulta puntual (un banco, uno o varios indicadores)

**Ejemplo:** "¿Cuántas tarjetas de crédito tiene el Banco Galicia? ¿Y cajas de ahorro? ¿Cuál es su mora?"

Receta:
1. Resolver el nombre "Galicia" → código 7 (ver diccionario, Identificación de entidades).
2. Tarjetas de crédito y cajas de ahorro → Información Adicional (trimestral). Descargar y correr `consultar_adicional.py`.
3. Mora → Entidades PDF (mensual). Correr `consultar_entidad.py`.
4. Responder los tres datos, cada uno con su período (¡pueden ser distintos: tarjetas a marzo, mora a abril!):

> El Banco Galicia, según los datos del BCRA:
> - **Tarjetas de crédito:** 4.383.666 plásticos emitidos (Información Adicional, marzo 2026).
> - **Cajas de ahorro:** 10.316.472 cuentas (Información Adicional, marzo 2026).
> - **Mora:** 8,09% de cartera irregular (Entidades Financieras, abril 2026).

---

## Tipo 2 — Consulta analítica: ranking / comparación

**Ejemplo:** "¿Qué banco tiene más mora?" / "¿Top 5 por cantidad de sucursales?" / "¿Cuáles son los 3 bancos más grandes por activo?"

Estas requieren recorrer **todos** los bancos del reporte. Usar `consultar_ranking.py`, que extrae el indicador pedido para todas las entidades y las ordena.

Receta:
1. Avisar al usuario que puede tardar un poco más (procesa el reporte completo, no un solo banco).
2. Descargar la fuente correspondiente.
3. Correr `consultar_ranking.py` con el indicador pedido.
4. Responder el ranking, aclarando el período y, si corresponde, filtrando entidades sin sentido (ej. excluir Compañías Financieras si la pregunta es sobre bancos).

> Los 5 bancos con mayor mora (cartera irregular), a abril 2026, según el BCRA:
> 1. Banco de Servicios Financieros — 50,5%
> 2. Banco Sáenz — 37,7%
> 3. Banco Sucrédito Regional — 24,8%
> 4. Banco Rioja — 22,8%
> 5. Ualá Bank — 22,1%
>
> *Ordenado por el indicador de cartera irregular sobre financiaciones totales. Nota: algunos son bancos de nicho con cartera mayormente de consumo.*

**Cuidado con los rankings de mora:** los bancos chicos y de nicho suelen liderar por mora. Si la pregunta busca relevancia sistémica, ofrecer también el peso de cada uno o filtrar por tamaño mínimo — pero solo si el usuario lo pide o si aclararlo evita una lectura engañosa.

---

## Tipo 3 — Consulta de evolución (un banco/indicador, varios períodos)

**Ejemplo:** "¿Cómo evolucionó la mora del Banco Galicia en el último año?"

Requiere varios períodos. Dos caminos según la fuente:
- **Pagos e IPC:** un solo archivo trae la serie histórica → descargar uno y extraer la serie completa.
- **Entidades (mora, balance):** cada mes es un PDF distinto → hay que descargar varios PDFs (uno por período). Avisar que esto tarda más. Descargar los meses del rango pedido y extraer el indicador de cada uno.

Receta para mora de Galicia último año:
1. Determinar los meses del último año disponibles.
2. Para cada mes, descargar el PDF de Entidades y extraer `irr_tot` de Galicia.
3. Presentar la serie:

> Evolución de la mora del Banco Galicia (cartera irregular), últimos meses según el BCRA:
> - Dic-25: 6,9%
> - Ene-26: 7,7%
> - Feb-26: 7,7%
> - Mar-26: 7,7%
> - Abr-26: 8,1%
>
> La mora subió de 6,9% a 8,1% en el período.

---

## Tipo 4 — Consulta cruzada (mezcla fuentes)

**Ejemplo:** "¿El ticket promedio de crédito le ganó a la inflación el último mes?"

Combina dos fuentes. Descargar ambas, extraer, comparar. Aclarar que son fuentes distintas con posibles rezagos distintos.

Receta:
1. Ticket promedio de crédito → Pagos (XLSX BCRA). Extraer monto/operaciones del último mes y del anterior; calcular la variación del ticket.
2. Inflación mensual → IPC (XLS INDEC) del mismo mes.
3. Comparar:

> En [mes], el ticket promedio de compras con tarjeta de crédito varió +X% mientras la inflación fue +Y% (INDEC). El ticket [creció más/menos] que los precios ese mes.
>
> *Ticket promedio = monto total / cantidad de operaciones (BCRA, Pagos Minoristas). Inflación = variación mensual del IPC nivel general (INDEC). Ambas fuentes pueden tener rezagos distintos: verificar que los períodos coincidan.*

---

## Tipo 5 — El dato no existe

**Ejemplo:** "¿Cuántos clientes nuevos sumó el Banco X el mes pasado?"

El BCRA no publica altas de clientes. Responder honestamente:

> El BCRA no publica la cantidad de clientes nuevos por banco en sus informes. Los datos disponibles más cercanos son la cantidad de cajas de ahorro y de titulares de tarjetas, pero no las altas netas de clientes por período.

Nunca inventar ni estimar. Si hay un dato *cercano* que podría servir, ofrecerlo aclarando que no es exactamente lo pedido.

---

## Manejo de ambigüedad

- **Banco ambiguo:** si "Banco Provincia" puede ser Provincia de Buenos Aires u otra, listar los candidatos y preguntar.
- **Período no especificado:** usar el último disponible y aclararlo. Si el usuario quiere otro, que lo pida.
- **Indicador ambiguo:** "cuentas" puede ser cajas de ahorro, cuentas corrientes o cuentas sueldo. Si no queda claro, aclarar cuál se está respondiendo o preguntar.

## Rendimiento

- Una consulta puntual sobre un banco: una descarga (rápida para XLSX/XLS, más lenta para el PDF de ~6MB).
- Una consulta analítica (ranking): una descarga + procesar todos los bancos.
- Una consulta de evolución sobre Entidades: varias descargas (un PDF por mes). La más lenta — avisar.
- Dentro de una misma sesión, reutilizar archivos ya descargados para el mismo período en lugar de volver a bajarlos.
