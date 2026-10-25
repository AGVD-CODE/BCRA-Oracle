#!/usr/bin/env python3
"""
Corre los valores de control del skill contra las fuentes oficiales y dice OK o
FALLA por cada uno (references/fuentes.md, sección 6).

    python3 tools/verificar.py              # todo: necesita red y pdftotext
    python3 tools/verificar.py --sin-cache  # descarga todo de nuevo (sin la caché de 2 horas)
    python3 tools/verificar.py --locales    # solo las comprobaciones que no usan la red

Usa los scripts del skill en español (skill/bcra-oraculo/scripts) y solo la
biblioteca estándar. Sale con código 1 si algo falla.

Qué comprueba:
- Locales: scripts idénticos y que compilan en los dos idiomas, misma VERSION en
  bcra_comun.py y todos los campos documentados en los diccionarios.
- Valores de control (publicaciones cerradas, no cambian): Galicia en el PDF de
  abril de 2026 e IPC nacional (noviembre de 2025, mayo de 2026, acumuladas de
  2024 y 2025).
- Valores de control heredados de la v1, del mismo PDF de abril de 2026:
  información adicional de Galicia a marzo de 2026, situación de deudores de
  Galicia y activo de los bancos (públicos + privados).
- API frente a PDF: Galicia, todos los campos de los meses que comparten.
- Los mismos valores de Galicia leídos con consultar_panel.py, y que el panel traiga
  los agregados oficiales.
- Funcionamiento en vivo de los 7 scripts: resumen, totales del sistema, nombre
  ambiguo, ranking, historia, panel, IPC, medios de pago y ficha institucional.

Si falta pdftotext: brew install poppler (macOS) o apt-get install -y poppler-utils.
"""
import argparse
import csv
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = ('bcra-oraculo', 'bcra-oracle-en')
SCRIPTS = os.path.join(RAIZ, 'skill', 'bcra-oraculo', 'scripts')
DICCIONARIOS = ('skill/bcra-oraculo/references/diccionario.md',
                'skill/bcra-oracle-en/references/dictionary.md')

# references/fuentes.md, sección 6. PDF de abril de 2026 (202604e.pdf), Banco Galicia (código 7)
GALICIA_ABRIL_2026 = {'irr_tot': 8.09, 'irr_cons': 16.17, 'irr_com': 3.32, 'roa': 0.04,
                      'apalancamiento': 4.3, 'tasa_prest': 32.4, 'bA': 36704435.9,
                      'bCA': 12339200.7}
# INDEC, nivel general nacional
IPC_MENSUAL = {'2025-11': 2.5, '2026-05': 2.1}
IPC_ACUMULADA = {'2024': 117.8, '2025': 31.5}

# Checksums de la v1 (diccionario.md, "Checksums de validación"), mismo PDF de abril de 2026
GALICIA_MARZO_2026_ADICIONAL = {'pla': 4383666, 'tit': 3094662, 'deb': 7533250,
                                'cah': 10316472, 'emp': 6025}
GALICIA_ABRIL_2026_CARTERA = {'tf_s1': 89.16, 'tf_s3': 2.62, 'tf_s4': 4.62, 'tf_s5': 0.85}
# "Sistema: 59 bancos, activo total ≈ 313,8 billones de pesos (abril 2026)"
BANCOS_ACTIVO_ABRIL_2026 = 313838752.9

resultados = []
entorno = dict(os.environ)


def registrar(nombre, ok, detalle=''):
    resultados.append((nombre, ok))
    print('%s %s%s' % ('OK   ' if ok else 'FALLA', nombre, ('  — ' + detalle) if detalle else ''))


def titulo(texto):
    print('\n== %s ==' % texto)


