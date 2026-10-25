#!/usr/bin/env python3
"""
Ranking de entidades por cualquier campo, consultando a todas en paralelo
(API oficial del BCRA, ~2-4 s para las 60 entidades bancarias).

Uso:
    python3 consultar_ranking.py irr_tot                      # top 10 bancos por mora
    python3 consultar_ranking.py pla --top 5 --participacion  # tarjetas de crédito + cuota de mercado
    python3 consultar_ranking.py sucursales --top 10
    python3 consultar_ranking.py roe --asc --top 5            # los 5 de menor ROE
    python3 consultar_ranking.py irr_tot --entre-mayores 20   # mora solo entre los 20 bancos más grandes por activo
    python3 consultar_ranking.py irr_tot --mayor-que 10       # cuántos y cuáles superan 10 %
    python3 consultar_ranking.py bA --grupo todas --todos     # todas las entidades (incluye compañías financieras)

Grupos: bancos (por defecto: públicos + privados), publicos, privados,
companias (compañías financieras), top10, todas.

Los campos son los mismos de consultar_entidad.py --campos.
NUNCA inventa: las entidades sin dato para el período se listan aparte.
"""
import argparse
import os
import sys

# Permite ejecutar el script desde cualquier carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcra_comun as bc  # noqa: E402

GRUPOS_RANKING = {
    'bancos': ['AAA10', 'AAA20'], 'publicos': ['AAA10'], 'privados': ['AAA20'],
    'companias': ['AAA30'], 'top10': ['AAA50'], 'todas': ['AAA00'],
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('campo', help='Clave del campo (ver consultar_entidad.py --campos)')
    ap.add_argument('--top', type=int, help='Cantidad a mostrar (10 por defecto; todas si se filtra por valor)')
    ap.add_argument('--todos', action='store_true', help='Listar todas las entidades')
    ap.add_argument('--asc', action='store_true', help='Orden ascendente (de menor a mayor)')
    ap.add_argument('--grupo', default='bancos', choices=sorted(GRUPOS_RANKING))
    ap.add_argument('--periodo', help='YYYY-MM (por defecto, el último publicado)')
    ap.add_argument('--participacion', action='store_true',
                    help='Agregar participación %% sobre el total del sistema (campos sumables)')
    ap.add_argument('--entre-mayores', type=int, metavar='N',
                    help='Limitar a las N entidades de mayor activo')
    ap.add_argument('--mayor-que', type=float, metavar='X', help='Filtrar valores > X')
    ap.add_argument('--menor-que', type=float, metavar='X', help='Filtrar valores < X')
    a = ap.parse_args()

    if a.campo not in bc.CAMPOS:
        raise bc.ErrorFuente('Campo desconocido: %s. Ver consultar_entidad.py --campos' % a.campo)
    seccion, desc, unidad, aditivo = bc.CAMPOS[a.campo]

    # Entidades del grupo
    ents = {}
    for g in GRUPOS_RANKING[a.grupo]:
        for e in bc.nomina(g):
            ents[e['codigo']] = e
    if not ents:
        raise bc.ErrorFuente('El grupo %s no tiene entidades en la nómina vigente' % a.grupo)

    secs = {seccion}
    if a.entre_mayores:
        secs.add('balance')

    def traer(cod):
        return bc.consultar(bc.codigo_api(cod), secs)

    resultados = bc.en_paralelo(traer, list(ents) + ['AAA00'])
    sistema = None
    filas, errores = [], []
    for cod, r in resultados:
        if cod == 'AAA00':
            sistema = r if not isinstance(r, Exception) else None
            continue
        if isinstance(r, Exception):
            errores.append({'codigo': cod, 'nombre': ents[cod]['nombre'], 'error': str(r)})
            continue
        filas.append((cod, r))

    # Período: el pedido o el último con datos en el sistema / en las entidades
    periodo = a.periodo
    if not periodo:
        candidatos = []
        if sistema and sistema['campos'].get(a.campo):
            candidatos.append(bc.ultimo_valor(sistema['campos'][a.campo])[0])
        for _, r in filas:
            p, _v = bc.ultimo_valor(r['campos'].get(a.campo) or {})
            if p:
                candidatos.append(p)
        if not candidatos:
            raise bc.ErrorFuente('Ninguna entidad publica el campo %s' % a.campo)
        periodo = max(candidatos)

    if a.entre_mayores:
        def activo(r):
            return (r['campos'].get('bA') or {}).get(periodo) or bc.ultimo_valor(
                r['campos'].get('bA') or {})[1] or 0
        filas.sort(key=lambda x: activo(x[1]), reverse=True)
        filas = filas[:a.entre_mayores]

    valores, sin_dato = [], []
    for cod, r in filas:
        v = (r['campos'].get(a.campo) or {}).get(periodo)
        nombre = r.get('nombre_fuente') if len(r.get('nombre_fuente') or '') > len(
            ents[cod]['nombre']) else ents[cod]['nombre']
        if v is None:
            sin_dato.append(nombre)
        else:
            valores.append({'entidad': nombre, 'codigo': cod, 'valor': v})

    con_dato = len(valores)
    filtrado = a.mayor_que is not None or a.menor_que is not None
    if a.mayor_que is not None:
        valores = [x for x in valores if x['valor'] > a.mayor_que]
    if a.menor_que is not None:
        valores = [x for x in valores if x['valor'] < a.menor_que]
    valores.sort(key=lambda x: x['valor'], reverse=not a.asc)

    total_sis = (sistema['campos'].get(a.campo) or {}).get(periodo) if sistema else None
    if a.participacion:
        if not aditivo:
            raise bc.ErrorFuente('La participación solo tiene sentido para campos sumables '
                                 '(montos y cantidades), no para %s (%s)' % (a.campo, unidad))
        if total_sis:
            for x in valores:
                x['participacion_pct'] = round(100.0 * x['valor'] / total_sis, 2)

    top = a.top or (len(valores) if filtrado else 10)
    lista = valores if a.todos else valores[:top]
    for i, x in enumerate(lista, 1):
        x['pos'] = i
    out = {
        'campo': a.campo, 'desc': desc, 'unidad': unidad, 'periodo': periodo,
        'grupo': a.grupo, 'orden': 'ascendente' if a.asc else 'descendente',
        'entidades_consultadas': len(filas), 'entidades_con_dato': con_dato,
        'ranking': [{'pos': x.pop('pos'), **x} for x in lista],
        'valor_sistema_financiero': total_sis,
        'fuente': 'BCRA — Información de Entidades Financieras (API oficial, consulta por entidad)',
    }
    if a.entre_mayores:
        out['filtro'] = 'Solo las %d entidades de mayor activo' % a.entre_mayores
    if filtrado:
        out['filtro_valor'] = {'mayor_que': a.mayor_que, 'menor_que': a.menor_que,
                               'entidades_que_cumplen': len(valores)}
    if sin_dato:
        out['sin_dato_en_el_periodo'] = sin_dato
    if errores:
        out['errores_fuente'] = errores
    if a.participacion and total_sis:
        out['nota_participacion'] = ('Participación = valor de la entidad / total del sistema '
                                     'financiero (incluye compañías financieras) x 100. CALCULADO.')
    bc.salida(out)


if __name__ == '__main__':
    bc.ejecutar(main)
