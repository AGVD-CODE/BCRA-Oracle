#!/usr/bin/env python3
"""
Medios de pago (Informe Mensual de Pagos Minoristas del BCRA, XLSX).

Busca solo el último archivo publicado, lo lee con la biblioteca estándar
(sin openpyxl) y calcula el ticket promedio (monto / cantidad).

Uso:
    python3 consultar_pagos.py --series                         # catálogo de series y último mes de cada una
    python3 consultar_pagos.py --buscar "tarjetas de crédito"   # último mes + variación mensual + ticket
    python3 consultar_pagos.py --buscar transferencias --hoja "Transferencias de fondos"
    python3 consultar_pagos.py --buscar echeq --meses 12        # serie mensual
    python3 consultar_pagos.py --buscar "débito" --mes 2026-06
    python3 consultar_pagos.py --archivo /ruta/local.xlsx --series   # usar un archivo ya descargado

Montos: pesos nominales (o la moneda que indique la serie). Ticket = monto / cantidad (CALCULADO).
"""
import argparse
import datetime as dt
import io
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

# Permite ejecutar el script desde cualquier carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcra_comun as bc  # noqa: E402

URL = ('https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Informes/'
       'series-informe-mensual-pagos-minoristas-{ym}.xlsx')
PAGINA = 'https://www.bcra.gob.ar/informe-de-pagos-minoristas/'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}


# ---------------------------------------------------------------------------
# Descarga del último archivo
# ---------------------------------------------------------------------------

def ultimo_archivo(meses_atras=5):
    hoy = dt.date.today()
    actual = '%04d-%02d' % (hoy.year, hoy.month)
    candidatos = [bc.mes_anterior(actual, i) for i in range(meses_atras + 1)]

    def bajar(ym):
        return bc.descargar(URL.format(ym=ym), validar=lambda b: b[:2] == b'PK')

    for ym, r in bc.en_paralelo(bajar, candidatos, workers=6):
        if not isinstance(r, Exception):
            return ym, r
    raise bc.ErrorFuente('No se encontró el XLSX de Pagos Minoristas de los últimos %d meses '
                         '(¿cambió la URL?). Ver %s' % (meses_atras + 1, PAGINA))


# ---------------------------------------------------------------------------
# Lector mínimo de XLSX
# ---------------------------------------------------------------------------

def _col(ref):
    letras = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letras:
        n = n * 26 + ord(ch) - 64
    return n - 1


def _rango(ref):
    a, b = ref.split(':')
    fa, fb = int(re.sub(r'[A-Z]', '', a)), int(re.sub(r'[A-Z]', '', b))
    return fa - 1, _col(a), fb - 1, _col(b)


def leer_xlsx(datos):
    """Devuelve {hoja: matriz de celdas} (fechas como serial numérico)."""
    z = zipfile.ZipFile(io.BytesIO(datos))
    compartidas = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            compartidas.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    rels = {r.get('Id'): r.get('Target') for r in
            ET.fromstring(z.read('xl/_rels/workbook.xml.rels')).findall('rel:Relationship', NS)}
    hojas = {}
    for h in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', NS):
        destino = rels[h.get('{%s}id' % NS['r'])].lstrip('/')
        ruta = destino if destino.startswith('xl/') else 'xl/' + destino
        raiz = ET.fromstring(z.read(ruta))
        celdas = {}
        for c in raiz.iter('{%s}c' % NS['m']):
            ref, t = c.get('r'), c.get('t')
            v = c.find('m:v', NS)
            if t == 's' and v is not None:
                val = compartidas[int(v.text)]
            elif t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
            elif v is not None and v.text is not None:
                if t in ('str', 'e'):
                    val = v.text
                else:
                    try:
                        val = float(v.text)
                    except ValueError:
                        val = v.text
            else:
                continue
            fila = int(re.sub(r'[A-Z]', '', ref)) - 1
            celdas[(fila, _col(ref))] = val
        # Celdas combinadas: replicar el valor de la esquina superior izquierda
        mc = raiz.find('m:mergeCells', NS)
        if mc is not None:
            for m in mc:
                f0, c0, f1, c1 = _rango(m.get('ref'))
                if (f0, c0) in celdas:
                    for f in range(f0, f1 + 1):
                        for col in range(c0, c1 + 1):
                            celdas.setdefault((f, col), celdas[(f0, c0)])
        hojas[h.get('name')] = celdas
    return hojas


def _ym_excel(v):
    if isinstance(v, float) and v > 20000:
        d = dt.date(1899, 12, 30) + dt.timedelta(days=int(v))
        return '%04d-%02d' % (d.year, d.month)
    return None


