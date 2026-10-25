#!/usr/bin/env python3
"""
Datos de UNA entidad financiera (o de un grupo: sistema, públicos, privados,
compañías financieras, 10 primeros privados) desde la API oficial del BCRA.

Uso (de más común a menos):
    python3 consultar_entidad.py Galicia                     # resumen: balance, mora, ROE, tarjetas, sucursales
    python3 consultar_entidad.py Galicia --campo irr_tot roe # solo esos campos
    python3 consultar_entidad.py Nacion --seccion adicional  # tarjetas, cuentas, empleados
    python3 consultar_entidad.py Santander --seccion sucursales --provincias
    python3 consultar_entidad.py sistema --campo irr_tot pla # total del sistema financiero
    python3 consultar_entidad.py Macro --seccion ficha       # presidente, gerente, accionistas (usa el PDF)
    python3 consultar_entidad.py Galicia --serie             # todos los períodos publicados, no solo el último
    python3 consultar_entidad.py --buscar "provincia"        # buscar entidades por nombre
    python3 consultar_entidad.py --campos                    # catálogo de campos disponibles

Secciones: resumen (por defecto), indicadores, balance, cartera, adicional,
remuneraciones, sucursales, ficha, todo.

Cada valor sale con su período ("YYYY-MM"). null = celda vacía o '---' en la fuente.
NUNCA inventa: si un campo no está publicado, lo devuelve como null o lo informa.
"""
import argparse
import os
import sys

# Permite ejecutar el script desde cualquier carpeta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcra_comun as bc  # noqa: E402

RESUMEN = ['bA', 'bPr', 'bDe', 'bPN', 'irr_tot', 'irr_cons', 'irr_com', 'prev_irr', 'roe',
           'roa', 'apalancamiento', 'cah', 'pla', 'deb', 'emp', 'sucursales', 'cajeros']
SECCIONES_VALIDAS = ['resumen', 'indicadores', 'balance', 'cartera', 'adicional',
                     'remuneraciones', 'sucursales', 'ficha', 'todo']


