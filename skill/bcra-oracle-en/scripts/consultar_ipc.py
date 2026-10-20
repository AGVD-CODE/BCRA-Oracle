#!/usr/bin/env python3
"""
Consulta datos de inflación del archivo IPC Nacional del INDEC (.xls).

Uso:
    # 1. Descargar el archivo del INDEC (¡el nombre es el MES DE PUBLICACIÓN!):
    #    El IPC de junio se publica en julio → sh_ipc_07_26.xls
    #    Probar desde el mes actual hacia atrás hasta que pese ~2.3MB (no ~36KB).
    #    wget -q "https://www.indec.gob.ar/ftp/cuadros/economia/sh_ipc_07_26.xls" -O /tmp/ipc.xls
    #
    # 2. Consultar:
    python consultar_ipc.py /tmp/ipc.xls --ultimo          # último mes disponible
    python consultar_ipc.py /tmp/ipc.xls --serie nivel     # serie completa del nivel general
    python consultar_ipc.py /tmp/ipc.xls --mes 2026-06     # un mes específico

Requiere: pip install xlrd --break-system-packages
Devuelve JSON. Si un dato no está, lo devuelve como null (nunca inventa).
"""
import sys, json, argparse
from datetime import datetime, timedelta

try:
    import xlrd
except ImportError:
    print(json.dumps({'error': 'Falta xlrd. Instalar con: pip install xlrd --break-system-packages'}))
    sys.exit(1)

MESES = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}

SERIES = {
    'nivel': ('Variación mensual IPC Nacional', 'Nivel general'),
    'interanual': ('Var. interanual IPC Nacional', 'Nivel general'),
    'nucleo': ('Variación mensual IPC Nacional', 'Núcleo'),
    'regulados': ('Variación mensual IPC Nacional', 'Regulados'),
    'estacional': ('Variación mensual IPC Nacional', 'Estacional'),
    'bienes': ('Variación mensual IPC Nacional', 'Bienes'),
    'servicios': ('Variación mensual IPC Nacional', 'Servicios'),
}

def excel_date(n):
    try: return datetime(1899, 12, 30) + timedelta(days=int(n))
    except: return None

def mlabel(dt):
    return f"{MESES[dt.month]}-{str(dt.year)[2:]}"

def col_map(sheet):
    """Mapea columna → etiqueta de mes 'YYYY-MM', leyendo la fila 5 (fechas serial Excel)."""
    fechas = sheet.row_values(5)
    cm = {}
    for c in range(1, sheet.ncols):
        f = fechas[c]
        if isinstance(f, float) and f > 40000:
            dt = excel_date(f)
            if dt: cm[c] = dt.strftime('%Y-%m')
    return cm

def find_row(sheet, label):
    for r in range(sheet.nrows):
        if str(sheet.cell_value(r, 0)).strip() == label:
            return r
    return None

def get_serie(wb, serie_key):
    hoja, etiqueta = SERIES[serie_key]
    try:
        sh = wb.sheet_by_name(hoja)
    except:
        return None, None
    cm = col_map(sh)
    r = find_row(sh, etiqueta)
    if r is None:
        return None, None
    inv = {}  # 'YYYY-MM' → valor
    for c, ym in cm.items():
        v = sh.cell_value(r, c)
        inv[ym] = round(float(v), 2) if v != '' else None
    return inv, sorted(inv.keys())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('xls', help='Ruta al archivo sh_ipc_MM_YY.xls del INDEC')
    ap.add_argument('--ultimo', action='store_true', help='Devolver el último mes disponible de todas las series')
    ap.add_argument('--serie', help='Serie a devolver (nivel, interanual, nucleo, regulados, estacional, bienes, servicios)')
    ap.add_argument('--mes', help='Mes específico en formato YYYY-MM')
    args = ap.parse_args()

    wb = xlrd.open_workbook(args.xls)

    if args.ultimo:
        out = {}
        ultimo_ym = None
        for k in SERIES:
            serie, orden = get_serie(wb, k)
            if serie:
                # último mes con dato no nulo
                for ym in reversed(orden):
                    if serie[ym] is not None:
                        out[k] = {'valor': serie[ym], 'mes': ym}
                        ultimo_ym = ym
                        break
        out['_periodo'] = ultimo_ym
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    if args.serie:
        serie, orden = get_serie(wb, args.serie)
        if serie is None:
            print(json.dumps({'error': f'Serie "{args.serie}" no encontrada'}, ensure_ascii=False))
            return
        print(json.dumps({'serie': args.serie, 'datos': serie}, ensure_ascii=False, indent=2))
        return

    if args.mes:
        out = {'mes': args.mes}
        for k in SERIES:
            serie, _ = get_serie(wb, k)
            out[k] = serie.get(args.mes) if serie else None
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    # Sin argumentos: mostrar qué meses hay disponibles
    serie, orden = get_serie(wb, 'nivel')
    print(json.dumps({'meses_disponibles': orden, 'ultimo': orden[-1] if orden else None}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