def correr(script, *args):
    """Corre un script del skill y devuelve (json, segundos)."""
    t = time.time()
    try:
        r = subprocess.run([sys.executable, '-B', os.path.join(SCRIPTS, script)] + list(args),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=900,
                           cwd=RAIZ, env=entorno)
    except subprocess.TimeoutExpired:
        return {'error': 'sin respuesta en 15 minutos'}, time.time() - t
    try:
        return json.loads(r.stdout.decode('utf-8')), time.time() - t
    except ValueError:
        return {'error': (r.stdout + r.stderr).decode('utf-8', 'replace')[-500:]}, time.time() - t


def error_de(d):
    if 'error' not in d:
        return None
    return d['error'] + (' (sin acceso a la red)' if d.get('sin_acceso_red') else '')


def mes_anterior(ym, n):
    total = int(ym[:4]) * 12 + int(ym[5:7]) - 1 - n
    return '%04d-%02d' % (total // 12, total % 12 + 1)


def decimales(v):
    s = repr(float(v))
    return len(s.split('.')[1]) if '.' in s and 'e' not in s else 0


def igual(obtenido, esperado):
    return isinstance(obtenido, (int, float)) and abs(obtenido - esperado) < 1e-6


def controlar(nombre, obtenido, esperado):
    if igual(obtenido, esperado):
        registrar('%s = %s' % (nombre, esperado), True)
    else:
        registrar(nombre, False, 'obtenido %s, esperado %s' % (obtenido, esperado))


def fallar_todos(etiqueta, esperados, motivo):
    for k in esperados:
        registrar('%s %s' % (etiqueta, k), False, motivo)


# ---------------------------------------------------------------------------
# Locales
# ---------------------------------------------------------------------------

def locales():
    titulo('Comprobaciones locales')
    distintos, no_compilan = [], []
    for skill in SKILLS:
        d = os.path.join(RAIZ, 'skill', skill, 'scripts')
        for f in sorted(os.listdir(d)):
            if f.endswith('.py'):
                ruta = os.path.join(d, f)
                try:
                    with open(ruta, encoding='utf-8') as fh:
                        compile(fh.read(), ruta, 'exec')
                except SyntaxError as e:
                    no_compilan.append('%s/%s: %s' % (skill, f, e))
    a, b = (os.path.join(RAIZ, 'skill', s, 'scripts') for s in SKILLS)
    nombres = sorted(set(os.listdir(a)) | set(os.listdir(b)))
    for f in nombres:
        if f == '__pycache__':
            continue
        if not (os.path.isfile(os.path.join(a, f)) and os.path.isfile(os.path.join(b, f))
                and filecmp.cmp(os.path.join(a, f), os.path.join(b, f), shallow=False)):
            distintos.append(f)
    registrar('scripts idénticos en los dos idiomas', not distintos, ', '.join(distintos))
    registrar('scripts compilan', not no_compilan, '; '.join(no_compilan))

    versiones = []
    for skill in SKILLS:
        with open(os.path.join(RAIZ, 'skill', skill, 'scripts', 'bcra_comun.py'),
                  encoding='utf-8') as fh:
            m = re.search(r'^VERSION = "(\d+\.\d+\.\d+)"$', fh.read(), re.M)
        versiones.append(m.group(1) if m else None)
    registrar('VERSION de bcra_comun.py', None not in versiones and len(set(versiones)) == 1,
              ' / '.join(str(v) for v in versiones))

    sys.path.insert(0, SCRIPTS)
    sys.dont_write_bytecode = True  # no dejar __pycache__ dentro del skill
    import bcra_comun as bc
    for ruta in DICCIONARIOS:
        with open(os.path.join(RAIZ, ruta), encoding='utf-8') as fh:
            texto = fh.read()
        # Las aperturas por situación de cada cartera (com_s1 ... cac_s5) van en una sola fila
        faltan = [k for k in bc.CAMPOS if '`%s`' % k not in texto and not re.fullmatch(
            r'(com|con|cac)_s\d', k)]
        registrar('campos documentados en ' + ruta, not faltan, ', '.join(faltan))


# ---------------------------------------------------------------------------
# Valores de control
# ---------------------------------------------------------------------------

def control_pdf_galicia():
    campos = list(GALICIA_ABRIL_2026) + list(GALICIA_ABRIL_2026_CARTERA) + \
        list(GALICIA_MARZO_2026_ADICIONAL)
    d, t = correr('consultar_historico.py', 'Galicia', '--campo', *campos,
                  '--desde', '2026-03', '--hasta', '2026-04')
    titulo('Valores de control: Galicia en el PDF de abril de 2026 (%.1f s)' % t)
    err = error_de(d)
    if not err and not any('202604e.pdf' in p for p in d.get('pdfs', [])):
        err = 'no se leyó 202604e.pdf (se leyó %s)' % d.get('pdfs')
    if err:
        fallar_todos('Galicia', GALICIA_ABRIL_2026, err)
    else:
        for k, v in GALICIA_ABRIL_2026.items():
            controlar('Galicia %s (2026-04)' % k, d['datos'][k]['serie'].get('2026-04'), v)

    titulo('Valores de control heredados de la v1: mismo PDF')
    if err:
        fallar_todos('Galicia', list(GALICIA_ABRIL_2026_CARTERA) +
                     list(GALICIA_MARZO_2026_ADICIONAL), err)
    else:
        for k, v in GALICIA_ABRIL_2026_CARTERA.items():
            controlar('Galicia %s (2026-04)' % k, d['datos'][k]['serie'].get('2026-04'), v)
        for k, v in GALICIA_MARZO_2026_ADICIONAL.items():
            controlar('Galicia %s (2026-03, trimestral)' % k,
                      d['datos'][k]['serie'].get('2026-03'), v)

    total, errores = 0.0, []
    for grupo in ('publicos', 'privados'):
        g, _ = correr('consultar_historico.py', grupo, '--campo', 'bA',
                      '--desde', '2026-04', '--hasta', '2026-04')
        v = None if error_de(g) else g['datos']['bA']['serie'].get('2026-04')
        if v is None:
            errores.append('%s: %s' % (grupo, error_de(g) or 'sin dato'))
        else:
            total += v
    if errores:
        registrar('activo de los bancos, públicos + privados (2026-04)', False, '; '.join(errores))
    else:
        controlar('activo de los bancos, públicos + privados (2026-04)', round(total, 1),
                  BANCOS_ACTIVO_ABRIL_2026)


def control_panel():
    """Los mismos valores de control de Galicia, leídos con consultar_panel.py (desde la 2.1.0)."""
    with tempfile.TemporaryDirectory() as tmp:
        ruta = os.path.join(tmp, 'panel.csv')
        d, t = correr('consultar_panel.py', '--entidades', 'Galicia', '--desde', '2026-04',
                      '--hasta', '2026-04', '--modo', 'pdf', '--campos', *GALICIA_ABRIL_2026,
                      '--salida', ruta)
        titulo('Valores de control: Galicia en el PDF de abril de 2026, con consultar_panel.py '
               '(%.1f s)' % t)
        err = error_de(d)
        filas = {}
        if not err:
            with open(ruta, newline='', encoding='utf-8') as fh:
                for r in csv.DictReader(fh):
                    filas[(r['periodo'], r['codigo'])] = r
            if ('2026-04', '7') not in filas:
                err = 'el CSV no tiene la fila de Galicia en 2026-04'
        if err:
            fallar_todos('panel: Galicia', GALICIA_ABRIL_2026, err)
            return
        r = filas[('2026-04', '7')]
        for k, v in GALICIA_ABRIL_2026.items():
            controlar('panel: Galicia %s (2026-04)' % k, float(r[k]) if r[k] else None, v)
        grupos = ('AAA00', 'AAA10', 'AAA20', 'AAA50')
        faltan = [g for g in grupos if ('2026-04', g) not in filas]
        registrar('panel: incluye los agregados (sistema, públicos, privados, 10 primeros)',
                  not faltan, ', '.join(faltan))


def control_ipc():
    titulo('Valores de control: IPC nacional del INDEC')
    for mes, esperado in IPC_MENSUAL.items():
        d, t = correr('consultar_ipc.py', '--mes', mes)
        err = error_de(d)
        if err:
            registrar('IPC mensual %s' % mes, False, err)
        else:
            controlar('IPC mensual %s' % mes, d['datos']['Nivel general']['mensual'], esperado)
    for anio, esperado in IPC_ACUMULADA.items():
        d, t = correr('consultar_ipc.py', '--acumulado', anio)
        err = error_de(d)
        if err:
            registrar('IPC acumulado %s' % anio, False, err)
        else:
            controlar('IPC acumulado %s' % anio, d.get('acumulada_pct'), esperado)


def control_api_frente_a_pdf():
    """Mismos valores en la API y en el PDF para los meses que comparten."""
    a, t1 = correr('consultar_entidad.py', 'Galicia', '--seccion', 'indicadores', 'balance',
                   'cartera', '--serie')
    titulo('API frente a PDF: Galicia')
    if error_de(a):
        registrar('API frente a PDF', False, error_de(a))
        return
    api = {k: v['serie'] for k, v in a['datos'].items()}
    hasta = a['actualizado_a']
    desde = mes_anterior(hasta, 2)  # la API trae los 3 últimos meses
    p, t2 = correr('consultar_historico.py', 'Galicia', '--campo', *sorted(api),
                   '--desde', desde, '--hasta', hasta)
    if error_de(p):
        registrar('API frente a PDF', False, error_de(p))
        return
    comparados, distintos, tolerados = 0, [], 0
    for k, serie in api.items():
        pdf = p['datos'][k]['serie']
        for per, v_api in serie.items():
            if per not in pdf:
                continue
            v_pdf = pdf[per]
            if v_api is None and v_pdf is None:
                continue
            comparados += 1
            # El PDF imprime los valores redondeados (4,3 donde la API dice 4,28):
            # se compara con la precisión del PDF
            if v_api is not None and v_pdf is not None and \
                    abs(v_api - v_pdf) <= 0.5 * 10 ** -decimales(v_pdf) + 1e-9:
                continue
            # Excepción conocida: montos menores a 0,05 millones que el PDF muestra como "---"
            if v_pdf is None and isinstance(v_api, (int, float)) and abs(v_api) < 0.05:
                tolerados += 1
                continue
            distintos.append('%s %s: API %s, PDF %s' % (k, per, v_api, v_pdf))
    detalle = '%d valores de %s a %s, %s, %.1f s' % (
        comparados, desde, hasta, ', '.join(os.path.basename(x) for x in p.get('pdfs', [])),
        t1 + t2)
    if tolerados:
        detalle += '; %d montos menores a 0,05 millones que el PDF muestra como "---"' % tolerados
    if distintos:
        detalle += '; distintos: ' + '; '.join(distintos[:10])
    registrar('API y PDF coinciden', comparados > 0 and not distintos, detalle)


# ---------------------------------------------------------------------------
# Funcionamiento en vivo (los datos cambian: se controla la forma, no el valor)
# ---------------------------------------------------------------------------

def en_vivo():
    titulo('Funcionamiento en vivo')
    d, t = correr('consultar_entidad.py', 'Galicia')
    ok = 'datos' in d and all(k in d['datos'] for k in ('bA', 'irr_tot', 'roe', 'pla', 'sucursales'))
    registrar('consultar_entidad.py: resumen de Galicia', ok,
              error_de(d) or '%.1f s, actualizado a %s' % (t, d.get('actualizado_a')))

    d, t = correr('consultar_entidad.py', 'sistema', '--campo', 'irr_tot', 'pla')
    registrar('consultar_entidad.py: totales del sistema',
              len(d.get('datos', {})) == 2, error_de(d) or '%.1f s' % t)

    d, t = correr('consultar_entidad.py', 'banco de la provincia')
    registrar('consultar_entidad.py: nombre ambiguo devuelve candidatos',
              len(d.get('candidatos', [])) >= 2, '%.1f s, %d candidatos' % (
                  t, len(d.get('candidatos', []))))

    d, t = correr('consultar_ranking.py', 'irr_tot', '--top', '5')
    ok = d.get('entidades_con_dato', 0) >= 40 and len(d.get('ranking', [])) == 5 and all(
        x['valor'] < 1000 for x in d.get('ranking', []))
    registrar('consultar_ranking.py: top 5 por mora', ok, error_de(d) or
              '%.1f s, %s entidades con dato a %s' % (t, d.get('entidades_con_dato'),
                                                       d.get('periodo')))

    d, t = correr('consultar_historico.py', 'Galicia', '--campo', 'irr_tot', '--meses', '6')
    serie = d.get('datos', {}).get('irr_tot', {}).get('serie', {})
    registrar('consultar_historico.py: 6 meses de mora de Galicia',
              len([v for v in serie.values() if v is not None]) == 6,
              error_de(d) or '%.1f s, %s a %s' % (t, d.get('desde'), d.get('hasta')))

    with tempfile.TemporaryDirectory() as tmp:
        d, t = correr('consultar_panel.py', '--modo', 'api', '--entidades', 'Galicia', 'Macro',
                      '--campos', 'bA', 'irr_tot', '--salida', os.path.join(tmp, 'p.csv'))
    registrar('consultar_panel.py: foto por API de Galicia y Macro',
              not error_de(d) and d.get('entidades') == 2 and d.get('periodos', 0) >= 4,
              error_de(d) or '%.1f s, %s a %s' % (t, d.get('desde'), d.get('hasta')))

    d, t = correr('consultar_ipc.py')
    registrar('consultar_ipc.py: último mes con divisiones',
              len(d.get('datos', {})) >= 12, error_de(d) or '%.1f s, mes %s' % (t, d.get('mes')))

    d, t = correr('consultar_pagos.py', '--buscar', 'tarjetas de crédito', '--hoja', 'Tarjetas')
    res = (d.get('resultados') or [{}])[0]
    registrar('consultar_pagos.py: tarjetas de crédito con ticket promedio',
              'ticket_promedio' in res, error_de(d) or '%.1f s, edición %s, mes %s' % (
                  t, d.get('edicion'), res.get('mes')))

    d, t = correr('consultar_entidad.py', 'Galicia', '--seccion', 'ficha')
    f = d.get('ficha', {})
    registrar('consultar_entidad.py: ficha institucional (PDF)',
              any(x.get('cargo') == 'PRESIDENTE' for x in f.get('directivos', [])),
              error_de(d) or f.get('error') or '%.1f s, PDF de %s' % (t, f.get('periodo')))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--locales', action='store_true', help='Solo comprobaciones sin red')
    ap.add_argument('--sin-cache', action='store_true', help='No usar la caché de descargas')
    a = ap.parse_args()
    if a.sin_cache:
        entorno['BCRA_ORACULO_SIN_CACHE'] = '1'

    locales()
    if not a.locales:
        titulo('Requisitos')
        hay = shutil.which('pdftotext') is not None
        registrar('pdftotext instalado', hay,
                  '' if hay else 'instalar: brew install poppler (macOS) o '
                                 'apt-get install -y poppler-utils')
        control_pdf_galicia()
        control_panel()
        control_ipc()
        control_api_frente_a_pdf()
        en_vivo()

    fallas = [n for n, ok in resultados if not ok]
    print('\n%d comprobaciones: %d OK, %d FALLA' % (len(resultados), len(resultados) - len(fallas),
                                                   len(fallas)))
    sys.exit(1 if fallas else 0)


if __name__ == '__main__':
    main()