def campos_de(seccion):
    return [k for k, v in bc.CAMPOS.items() if v[0] == seccion]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('entidad', nargs='?', help='Nombre, alias, código BCRA o grupo')
    ap.add_argument('--seccion', nargs='+', default=None, choices=SECCIONES_VALIDAS)
    ap.add_argument('--campo', nargs='+', help='Claves de campo (ver --campos)')
    ap.add_argument('--serie', action='store_true', help='Todos los períodos publicados')
    ap.add_argument('--provincias', action='store_true', help='Sucursales y cajeros por provincia')
    ap.add_argument('--filas', action='store_true', help='Balance completo con títulos originales')
    ap.add_argument('--buscar', metavar='TEXTO', help='Listar entidades cuyo nombre contenga TEXTO')
    ap.add_argument('--listar', action='store_true', help='Listar todas las entidades vigentes')
    ap.add_argument('--campos', action='store_true', help='Catálogo de campos')
    a = ap.parse_args()

    if a.campos:
        salida_campos = {}
        for k, (sec, desc, unidad, _) in bc.CAMPOS.items():
            salida_campos.setdefault(sec, {})[k] = '%s [%s]' % (desc, unidad)
        bc.salida(salida_campos)
        return

    if a.listar or a.buscar:
        ents = bc.nomina()
        if a.buscar:
            t = bc.norm(a.buscar)
            ents = [e for e in ents if t in bc.norm(e['nombre'])]
        bc.salida({'total': len(ents), 'entidades': ents,
                   'grupos': {k: v[1] for k, v in bc.GRUPOS.items()}})
        return

    if not a.entidad:
        ap.error('Indicar la entidad (o usar --buscar / --listar / --campos)')

    ent = bc.resolver(a.entidad)

    # Qué campos y secciones hacen falta
    secciones = set(a.seccion or ([] if a.campo else ['resumen']))
    pedidos = list(a.campo or [])
    desconocidos = [k for k in pedidos if k not in bc.CAMPOS]
    if desconocidos:
        raise bc.ErrorFuente('Campo(s) desconocido(s): %s. Ver --campos.' % ', '.join(desconocidos))
    if 'todo' in secciones:
        secciones = {'indicadores', 'balance', 'cartera', 'adicional', 'remuneraciones',
                     'sucursales', 'ficha'}
    if 'resumen' in secciones:
        secciones.discard('resumen')
        pedidos += [k for k in RESUMEN if k not in pedidos]
    for s in secciones - {'ficha'}:
        pedidos += [k for k in campos_de(s) if k not in pedidos]
    secs_api = {bc.CAMPOS[k][0] for k in pedidos}
    if a.provincias:
        secs_api.add('sucursales')
    if a.filas:
        secs_api.add('balance')

    out = {'entidad': ent['nombre'], 'codigo': ent['codigo'], 'tipo': ent['tipo']}
    if secs_api:
        datos = bc.consultar(ent['api'], secs_api)
        if len(datos.get('nombre_fuente') or '') > len(out['entidad']):
            out['entidad'] = datos['nombre_fuente']
        out['fuente'] = 'BCRA — Información de Entidades Financieras'
        out['actualizado_a'] = datos['actualizado']
        out['consulta_web'] = sorted({bc.PAGINA_WEB[bc.ENDPOINT_DE[s]].format(c=ent['api'])
                                      for s in secs_api})
        res = {}
        sin_dato = []
        for k in pedidos:
            serie = datos['campos'].get(k)
            info = bc.describir(k)
            if not serie or all(v is None for v in serie.values()):
                sin_dato.append(k)
                continue
            p, v = bc.ultimo_valor(serie)
            item = {'valor': v, 'periodo': p, 'unidad': info['unidad'], 'desc': info['desc']}
            if a.serie:
                item['serie'] = {per: serie[per] for per in sorted(serie)}
            res[k] = item
        out['datos'] = res
        if sin_dato:
            out['sin_dato_publicado'] = sin_dato
        if a.provincias and 'por_provincia' in datos['extra']:
            out['por_provincia'] = datos['extra']['por_provincia']
            out['por_provincia_periodo'] = datos['actualizado_por_seccion'].get('adicional')
        if 'exterior' in datos['extra'] and (a.provincias or 'sucursales' in secciones):
            out['exterior'] = datos['extra']['exterior']
        if 'composicion_sistema' in datos['extra']:
            out['composicion_sistema'] = datos['extra']['composicion_sistema']
        if a.filas:
            out['balance_completo_millones'] = datos['extra'].get('filas_balance')
        if datos['extra'].get('errores'):
            out['errores_fuente'] = datos['extra']['errores']
        out['nota'] = ('Montos de balance en millones de pesos corrientes; cartera en millones '
                       'de pesos; indicadores en %. Información adicional (tarjetas, cuentas, '
                       'empleados) es trimestral: su período puede ser anterior al del balance.')

    if 'ficha' in secciones:
        out['ficha'] = ficha(ent, out.get('actualizado_a'))

    bc.salida(out)


def ficha(ent, actualizado):
    """Directivos, accionistas y auditor: solo están en el PDF mensual."""
    if ent['tipo'] != 'entidad':
        return {'error': 'La ficha institucional existe solo para entidades, no para grupos'}
    if not bc.hay_pdftotext():
        return {'error': 'Falta pdftotext (poppler-utils) para leer el PDF con la ficha '
                         'institucional. Instalar: apt-get install -y poppler-utils'}
    if not actualizado:
        actualizado = bc.consultar(ent['api'], {'indicadores'})['actualizado']
    ultimo_error = None
    for ym in [actualizado, bc.mes_anterior(actualizado)]:
        try:
            ruta = bc.pdf_entidades(ym)
            texto, pag = bc.paginas_entidad_pdf(ruta, ent)
            f = bc.ficha_pdf(texto)
            f['periodo'] = ym
            f['fuente'] = bc.PDF_ENTIDADES.format(ym=ym.replace('-', '')) + ' (pág. %d)' % pag
            return f
        except bc.NoEncontrado as e:
            ultimo_error = e
    return {'error': 'No se encontró el PDF mensual: %s' % ultimo_error}


if __name__ == '__main__':
    bc.ejecutar(main)