def series_de_hoja(celdas):
    """Arma series {nombre: {'cantidad': {ym: v}, 'monto': {...}, 'otras': {...}}}."""
    if not celdas:
        return {}
    filas = max(f for f, _ in celdas) + 1
    cols = max(c for _, c in celdas) + 1
    fila_fecha = next((f for f in range(min(filas, 10))
                       if any(str(celdas.get((f, c), '')).strip() == 'Fecha' for c in range(cols))),
                      None)
    if fila_fecha is None:
        return {}
    cols_fecha = [c for c in range(cols) if str(celdas.get((fila_fecha, c), '')).strip() == 'Fecha']
    # Primera fila con datos: todo lo anterior es encabezado (puede haber una
    # fila de "Cantidad / Monto" debajo de la fila "Fecha").
    primera = next((f for f in range(fila_fecha + 1, filas)
                    if any(_ym_excel(celdas.get((f, cf))) for cf in cols_fecha)), filas)
    series = {}
    anterior = (None, None)  # (nombre, tipo) de la columna previa
    for c in range(cols):
        if c in cols_fecha:
            anterior = (None, None)
            continue
        cf = max([x for x in cols_fecha if x < c], default=None)
        if cf is None:
            continue
        partes = []
        for f in range(primera):
            t = celdas.get((f, c))
            if isinstance(t, str):
                t = ' '.join(t.split())
                if t and t != 'Fecha' and t not in partes:
                    partes.append(t)
        medida = ''
        for p in reversed(partes):
            if re.match(r'(?i)^(cantidad|monto|saldo)', p):
                medida = p
                partes.remove(p)
                break
        if not medida and partes and re.search(r'(?i)\bmonto$', partes[-1]):
            medida = 'Monto'
        low = medida.lower()
        tipo = 'cantidad' if low.startswith('cantidad') else (
            'monto' if low.startswith('monto') or low.endswith('monto') else (low or 'valor'))
        nombre = ' / '.join(partes)
        # Columna de monto (o saldo) cuyo encabezado no repite el del grupo:
        # pertenece a la serie de la columna de cantidad que la precede.
        if tipo != 'cantidad' and anterior[1] == 'cantidad' and tipo not in series.get(anterior[0], {}):
            nombre = anterior[0]
        if not nombre:
            continue
        destino = series.setdefault(nombre, {})
        valores = destino.setdefault(tipo, {})
        for f in range(primera, filas):
            ym = _ym_excel(celdas.get((f, cf)))
            v = celdas.get((f, c))
            if ym and isinstance(v, float):
                valores[ym] = v
        anterior = (nombre, tipo)
    return {k: v for k, v in series.items() if any(v.values())}


def resumen_serie(s, ym=None):
    """Último mes (o el pedido) con cantidad, monto, ticket y variación mensual."""
    meses = sorted(set().union(*[set(x) for x in s.values()]))
    if not meses:
        return None
    if ym is None:
        ym = meses[-1]
    if ym not in meses:
        return {'mes': ym, 'sin_dato': True}
    prev = bc.mes_anterior(ym)
    out = {'mes': ym}
    for k, serie in s.items():
        if ym in serie:
            out[k] = round(serie[ym], 2)
            if serie.get(prev):
                out['var_mensual_%s_pct' % k] = round(100.0 * (serie[ym] / serie[prev] - 1), 2)
    cant, monto = s.get('cantidad', {}), s.get('monto', {})
    if cant.get(ym) and monto.get(ym):
        out['ticket_promedio'] = round(monto[ym] / cant[ym], 2)
        if cant.get(prev) and monto.get(prev):
            tp = monto[prev] / cant[prev]
            out['var_mensual_ticket_pct'] = round(100.0 * (out['ticket_promedio'] / tp - 1), 2)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--series', action='store_true', help='Catálogo de series')
    ap.add_argument('--buscar', help='Texto a buscar en el nombre de la serie (sin importar acentos)')
    ap.add_argument('--hoja', help='Limitar a una hoja')
    ap.add_argument('--mes', help='YYYY-MM')
    ap.add_argument('--meses', type=int, help='Devolver la serie de los últimos N meses')
    ap.add_argument('--archivo', help='XLSX local en lugar de descargar')
    a = ap.parse_args()

    if a.archivo:
        with open(a.archivo, 'rb') as f:
            datos = f.read()
        ym_arch, origen = None, a.archivo
    else:
        ym_arch, datos = ultimo_archivo()
        origen = URL.format(ym=ym_arch)
    hojas = leer_xlsx(datos)
    base = {'fuente': 'BCRA — Informe Mensual de Pagos Minoristas', 'archivo': origen,
            'pagina': PAGINA, 'edicion': ym_arch}

    todas = {}
    for h, celdas in hojas.items():
        if a.hoja and bc.norm(a.hoja) != bc.norm(h):
            continue
        for nombre, s in series_de_hoja(celdas).items():
            todas[(h, nombre)] = s
    if a.hoja and not todas:
        raise bc.ErrorFuente('Hoja inexistente: %s. Hojas: %s' % (a.hoja, ', '.join(hojas)))

    if a.buscar:
        t = bc.norm(a.buscar)
        todas = {k: v for k, v in todas.items() if t in bc.norm(k[0] + ' ' + k[1])}
        if not todas:
            raise bc.ErrorFuente('Ninguna serie contiene "%s". Usar --series para ver el catálogo'
                                 % a.buscar)

    if a.series or not a.buscar:
        cat = {}
        for (h, nombre), s in todas.items():
            ultimo = max((max(x) for x in s.values() if x), default=None)
            cat.setdefault(h, []).append({'serie': nombre, 'medidas': sorted(s), 'ultimo_mes': ultimo})
        base['hojas'] = cat
        bc.salida(base)
        return

    res = []
    for (h, nombre), s in todas.items():
        item = {'hoja': h, 'serie': nombre}
        if a.meses:
            meses = sorted(set().union(*[set(x) for x in s.values()]))[-a.meses:]
            item['datos'] = {}
            for m in meses:
                fila = {k: round(v[m], 2) for k, v in s.items() if m in v}
                if s.get('cantidad', {}).get(m) and s.get('monto', {}).get(m):
                    fila['ticket_promedio'] = round(s['monto'][m] / s['cantidad'][m], 2)
                item['datos'][m] = fila
        else:
            item.update(resumen_serie(s, a.mes) or {})
        res.append(item)
    base['resultados'] = res
    base['nota'] = ('Cada hoja tiene su propio rezago: el último mes puede variar por serie. '
                    'ticket_promedio y var_* son CALCULADOS (monto / cantidad; variación vs. mes anterior). '
                    'Montos nominales, sin ajustar por inflación.')
    bc.salida(base)


if __name__ == '__main__':
    bc.ejecutar(main)
