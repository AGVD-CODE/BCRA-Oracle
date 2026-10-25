#!/usr/bin/env python3
"""
Inflación (IPC Nacional, INDEC) desde el CSV oficial de series, que tiene
URL fija y siempre trae el último mes publicado. Solo biblioteca estándar.

Uso:
    python3 consultar_ipc.py                           # último mes: general, núcleo, regulados, estacional, bienes, servicios y 12 divisiones
    python3 consultar_ipc.py --mes 2026-06             # un mes específico
    python3 consultar_ipc.py --serie nivel --desde 2025-10   # serie mensual (variación mensual e interanual)
    python3 consultar_ipc.py --serie vivienda --meses 12
    python3 consultar_ipc.py --acumulado 2026          # acumulada del año (hasta el último mes publicado)
    python3 consultar_ipc.py --acumulado --desde 2025-07 --hasta 2026-06   # acumulada entre meses (inclusive)
    python3 consultar_ipc.py --ranking-divisiones      # qué rubro subió más el último mes
    python3 consultar_ipc.py --region GBA              # regiones: Nacional, GBA, Pampeana, Noreste, Noroeste, Cuyo, Patagonia

Series: nivel (nivel general), nucleo, regulados, estacional, bienes, servicios,
o una división por código (01..12) o nombre (alimentos, vivienda, salud, transporte...).

Las acumuladas se calculan con el índice (cociente de índices), igual que el INDEC.
"""
import argparse
import csv
import io
import os
import sys

# Permite ejecutar el script desde cualquier carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcra_comun as bc  # noqa: E402

URL = 'https://www.indec.gob.ar/ftp/cuadros/economia/serie_ipc_divisiones.csv'
PAGINA = 'https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31'
BASICAS = {'nivel': '0', 'nucleo': 'Núcleo', 'regulados': 'Regulados',
           'estacional': 'Estacional', 'bienes': 'B', 'servicios': 'S'}
NOMBRES = {'0': 'Nivel general', 'Núcleo': 'Núcleo', 'Regulados': 'Regulados',
           'Estacional': 'Estacional', 'B': 'Bienes', 'S': 'Servicios'}
REGIONES = ['Nacional', 'GBA', 'Pampeana', 'Noreste', 'Noroeste', 'Cuyo', 'Patagonia']


def cargar(region):
    datos = bc.descargar(URL, validar=lambda b: b[:6] == b'Codigo')
    texto = datos.decode('latin-1')
    series, nombres = {}, dict(NOMBRES)
    for r in csv.DictReader(io.StringIO(texto), delimiter=';'):
        if r.get('Region') != region:
            continue
        cod = r['Codigo'].strip()
        per = r['Periodo'].strip()
        ym = '%s-%s' % (per[:4], per[4:6])
        if r.get('Descripcion') and cod not in NOMBRES:
            nombres[cod] = r['Descripcion'].strip()
        series.setdefault(cod, {})[ym] = {
            'indice': bc.num_ar(r['Indice_IPC']), 'mensual': bc.num_ar(r['v_m_IPC']),
            'interanual': bc.num_ar(r['v_i_a_IPC'])}
    if not series:
        raise bc.ErrorFuente('El CSV del INDEC no trae datos para la región %s' % region)
    return series, nombres


def resolver_serie(q, nombres):
    nq = bc.norm(q)
    alias = {bc.norm(k): v for k, v in BASICAS.items()}
    alias.update({'GENERAL': '0', 'NIVEL GENERAL': '0', 'INFLACION': '0', 'CORE': 'Núcleo'})
    if nq in alias:
        return alias[nq]
    for cod, nom in nombres.items():
        if nq == bc.norm(cod) or nq == bc.norm(nom) or (len(nq) >= 4 and nq in bc.norm(nom)):
            return cod
    raise bc.ErrorFuente('Serie desconocida: %s. Opciones: %s' % (
        q, ', '.join(list(BASICAS) + ['%s (%s)' % (c, n) for c, n in sorted(nombres.items())
                                      if c[:1].isdigit() and c != '0'])))


def fila_mes(series, nombres, ym):
    out = {}
    primeras = ['0', 'Núcleo', 'Regulados', 'Estacional', 'B', 'S']
    divisiones = sorted(c for c in series if c[:1].isdigit() and c != '0')
    for cod in primeras + divisiones:
        if cod not in series:
            continue
        d = series[cod].get(ym)
        if d:
            out[nombres.get(cod, cod)] = {'mensual': d['mensual'], 'interanual': d['interanual']}
    return out


