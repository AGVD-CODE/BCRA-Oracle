# Contrato de bcra-oraculo para otros skills

`bcra-oraculo` es la **capa de datos** de esta biblioteca de skills: descarga las publicaciones oficiales del BCRA y del INDEC, las normaliza y devuelve cada dato con una clave estable, su período, su unidad y su fuente. Los skills de análisis (por ejemplo, [estratega-bancario](https://github.com/AGVD-CODE/Banking-Metrics-Analyst)) se construyen encima y no vuelven a parsear las fuentes.

Este documento dice qué puede dar por estable un skill que depende de `bcra-oraculo` dentro de una misma versión mayor. Describe la **versión 2.0.0** (`bcra_comun.VERSION`).

## Índice
1. Dos formas de usarlo
2. Funciones y datos públicos de `bcra_comun.py`
3. Excepciones
4. JSON que devuelven los scripts
5. Claves de los campos
6. Política de versiones

---

## 1. Dos formas de usarlo

### A. Importar el módulo del skill instalado al lado

Si `bcra-oraculo` está instalado en la misma carpeta de skills que el tuyo (`skills/bcra-oraculo/` y `skills/mi-skill/`), importá su módulo directamente. Recibís las correcciones de `bcra-oraculo` sin copiar nada, pero tu skill deja de funcionar si `bcra-oraculo` no está instalado.

```python
# mi-skill/scripts/datos.py
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', '..', 'bcra-oraculo', 'scripts'))
import bcra_comun as bc  # noqa: E402

if bc.VERSION.split('.')[0] != '2':
    raise ImportError('mi-skill necesita bcra-oraculo 2.x; está instalada la %s' % bc.VERSION)
```

Controlá siempre la versión mayor: es la que garantiza este contrato (sección 6).

También podés correr los scripts de `bcra-oraculo` como procesos y leer su JSON (sección 4). Sirve para preguntas sueltas; para recorrer muchas entidades, importar el módulo es más rápido.

### B. Incluir una copia de `bcra_comun.py`

Copiá `skill/bcra-oraculo/scripts/bcra_comun.py` en `scripts/` de tu skill. El skill queda autocontenido: no depende de que `bcra-oraculo` esté instalado. A cambio, las correcciones no llegan solas: hay que volver a copiar.

Reglas para la copia:

- **Copiá desde una release** (`v2.0.0`, …), no desde `main`, y no la edites: los cambios van a este repositorio.
- **Dejá constancia de qué versión copiaste.** La constante `VERSION` del archivo ya lo dice; agregá además al principio del docstring de dónde salió:

  ```python
  """
  Funciones compartidas por los scripts del Oráculo BCRA.

  Copia incluida en mi-skill, tomada de bcra-oraculo 2.0.0
  (https://github.com/AGVD-CODE/BCRA-Oracle/releases/tag/v2.0.0, licencia MIT).
  No editar acá: los cambios van al repositorio de bcra-oraculo.
  ...
  """
  ```

- **Para actualizarla,** leé el `CHANGELOG.md` desde la versión que tenés. Si sube la versión mayor, revisá lo que dice que cambió antes de reemplazar la copia.

**Así lo hace estratega-bancario:** usa su copia en `skill/estratega-bancario/scripts/bcra_comun.py` y, si se define la variable de entorno `BCRA_ORACULO_DIR` con la carpeta de un `bcra-oraculo` instalado, usa la de ese skill. Su copia actual es idéntica a la 2.0.0 de este repositorio salvo la constante `VERSION` y la línea de versionado del docstring, que se agregaron después.

Combinar las dos formas (copia por defecto, instalada si se pide) es lo más robusto:

```python
def cargar_bcra_comun():
    externo = os.environ.get('BCRA_ORACULO_DIR')
    sys.path.insert(0, os.path.join(externo, 'scripts') if externo else AQUI)
    import bcra_comun
    return bcra_comun
```

---

## 2. Funciones y datos públicos de `bcra_comun.py`

Convenciones que valen para todo:

- **Período:** texto `"YYYY-MM"`, el mes al que corresponde el dato (no el de publicación).
- **Serie:** `{"YYYY-MM": valor}`. `None` significa "sin dato publicado" (la fuente muestra celda vacía, `---`, `0` o `99999`). Nunca es cero.
- **Unidades:** las de `CAMPOS`. El balance se devuelve en **millones** de pesos (la API publica miles: el módulo convierte). Indicadores en %, salvo `apalancamiento` (veces) y `dep_empleado` / `fin_empleado` (millones de pesos).
- **Red y caché:** todas las funciones que descargan usan una caché en disco compartida por todos los skills (`<tmp>/bcra-oraculo-cache`), de 2 horas (24 horas para los PDF). `BCRA_ORACULO_TTL=<segundos>` cambia la duración; `BCRA_ORACULO_SIN_CACHE=1` la desactiva.
- **Hilos:** las funciones se pueden llamar desde varios hilos a la vez (es lo que hace `en_paralelo`).

### `VERSION`

`str`, por ejemplo `"2.0.0"`. Versión semántica del módulo (sección 6).

### `nomina(grupo='AAA00')`

Entidades vigentes de un grupo, según el BCRA.

- **Entrada:** `grupo`, código de grupo de la API: `'AAA00'` sistema financiero (bancos y compañías financieras), `'AAA10'` públicas, `'AAA20'` privadas, `'AAA30'` compañías financieras, `'AAA50'` 10 primeros bancos privados. Son los primeros elementos de `GRUPOS`.
- **Salida:** `list` de `{'codigo': int, 'nombre': str}`, por ejemplo `{'codigo': 7, 'nombre': 'BANCO DE GALICIA Y BUENOS AIRES S.A.'}`. Los nombres vienen cortados a 40 caracteres.
- **Errores:** `ErrorFuente` (consulta en mantenimiento o respuesta inválida), `SinRed`.

### `resolver(consulta, entidades=None)`

Convierte lo que escribió el usuario en una entidad o un grupo.

- **Entrada:** `consulta`, nombre, alias (`'Nación'`, `'Provincia'`, `'BBVA'`), código BCRA (`'7'`, `'00007'`) o grupo (`'sistema'`, `'privados'`, `'AAA20'`, …). `entidades`: lista de `nomina()` ya descargada, para no volver a pedirla.
- **Salida para una entidad:** `{'codigo': 7, 'api': '00007', 'nombre': 'BANCO DE GALICIA Y BUENOS AIRES S.A.', 'tipo': 'entidad'}`.
- **Salida para un grupo:** `{'codigo': 'AAA00', 'api': 'AAA00', 'nombre': 'SISTEMA FINANCIERO (bancos y compañías financieras)', 'tipo': 'grupo', 'grupo': 'sistema'}`.
- **Errores:** `Ambiguo` con `.datos = {'candidatos': [{'codigo', 'nombre'}, …]}` si coincide con varias entidades, o con `.datos = {'sugerencias_por_parecido': [...]}` si no figura en la nómina (por ejemplo, una billetera virtual). `ErrorFuente` si el código no existe. `SinRed`.

El campo `api` es el que se pasa a `consultar`. No elegir un candidato por cuenta propia: preguntarle al usuario.

### `consultar(codigo_api_, secciones)`

Trae de la API del BCRA las secciones pedidas de una entidad o grupo (en paralelo) y las une.

- **Entrada:** `codigo_api_`, el `api` de `resolver` (`'00007'`, `'AAA00'`). `secciones`, conjunto de nombres: `'indicadores'`, `'balance'`, `'cartera'`, `'adicional'`, `'remuneraciones'`, `'sucursales'` (las tres últimas salen del mismo pedido).
- **Salida:**

  ```python
  {
      'campos': {'irr_tot': {'2024-12': 1.83, '2025-12': 6.9, '2026-05': 8.94, '2026-06': 8.3, '2026-07': 9.13}, ...},
      'titulos': {'irr_tot': 'A9 - Total Cartera Irregular / Total Financiaciones (%)', ...},  # título original
      'actualizado': '2026-07',                    # el más reciente de las secciones
      'actualizado_por_seccion': {'indicadores': '2026-07', 'adicional': '2026-07', ...},
      'nombre_fuente': 'BANCO DE GALICIA Y BUENOS AIRES S.A.',   # opcional, nombre sin cortar
      'extra': {
          'filas_balance': [{'titulo', 'nivel', 'valores': {per: millones}}],  # con 'balance'
          'por_provincia': {provincia: {'suc_plenas': n, 'cajeros': n, ...}},   # con 'adicional'
          'exterior': [...], 'composicion_sistema': {...},
          'errores': {'cartera': 'mensaje'},       # secciones que fallaron
      },
  }
  ```

  La API publica 5 columnas por sección: los 2 últimos diciembres y los 3 últimos meses (en `adicional`, 3 diciembres y 2 trimestres). `sucursales` trae solo el mes de actualización.
- **Errores:** si falla una sección, no lanza: la anota en `extra['errores']` y devuelve el resto. Lanza `SinRed` si no hay red.

### `pdf_entidades(ym)`

Descarga el PDF mensual "Información de Entidades Financieras" de un mes.

- **Entrada:** `ym`, `'YYYY-MM'`.
- **Salida:** `str`, ruta local del PDF (en la caché). Cada PDF trae ese mes, los dos anteriores y los 2 últimos diciembres. Pesa entre 3,5 y 17 MB.
- **Errores:** `NoEncontrado` si el mes no está publicado (el servidor responde 404 o algo que no es un PDF). `SinRed`, `ErrorFuente`.

### `paginas_entidad_pdf(ruta, entidad)`

Texto de las 4 páginas de una entidad o grupo dentro del PDF.

- **Entrada:** `ruta`, la de `pdf_entidades`. `entidad`, el diccionario de `resolver`.
- **Salida:** `(texto, pagina_inicial)`: el texto de `pdftotext -layout` de esas páginas (separadas por `\f`) y el número de página del archivo donde empiezan.
- **Errores:** `ErrorFuente` si falta `pdftotext`, si no se lee el índice o si la entidad no figura en ese PDF (por ejemplo, una entidad que todavía no existía).
- **Limitación conocida:** la entidad se busca por su nombre **actual** en el índice del PDF. Una entidad que cambió de nombre no se encuentra en los PDF anteriores al cambio (Santander, antes Santander Río, en los PDF anteriores a junio de 2022; BBVA, antes BBVA Francés, en los anteriores a diciembre de 2019).
- **Trimestre recién cerrado:** en el PDF de un mes de cierre de trimestre, la información adicional de ese trimestre suele venir en `---` (`None`). La completa el PDF del mes siguiente.

### `normalizar_pdf(texto)`

Convierte el texto de `paginas_entidad_pdf` a las mismas claves que la API.

- **Entrada:** `texto`.
- **Salida:** el mismo formato que `consultar` (`campos`, `titulos`, `extra`), con `actualizado` en `None`. Cubre `indicadores`, `balance`, `cartera`, `adicional` y `remuneraciones` (no `sucursales`). En `extra['referencias']` vienen, por indicador, los valores de comparación que imprime el PDF: `{'irr_tot': {'grupo_institucional': x, 'diez_primeros': y, 'sistema': z}}`.
- **Historia:** completa desde 2014. En 2011-2013 faltan los indicadores de mora (el BCRA usaba otros códigos y el módulo no los informa para no atribuirlos al indicador equivocado). Antes de 2011 el PDF no se puede leer.

Si varios PDF traen el mismo mes, quedarse con el del PDF más nuevo (puede tener el dato revisado).

### `describir(k)`

- **Entrada:** `k`, clave de campo.
- **Salida:** `{'desc': str, 'unidad': str, 'seccion': str}`. Para una clave desconocida devuelve `{'desc': k, 'unidad': None, 'seccion': None}`.

### `ultimo_valor(serie)`

- **Entrada:** una serie `{'YYYY-MM': valor}`.
- **Salida:** `(periodo, valor)` del período más reciente con dato, o `(None, None)` si no hay ninguno.

### `en_paralelo(funcion, elementos, workers=16)`

- **Entrada:** una función de un argumento y los elementos a los que aplicarla.
- **Salida:** `list` de `(elemento, resultado)` en el **mismo orden** que `elementos`. Si una llamada lanzó una excepción, el resultado es esa excepción (no se relanza), así que hay que revisar `isinstance(r, Exception)`.
- **Errores:** si alguna llamada lanzó `SinRed`, la relanza al final: sin red no tiene sentido seguir.

### `CAMPOS`

`dict` de clave de campo a `(seccion, descripcion, unidad, aditivo)`. Hoy son 117 claves. `aditivo` es `True` para montos y cantidades, que se pueden sumar entre entidades (sirven para calcular participación de mercado); `False` para porcentajes y cocientes.

```python
bc.CAMPOS['pla']      # ('adicional', 'Tarjetas de crédito (plásticos)', 'cantidad', True)
bc.CAMPOS['irr_tot']  # ('indicadores', 'Mora total: cartera irregular / financiaciones totales (A9)', '%', False)
```

### `GRUPOS`

`dict` de nombre de grupo a `(codigo_api, nombre)`: `'sistema'` (`AAA00`), `'publicos'` (`AAA10`), `'privados'` (`AAA20`), `'companias'` (`AAA30`), `'top10'` (`AAA50`). El BCRA publica estos agregados ya ponderados: usarlos en lugar de sumar o promediar entidades.

### `ALIAS`

`dict` de nombre coloquial normalizado (mayúsculas, sin acentos) a código BCRA: `{'GALICIA': 7, 'NACION': 11, 'PROVINCIA': 14, 'NARANJA X': 45030, ...}`. `resolver` ya lo usa y verifica que el código siga en la nómina vigente.

### También estables (las usa estratega-bancario)

Estas no son el núcleo del contrato, pero estratega-bancario ya depende de ellas, así que cambiarlas también sube la versión mayor:

| Nombre | Qué hace |
|---|---|
| `norm(s)` | Mayúsculas, sin acentos ni signos, espacios simples. Es la normalización de `ALIAS` y `ALIAS_GRUPO`. |
| `codigo_api(codigo)` | `7` → `'00007'`; `'AAA00'` queda igual. |
| `mes_anterior(ym, n=1)` | `'2026-01'` → `'2025-12'`. |
| `hay_pdftotext()` | `True` si `pdftotext` está instalado. |
| `ejecutar(main)` y `salida(obj, codigo=0)` | Corren un `main()` y escriben JSON en la salida, con los códigos de la sección 4. |
| `PDF_ENTIDADES` | Plantilla de la URL del PDF mensual (`.format(ym='202604')`). |
| `ALIAS_GRUPO` y `VACIAS` | Nombres de grupo normalizados → clave de `GRUPOS`, y palabras que `resolver` ignora al comparar nombres. |

Todo lo demás del módulo (`api`, `descargar`, `normalizar`, `filas_pdf`, `ficha_pdf`, los mapas de filas, etc.) es interno y puede cambiar en una versión menor. Si otro skill necesita algo de eso, primero se agrega a este contrato.

### Ejemplo

```python
ent = bc.resolver('Galicia')
datos = bc.consultar(ent['api'], {'indicadores', 'adicional'})
periodo, mora = bc.ultimo_valor(datos['campos']['irr_tot'])
info = bc.describir('irr_tot')
print('%s: %s %s a %s' % (info['desc'], mora, info['unidad'], periodo))

# Una serie de 2018 a hoy, desde los PDF (un PDF cada 3 meses)
ruta = bc.pdf_entidades('2018-12')
texto, _ = bc.paginas_entidad_pdf(ruta, ent)
diciembre_2018 = bc.normalizar_pdf(texto)['campos']['bA']['2018-12']
```

---

## 3. Excepciones

```
Exception
├── ErrorFuente      la fuente respondió algo inesperado o no tiene el dato
│   ├── NoEncontrado el archivo no está publicado (HTTP 404) o cambió la URL
│   └── Ambiguo      el nombre no identifica una sola entidad; los candidatos van en .datos
└── SinRed           no hay conexión con la fuente (DNS, proxy o firewall)
```

**`SinRed` no hereda de `ErrorFuente`:** un `except bc.ErrorFuente` no la atrapa. Es a propósito: sin red no hay que responder de memoria, sino pedirle al usuario que habilite el acceso a `www.bcra.gob.ar` y `www.indec.gob.ar` (el texto para eso está en `bc.AYUDA_RED`).

---

## 4. JSON que devuelven los scripts

Los scripts de `skill/bcra-oraculo/scripts/` (`consultar_entidad.py`, `consultar_ranking.py`, `consultar_historico.py`, `consultar_ipc.py`, `consultar_pagos.py`) siguen las mismas reglas:

- Escriben **un objeto JSON** en la salida estándar (UTF-8). Los errores previstos también salen como JSON, no como traceback.
- Los períodos son `"YYYY-MM"` y `null` significa "sin dato publicado".
- Lo que no viene tal cual de la fuente lo dice: los campos calculados tienen "(CALCULADO)" en `desc`, y las variaciones, tickets y acumuladas traen una `nota` o un `metodo` con la fórmula.
- Siempre traen la fuente (`fuente`, y `archivo`, `pdfs`, `pagina` o `consulta_web` para citarla).

**Código de salida y errores:**

| Código | Significado | JSON |
|---|---|---|
| 0 | OK | el resultado |
| 1 | error de la fuente, dato inexistente o nombre ambiguo | `{"error": "..."}`, más `candidatos` o `sugerencias_por_parecido` si el nombre es ambiguo |
| 2 | sin acceso a la red | `{"error": "Sin acceso a la fuente oficial", "detalle": "...", "sin_acceso_red": true, "ayuda": "..."}` |
| 2 | argumentos inválidos | ninguno: argparse escribe el uso en la salida de errores |
| 130 | interrumpido | `{"error": "Interrumpido"}` |

Para distinguir los dos casos del código 2, mirar si la salida estándar trae JSON.

**Claves principales de cada script:**

| Script | Claves |
|---|---|
| `consultar_entidad.py` | `entidad`, `codigo`, `tipo`, `fuente`, `actualizado_a`, `consulta_web`, `datos` (`{clave: {valor, periodo, unidad, desc}}`, más `serie` con `--serie`), `sin_dato_publicado`, `nota`. Según las opciones: `por_provincia`, `exterior`, `balance_completo_millones` (`--filas`), `ficha` (`--seccion ficha`), `errores_fuente`. `--campos` devuelve `{seccion: {clave: "descripción [unidad]"}}` y `--buscar` / `--listar`, `{total, entidades, grupos}`. |
| `consultar_ranking.py` | `campo`, `desc`, `unidad`, `periodo`, `grupo`, `orden`, `entidades_consultadas`, `entidades_con_dato`, `ranking` (`[{pos, entidad, codigo, valor, participacion_pct}]`), `valor_sistema_financiero`, `fuente`, `sin_dato_en_el_periodo`, `filtro`, `filtro_valor`, `nota_participacion`. |
| `consultar_historico.py` | `entidad`, `codigo`, `desde`, `hasta`, `fuente`, `pdfs`, `datos` (`{clave: {desc, unidad, serie, variacion, meses_sin_dato, nota}}`), `errores_fuente`. `variacion` trae `puntos` para % y veces, y `pct` para montos. |
| `consultar_ipc.py` | Siempre `fuente`, `archivo`, `pagina`, `ultimo_mes_publicado`, `unidad`. Un mes: `mes`, `datos` (`{"Nivel general": {mensual, interanual}, ...}`), `acumulada_anio_pct`. `--serie`: `serie`, `desde`, `hasta`, `datos` (`{periodo: {mensual, interanual}}`). `--acumulado`: `serie`, `desde`, `hasta`, `acumulada_pct`, `metodo`. `--ranking-divisiones`: `mes`, `nivel_general_mensual`, `divisiones_por_variacion_mensual`. |
| `consultar_pagos.py` | `fuente`, `archivo`, `pagina`, `edicion`. Con `--series`: `hojas` (`{hoja: [{serie, medidas, ultimo_mes}]}`). Con `--buscar`: `resultados` (`[{hoja, serie, mes, cantidad, monto, ticket_promedio, var_mensual_*_pct}]`, o `datos` por mes con `--meses`), `nota`. |

Ejemplo (`consultar_entidad.py Galicia --campo irr_tot pla --serie`, recortado):

```json
{
 "entidad": "BANCO DE GALICIA Y BUENOS AIRES S.A.",
 "codigo": 7,
 "tipo": "entidad",
 "fuente": "BCRA — Información de Entidades Financieras",
 "actualizado_a": "2026-07",
 "datos": {
  "irr_tot": {"valor": 9.13, "periodo": "2026-07", "unidad": "%",
              "desc": "Mora total: cartera irregular / financiaciones totales (A9)",
              "serie": {"2024-12": 1.83, "2025-12": 6.9, "2026-05": 8.94, "2026-06": 8.3, "2026-07": 9.13}},
  "pla": {"valor": 4930958, "periodo": "2026-06", "unidad": "cantidad",
          "desc": "Tarjetas de crédito (plásticos)",
          "serie": {"2023-12": 4223804, "2024-12": 4380291, "2025-12": 5014189, "2026-03": 4383666, "2026-06": 4930958}}
 }
}
```

Agregar una clave nueva al JSON es un cambio menor; renombrar o quitar una de esta tabla, o cambiar su tipo, es un cambio mayor.

---

## 5. Claves de los campos

Las claves son las mismas en `bcra_comun.CAMPOS`, en todos los scripts y en los dos idiomas del skill. La referencia completa, con descripción, unidad, frecuencia y rezago de cada una, está en [`skill/bcra-oraculo/references/diccionario.md`](../skill/bcra-oraculo/references/diccionario.md) (en inglés, [`dictionary.md`](../skill/bcra-oracle-en/references/dictionary.md)). La lista también sale de `python3 scripts/consultar_entidad.py --campos`.

| Sección | Frecuencia | Claves | Ejemplos |
|---|---|---|---|
| `indicadores` | mensual | 31 | `irr_tot`, `irr_cons`, `irr_com`, `prev_irr`, `roe`, `roa`, `apalancamiento`, `tasa_prest`, `tasa_dep`, `liq_amplia` |
| `balance` | mensual | 27 | `bA`, `bPr`, `bDe`, `bPN`, `bCA`, `bPF`, `bRes` (millones de pesos) |
| `cartera` | mensual | 33 | `tf_total`, `tf_s1` … `tf_s5`, `tf_irregular` (CALCULADO), `com_s3`, `con_part` |
| `adicional` | trimestral | 13 | `pla`, `tit`, `deb`, `cah`, `cc`, `emp`, `pf_ind` |
| `remuneraciones` | mensual | 2 | `remu`, `remu_emp` |
| `sucursales` | foto al mes de actualización | 11 | `sucursales` (CALCULADO), `cajeros`, `suc_plenas`, `suc_exterior` |

`tools/verificar.py` comprueba que todas las claves de `CAMPOS` estén documentadas en los dos diccionarios.

---

## 6. Política de versiones

`bcra_comun.VERSION` sigue [versionado semántico](https://semver.org/lang/es/) y es la versión del skill entero. Cada versión publicada tiene su tag (`v2.0.0`) y su release en GitHub con los dos `.skill`.

| Cambio | Versión | Ejemplos |
|---|---|---|
| **Mayor** (3.0.0) | rompe a quien depende del módulo | cambia la firma de una función pública o lo que devuelve; se renombra o elimina una clave de campo; cambia la unidad o el significado de un campo; se renombra o elimina una clave del JSON de la sección 4; cambia la jerarquía de excepciones |
| **Menor** (2.1.0) | agrega sin romper | una función, un campo, una clave del JSON, un script o una opción nueva |
| **Parche** (2.0.1) | corrige sin cambiar la interfaz | adaptar el parseo a un cambio de formato del BCRA o del INDEC, cambiar una URL, corregir un error |

Reglas:

1. **Todo cambio en una firma o una clave sube la versión mayor y se registra en [`CHANGELOG.md`](../CHANGELOG.md)**, diciendo qué tienen que cambiar los skills que dependen.
2. `bcra_comun.py` es idéntico en `skill/bcra-oraculo/` y `skill/bcra-oracle-en/`. Se cambia en los dos a la vez, con la misma `VERSION`.
3. Antes de publicar, `python3 tools/verificar.py` tiene que pasar entero.
4. Un skill que depende de `bcra-oraculo` controla la versión mayor al importar (sección 1) y, si incluye una copia, dice qué versión copió.
