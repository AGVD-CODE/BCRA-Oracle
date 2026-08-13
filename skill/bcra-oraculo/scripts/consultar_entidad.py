#!/usr/bin/env python3
"""
Consulta indicadores, balance y mora de un banco (o de todos) desde el PDF de
Entidades Financieras del BCRA, para UN período.

Uso:
    # 1. Descargar el PDF del período (ver references/fuentes.md):
    #    wget -q "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Entidades/202604e.pdf" -O /tmp/entidades.pdf
    #    pdftotext -layout /tmp/entidades.pdf /tmp/entidades.txt
    #
    # 2. Consultar (el período se pasa para localizar el pie de página del PDF):
    python consultar_entidad.py /tmp/entidades.txt --periodo "Abril 2026" --banco "Galicia"
    python consultar_entidad.py /tmp/entidades.txt --periodo "Abril 2026" --banco "Galicia" --campo irr_tot
    python consultar_entidad.py /tmp/entidades.txt --periodo "Abril 2026" --todos --campo irr_tot

NUNCA inventa: si un campo no aparece, lo devuelve como null.
"""
import re, json, sys, argparse, unicodedata

COL = 4  # columna del período más reciente en cada página del banco

NAME_TO_COD = {
    'BACS BANCO DE CREDITO Y SECURITIZACION S.A.': '340', 'BANCO BBVA ARGENTINA S.A.': '17',
    'BANCO BICA S.A.': '426', 'BANCO CMF S.A.': '319', 'BANCO COINAG S.A.': '431',
    'BANCO COLUMBIA S.A.': '389', 'BANCO COMAFI SOCIEDAD ANONIMA': '299',
    'BANCO CREDICOOP COOPERATIVO LIMITADO': '191', 'BANCO DE COMERCIO S.A.': '432',
    'BANCO DE CORRIENTES S.A.': '94', 'BANCO DE FORMOSA S.A.': '315',
    'BANCO DE GALICIA Y BUENOS AIRES S.A.': '7', 'BANCO DE INVERSION Y COMERCIO EXTERIOR S.A.': '300',
    'BANCO DE LA CIUDAD DE BUENOS AIRES': '29', 'BANCO DE LA NACION ARGENTINA': '11',
    'BANCO DE LA PAMPA SA': '93', 'BANCO DE LA PROVINCIA DE BUENOS AIRES': '14',
    'BANCO DE LA PROVINCIA DE CORDOBA S.A.': '20', 'BANCO DE LA REPUBLICA ORIENTAL DEL URUGUAY': '269',
    'BANCO DE SAN JUAN S.A.': '45', 'BANCO DE SANTA CRUZ S.A.': '86',
    'BANCO DE SANTIAGO DEL ESTERO S.A.': '321', 'BANCO DE SERVICIOS FINANCIEROS S.A.': '332',
    'BANCO DE SERVICIOS FINANCIEROS CARREFOUR SAU': '332', 'BANCO DE SERVICIOS Y TRANSACCIONES SAU': '338',
    'BANCO DE VALORES S.A.': '198', 'BANCO DEL CHUBUT S.A.': '83', 'BANCO DEL SOL S.A.': '310',
    'BANCO DINO S.A.': '448', 'BANCO HIPOTECARIO S.A.': '44', 'BANCO INDUSTRIAL S.A.': '322',
    'BANCO JULIO SOCIEDAD ANONIMA': '305', 'BANCO MACRO S.A.': '285', 'BANCO MARIVA S.A.': '254',
    'BANCO MASVENTAS S.A.': '341', 'BANCO MERIDIAN S.A.': '281', 'BANCO MUNICIPAL DE ROSARIO': '65',
    'BANCO PATAGONIA S.A.': '34', 'BANCO PIANO S.A.': '301', 'BANCO PROVINCIA DE TIERRA DEL FUEGO': '268',
    'BANCO PROVINCIA DEL NEUQUEN SOCIEDAD ANONIMA': '97', 'BANCO RIOJA SOCIEDAD ANONIMA UNIPERSONAL': '309',
    'BANCO ROELA S.A.': '247', 'BANCO SAENZ S.A.': '277', 'BANCO SANTANDER ARGENTINA S.A.': '72',
    'BANCO SUCREDITO REGIONAL S.A.U.': '435', 'BANCO SUPERVIELLE S.A.': '27', 'BANCO VOII S.A.': '312',
    'BANK OF CHINA LIMITED': '131', 'BANK OF CHINA LIMITED SUCURSAL BUENOS AIRES': '131',
    'BIBANK S.A.': '147', 'BNP PARIBAS': '266', 'BRUBANK S.A.U.': '143', 'CITIBANK N.A.': '16',
    'INDUSTRIAL AND COMMERCIAL BANK OF CHINA S.A.U.': '15', 'JPMORGAN CHASE BANK, NATIONAL ASSOCIATION': '165',
    'NUEVO BANCO DE ENTRE RIOS S.A.': '386', 'NUEVO BANCO DE SANTA FE SOCIEDAD ANONIMA': '330',
    'NUEVO BANCO DEL CHACO S. A.': '311', 'RCI BANQUE S.A.': '339', 'UALA BANK S.A.U.': '384',
    'BANCO DE GALICIA Y BUENOS AIRES S.A.U.': '7', 'BANCO GGAL SA': '7',
    'BANCO BICA SOCIEDAD ANONIMA': '426', 'BANCO DE SAN JUAN S. A.': '45',
    'BANCO SANTANDER ARGENTINA SOCIEDAD ANONIMA': '72',
    'INDUSTRIAL AND COMMERCIAL BANK OF CHINA (ARGENTINA) S.A.U.': '15',
    'NUEVO BANCO DE SANTA FE SA': '330',
}