def acumulada(serie, desde, hasta):
    """Variación % entre el índice de 'hasta' y el del mes anterior a 'desde'."""
    base = serie.get(bc.mes_anterior(desde), {}).get('indice')
    fin = serie.get(hasta, {}).get('indice')
    if not base or not fin:
        return None
    return round(100.0 * (fin / base - 1), 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--mes', help='YYYY-MM')
    ap.add_argument('--serie')
    ap.add_argument('--desde')
    ap.add_argument('--hasta')
    ap.add_argument('--meses', type=int)
    ap.add_argument('--acumulado', nargs='?', const='rango', metavar='AÑO')
    ap.add_argument('--ranking-divisiones', action='store_true')
    ap.add_argument('--region', default='Nacional', choices=REGIONES)
    a = ap.parse_args()

    series, nombres = cargar(a.region)
    general = series['0']
    ultimo = max(p for p, d in general.items() if d['mensual'] is not None)
    base = {'fuente': 'INDEC — Índice de Precios al Consumidor (IPC), región ' + a.region,
            'archivo': URL, 'pagina': PAGINA, 'ultimo_mes_publicado': ultimo, 'unidad': '%'}

    if a.acumulado:
        cod = resolver_serie(a.serie, nombres) if a.serie else '0'
        s = series[cod]
        if a.acumulado != 'rango':
            anio = a.acumulado
            desde = '%s-01' % anio
            hasta = min('%s-12' % anio, ultimo)
        else:
            if not a.desde:
                raise bc.ErrorFuente('Indicar --desde (y opcionalmente --hasta) o un año')
            desde, hasta = a.desde, a.hasta or ultimo
        v = acumulada(s, desde, hasta)
        if v is None:
            raise bc.ErrorFuente('No hay índice publicado para %s a %s' % (desde, hasta))
        base.update({'serie': nombres.get(cod, cod), 'desde': desde, 'hasta': hasta,
                     'acumulada_pct': v,
                     'metodo': 'CALCULADO: índice de %s / índice de %s - 1' % (
                         hasta, bc.mes_anterior(desde))})
        if hasta < '%s-12' % desde[:4] and a.acumulado != 'rango':
            base['nota'] = 'Año incompleto: acumulada de enero a %s' % hasta
        bc.salida(base)
        return

    if a.serie:
        cod = resolver_serie(a.serie, nombres)
        s = series[cod]
        hasta = a.hasta or ultimo
        desde = a.desde or bc.mes_anterior(hasta, (a.meses or 12) - 1)
        base.update({'serie': nombres.get(cod, cod), 'desde': desde, 'hasta': hasta,
                     'datos': {p: {'mensual': s[p]['mensual'], 'interanual': s[p]['interanual']}
                               for p in sorted(s) if desde <= p <= hasta}})
        bc.salida(base)
        return

    ym = a.mes or ultimo
    if ym not in general:
        raise bc.ErrorFuente('El INDEC no publicó el IPC de %s. Último disponible: %s' % (ym, ultimo))

    if a.ranking_divisiones:
        divs = [(nombres[c], series[c][ym]['mensual'], series[c][ym]['interanual'])
                for c in series if c[:1].isdigit() and c != '0' and ym in series[c]]
        divs.sort(key=lambda x: -(x[1] if x[1] is not None else -999))
        base.update({'mes': ym, 'nivel_general_mensual': general[ym]['mensual'],
                     'divisiones_por_variacion_mensual': [
                         {'pos': i, 'division': n, 'mensual': m, 'interanual': ia}
                         for i, (n, m, ia) in enumerate(divs, 1)]})
        bc.salida(base)
        return

    base.update({'mes': ym, 'datos': fila_mes(series, nombres, ym),
                 'acumulada_anio_pct': acumulada(general, '%s-01' % ym[:4], ym),
                 'nota': 'mensual = variación contra el mes anterior; interanual = contra el mismo '
                         'mes del año anterior; acumulada_anio_pct = enero a %s (CALCULADO con el '
                         'índice).' % ym})
    bc.salida(base)


if __name__ == '__main__':
    bc.ejecutar(main)
