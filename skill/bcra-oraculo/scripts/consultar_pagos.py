#!/usr/bin/env python3
"""
Consulta datos de medios de pago del XLSX de Pagos Minoristas del BCRA.

El XLSX tiene varias hojas (Cheques, Transferencias, Tarjetas, etc.), cada una con
su propia estructura. Este script ayuda a explorar y extraer, pero para preguntas
específicas conviene inspeccionar la hoja relevante (el archivo trae la serie histórica
completa, así que una descarga alcanza).

Uso:
    # Descargar (ver references/fuentes.md):
    #   wget -q "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/Informes/series-informe-mensual-pagos-minoristas-2026-06.xlsx" -O /tmp/pagos.xlsx

    python consultar_pagos.py /tmp/pagos.xlsx --hojas            # listar hojas
    python consultar_pagos.py /tmp/pagos.xlsx --hoja "Tarjetas"  # volcar una hoja para inspección

Requiere: pip install openpyxl --break-system-packages
"""
import sys, json, argparse

try:
    import openpyxl
except ImportError:
    print(json.dumps({'error': 'Falta openpyxl. Instalar: pip install openpyxl --break-system-packages'}))
    sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('xlsx')
    ap.add_argument('--hojas', action='store_true', help='Listar las hojas del archivo')
    ap.add_argument('--hoja', help='Volcar el contenido de una hoja (primeras filas) para inspección')
    ap.add_argument('--filas', type=int, default=40, help='Cuántas filas volcar (default 40)')
    args = ap.parse_args()

    wb = openpyxl.load_workbook(args.xlsx, read_only=True, data_only=True)

    if args.hojas:
        print(json.dumps({'hojas': wb.sheetnames}, ensure_ascii=False, indent=2))
        return

    if args.hoja:
        if args.hoja not in wb.sheetnames:
            print(json.dumps({'error': f'Hoja "{args.hoja}" no existe', 'hojas': wb.sheetnames}, ensure_ascii=False))
            return
        ws = wb[args.hoja]
        rows = []
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= args.filas: break
            # Limpiar celdas None de los extremos para legibilidad
            vals = [c for c in row]
            rows.append(vals)
        print(json.dumps({'hoja': args.hoja, 'filas': rows}, ensure_ascii=False, indent=2, default=str))
        return

    print(json.dumps({'hojas': wb.sheetnames, 'ayuda': 'Usar --hoja "<nombre>" para inspeccionar'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