IND_MAP = [
    ('apalancamiento', 'Apalancamiento'), ('irr_tot', 'Total Cartera Irregular / Total Financiaciones'),
    ('prev_irr', 'Previsiones sobre Cartera Irregular'), ('irr_cons', 'Cartera Irregular Consumo'),
    ('irr_com', 'Cartera Irregular Comercial'), ('exc_prev', 'Posicion de Previsiones'),
    ('part_venc', 'Importancia de Cartera Vencida'), ('absorc_gastos', 'Absorcion de Gastos'),
    ('dep_empleado', 'Depositos por Empleado'), ('fin_empleado', 'Financiaciones por Empleado'),
    ('tasa_prest', 'Tasa Implicita Prestamos Totales'), ('tasa_dep', 'Tasa Implicita Depositos Totales'),
    ('margen_fin_activo', 'Margen Financiero en Terminos de Activo'),
    ('roa_inco', 'Cargos por Incobrabilidad / Activo'), ('result_serv_activo', 'Resultados por Servicios / Activo'),
    ('roa_adm', 'Gastos de Administracion / Activo'), ('liq_tit_cot', 'Liquidez con titulos con cotiz'),
]
BAL_MAP = [
    ('bA', r'^\s+ACTIVO\s'), ('bPr', r'^\s+Pr.stamos\s'), ('bDe', r'^\s+Dep.sitos\s'),
    ('bCA', 'Caja de ahorro'), ('bPN', 'PATRIMONIO NETO'), ('bTi', 'itulos P'),
    ('bPF', 'Plazo fijo'),
]

def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', re.sub(r'[^A-Za-z0-9 ]', ' ', s.upper())).strip()

def parse_num(s):
    if not s or s.strip() == '---': return None
    s = s.strip().rstrip('%').replace('.', '').replace(',', '.')
    try: return round(float(s), 4)
    except: return None

def get_col(line, col_idx):
    tokens = re.findall(r'-?\d+(?:\.\d+)*,\d+%?|---', line)
    data = [parse_num(t) for t in tokens]
    return data[col_idx] if len(data) > col_idx else None

def parse_indicadores(text, col):
    d = {}
    for line in text.split('\n'):
        nl = norm(line)
        for key, needle in IND_MAP:
            if norm(needle) in nl and key not in d:
                d[key] = get_col(line, col); break
        if 'Rendimiento Anual' in line and 'ROE' in line and 'roe' not in d:
            d['roe'] = get_col(line, col)
        elif 'Retorno sobre Activos' in line and 'ROA' in line and 'antes' not in line.lower() and 'roa' not in d:
            d['roa'] = get_col(line, col)
    return d

def parse_balance(text, col):
    b = {}
    for line in text.split('\n'):
        for key, pat in BAL_MAP:
            if key in b: continue
            if pat.startswith('^'):
                if re.search(pat, line): b[key] = get_col(line, col)
            elif pat in line:
                b[key] = get_col(line, col)
    return b

