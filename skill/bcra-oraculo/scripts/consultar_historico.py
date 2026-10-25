#!/usr/bin/env python3
"""
Serie mensual de un campo para una entidad (o grupo) a partir de los PDF
mensuales "Información de Entidades Financieras" del BCRA.

Usar solo cuando la pregunta pide más historia que la que trae
consultar_entidad.py --serie (la API publica 5 columnas: los 2 últimos
diciembres y los 3 últimos meses). Requiere pdftotext (poppler-utils).

Uso:
    python3 consultar_historico.py Galicia --campo irr_tot                 # últimos 12 meses
    python3 consultar_historico.py Galicia --campo irr_tot roe --meses 24
    python3 consultar_historico.py Nacion --campo bDe --desde 2025-01 --hasta 2026-06
    python3 consultar_historico.py sistema --campo irr_tot irr_cons

Cada PDF trae 3 meses consecutivos más 2 diciembres, así que se descarga
un PDF cada 3 meses (12 meses = 4 PDF). Se procesan solo las páginas de la
entidad, no el documento completo. Si el último PDF es de un mes de cierre de
trimestre y trae vacía la información adicional de ese trimestre, se lee
también el del mes siguiente, que la completa.

Historia: completa desde 2014. En 2011-2013 faltan los indicadores de mora
(el BCRA usaba otros códigos y no se informan para no confundirlos). Los PDF
de 2010 y anteriores no se pueden leer. Solo funciona para entidades vigentes
hoy; las que cambiaron de nombre se encuentran igual, porque se ubican por código.
"""
import argparse
import os
import sys

# Permite ejecutar el script desde cualquier carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcra_comun as bc  # noqa: E402

SECCIONES_PDF = {'indicadores', 'balance', 'cartera', 'adicional', 'remuneraciones'}


def meses_entre(desde, hasta):
    out, m = [], hasta
    while m >= desde:
        out.append(m)
        m = bc.mes_anterior(m)
    return out[::-1]


def mes_siguiente(ym):
    a, m = int(ym[:4]), int(ym[5:7])
    return '%04d-%02d' % (a + m // 12, m % 12 + 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('entidad')
    ap.add_argument('--campo', nargs='+', required=True)
    ap.add_argument('--meses', type=int, default=12)
    ap.add_argument('--desde', help='YYYY-MM')
    ap.add_argument('--hasta', help='YYYY-MM (por defecto, el último publicado)')
    a = ap.parse_args()

    for k in a.campo:
        if k not in bc.CAMPOS:
            raise bc.ErrorFuente('Campo desconocido: %s. Ver consultar_entidad.py --campos' % k)
        if bc.CAMPOS[k][0] not in SECCIONES_PDF:
            raise bc.ErrorFuente('El campo %s (%s) no tiene serie histórica en el PDF; usar '
                                 'consultar_entidad.py' % (k, bc.CAMPOS[k][0]))
    bc.exigir_pdftotext()
    ent = bc.resolver(a.entidad)

    hasta = a.hasta or bc.consultar(ent['api'], {'indicadores'})['actualizado']
    desde = a.desde or bc.mes_anterior(hasta, max(1, a.meses) - 1)
    if desde > hasta:
        raise bc.ErrorFuente('--desde es posterior a --hasta')
    objetivo = meses_entre(desde, hasta)

    # Un PDF cubre su mes y los dos anteriores
    plan, cubiertos = [], set()
    for m in reversed(objetivo):
        if m not in cubiertos:
            plan.append(m)
            cubiertos.update({m, bc.mes_anterior(m), bc.mes_anterior(m, 2)})

    def leer(ym):
        ruta = bc.pdf_entidades(ym)
        texto, pag = bc.paginas_entidad_pdf(ruta, ent)
        r = bc.normalizar_pdf(texto)
        r['pdf'] = bc.PDF_ENTIDADES.format(ym=ym.replace('-', '')) + ' (pág. %d)' % pag
        r['ym'] = ym
        return r

    def procesar(ym):
        try:
            return leer(ym)
        except bc.NoEncontrado:
            return leer(bc.mes_anterior(ym))  # el mes pedido todavía no está publicado

    resultados = bc.en_paralelo(procesar, plan, workers=4)
    series = {k: {} for k in a.campo}
    pdfs, errores = [], []
    ok = [r for _, r in resultados if not isinstance(r, Exception)]
    for _, r in resultados:
        if isinstance(r, Exception):
            errores.append(str(r))

    # El PDF de un mes de cierre de trimestre suele traer ese trimestre vacío
    # ('---') en la información adicional; lo completa el PDF del mes siguiente.
    trimestrales = [k for k in a.campo if bc.CAMPOS[k][0] == 'adicional']
    sin_completar = None
    if ok and trimestrales:
        ultimo = max(ok, key=lambda x: x['ym'])
        m = ultimo['ym']
        if m[5:] in ('03', '06', '09', '12') and desde <= m and any(
                (ultimo['campos'].get(k) or {}).get(m) is None for k in trimestrales):
            try:
                ok.append(leer(mes_siguiente(m)))
            except bc.NoEncontrado:
                sin_completar = m
            except bc.ErrorFuente as e:
                errores.append(str(e))

    for r in sorted(ok, key=lambda x: x['ym']):  # el PDF más nuevo pisa revisiones
        pdfs.append(r['pdf'])
        for k in a.campo:
            for p, v in (r['campos'].get(k) or {}).items():
                if desde <= p <= hasta:
                    series[k][p] = v

    out = {'entidad': ent['nombre'], 'codigo': ent['codigo'], 'desde': desde, 'hasta': hasta,
           'fuente': 'BCRA — Información de Entidades Financieras (PDF mensual)',
           'pdfs': pdfs, 'datos': {}}
    for k in a.campo:
        info = bc.describir(k)
        serie = {p: series[k][p] for p in sorted(series[k])}
        item = {'desc': info['desc'], 'unidad': info['unidad'], 'serie': serie}
        con_dato = [(p, v) for p, v in serie.items() if v is not None]
        faltan = [m for m in objetivo if m not in serie and info['seccion'] not in
                  ('adicional',)]
        if len(con_dato) >= 2:
            (p0, v0), (p1, v1) = con_dato[0], con_dato[-1]
            if info['unidad'] in ('%', 'veces'):
                item['variacion'] = {'desde': p0, 'hasta': p1, 'puntos': round(v1 - v0, 2),
                                     'nota': 'CALCULADO: diferencia en puntos'}
            elif v0:
                item['variacion'] = {'desde': p0, 'hasta': p1,
                                     'pct': round(100.0 * (v1 / v0 - 1), 2),
                                     'nota': 'CALCULADO: variación nominal (sin ajustar por inflación)'}
        if faltan:
            item['meses_sin_dato'] = faltan
        if info['seccion'] == 'adicional':
            item['nota'] = 'Dato trimestral: solo hay valores a fin de cada trimestre.'
            if sin_completar and serie.get(sin_completar) is None:
                item['nota'] += (' El trimestre %s lo completa el PDF de %s, que todavía no '
                                 'está publicado.' % (sin_completar, mes_siguiente(sin_completar)))
        out['datos'][k] = item
    if errores:
        out['errores_fuente'] = errores
    bc.salida(out)


if __name__ == '__main__':
    bc.ejecutar(main)