def extract_bank_name(page_text, period_word):
    for line in page_text.split('\n'):
        line = line.strip()
        if (len(line) > 10 and re.search(r'[A-ZAEIOU]{4,}', line) and
            period_word not in line and 'INDICADORES' not in line and
            not any(x in line for x in ['CAPITAL', 'ACTIVOS', 'EFICIENCIA', 'RENTABILIDAD',
                'LIQUIDEZ', 'Apalancamiento', 'Cartera', 'Retorno', 'Gastos', 'Tasa', 'Margen',
                'Liquidez', 'Rendimiento', 'Posici', 'Importancia']) and
            '%' not in line and not re.search(r'\d,\d', line)):
            if any(w in line for w in ['BANCO', 'BANK', 'CITIBANK', 'JPMORGAN', 'BNP', 'RCI',
                'BRUBANK', 'BIBANK', 'UALA', 'BACS', 'INDUSTRIAL', 'NUEVO', 'COMAFI', 'CREDICOOP',
                'HIPOTECARIO', 'PATAGONIA', 'SUPERVIELLE', 'MACRO', 'GALICIA', 'SANTANDER', 'BBVA',
                'ROELA', 'MARIVA', 'MASVENTAS', 'MERIDIAN', 'MUNICIPAL', 'PIANO', 'RIOJA', 'SAENZ',
                'SUCREDITO', 'VOII', 'DINO', 'JULIO', 'CMF', 'BICA', 'COINAG', 'COLUMBIA', 'FORMOSA',
                'CORRIENTES', 'CHUBUT', 'CHACO', 'NEUQU', 'PAMPA', 'SANTIAGO', 'ENTRE', 'SANTA FE',
                'TIERRA DEL FUEGO', 'CARREFOUR', 'COMERCIO', 'VALORES']):
                return line
    return None

def process(txt_path, period_word):
    with open(txt_path, encoding='utf-8', errors='replace') as f:
        pages = f.read().split('\f')
    footer = f'{period_word} | Informaci'
    data = {}
    seen = set()
    for i, page in enumerate(pages):
        if 'INDICADORES' in page and 'Apalancamiento' in page and footer in page:
            name = extract_bank_name(page, period_word)
            if not name: continue
            cod = NAME_TO_COD.get(name)
            if not cod or cod in seen: continue
            seen.add(cod)
            ind = parse_indicadores(page, COL)
            bal = parse_balance(pages[i-1], COL) if i > 0 else {}
            data[cod] = {'n': name, 'datos': {**ind, **bal}}
    return data

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('txt')
    ap.add_argument('--periodo', required=True)
    ap.add_argument('--banco')
    ap.add_argument('--todos', action='store_true')
    ap.add_argument('--campo')
    args = ap.parse_args()

    data = process(args.txt, args.periodo)
    if not data:
        print(json.dumps({'error': f'No se encontraron bancos. Verificar que "{args.periodo}" coincida con el pie de pagina del PDF.'}, ensure_ascii=False))
        return

    if args.todos:
        result = {info['n']: (info['datos'].get(args.campo) if args.campo else info['datos']) for cod, info in data.items()}
        print(json.dumps({'periodo': args.periodo, 'total': len(data), 'bancos': result}, ensure_ascii=False, indent=2))
        return

    if not args.banco:
        print(json.dumps({'periodo': args.periodo, 'bancos_disponibles': sorted(v['n'] for v in data.values())}, ensure_ascii=False, indent=2))
        return

    nq = norm(args.banco)
    cands = [(cod, info) for cod, info in data.items() if nq in norm(info['n'])]
    if not cands:
        print(json.dumps({'error': f'No se encontro "{args.banco}"', 'disponibles': sorted(v['n'] for v in data.values())[:15]}, ensure_ascii=False, indent=2))
        return
    if len(cands) > 1:
        print(json.dumps({'ambiguo': args.banco, 'candidatos': [c[1]['n'] for c in cands]}, ensure_ascii=False, indent=2))
        return

    cod, info = cands[0]
    out = {'banco': info['n'], 'codigo': cod, 'periodo': args.periodo}
    if args.campo:
        out[args.campo] = info['datos'].get(args.campo)
    else:
        out['datos'] = info['datos']
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
