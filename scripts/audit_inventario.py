"""Inventario y diagnóstico de calidad de los CSV de data/.

Uso:
    python scripts/audit_inventario.py                      # imprime el informe en Markdown
    python scripts/audit_inventario.py --salida docs/auditoria_inventario.md

Recorre data/alquiler, data/demografia y data/transmisiones (o la carpeta que indiques
con --datos). Solo usa la librería estándar y nunca modifica los archivos de datos.
"""
import argparse
import csv
import hashlib
import os
import re
from collections import Counter

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATOS_POR_DEFECTO = os.path.join(REPO, "data")

# Bloque de metadatos que epdata.es añade al final de cada export
TRAILER = re.compile(r'^\s*"?(Métrica|Fuente|Clasificación|Unidad|Escala|EscalaFactorPotencia10|SonDatosNumericos|Url|Titulo|Subtitulo)"?\s*[:;]')
BLANK = re.compile(r"^[;\s]*$")
# Solo años plausibles: evita confundir códigos postales o precios con años
YEAR = re.compile(r"^\s*((?:19|20)\d{2})(?:\s*-\s*\d|T\d)?\s*$")
PERIOD_LIKE = YEAR
DECIMAL_COMMA = re.compile(r"^-?(\d{1,3}(\.\d{3})+|\d+),\d+$")
# "1.079" puede ser 1079 (miles) o 1,079 (decimal): ambiguo sin contexto
AMBIGUOUS = re.compile(r"^\d{1,3}\.\d{3}$")
PERIOD_HEADERS = {"año", "anio", "periodo", "fecha"}


def split_body(lines):
    """Devuelve las líneas de datos y el bloque de metadatos (si existe)."""
    body, meta = [], []
    for i, line in enumerate(lines):
        if BLANK.match(line) or TRAILER.match(line):
            meta = lines[i:]
            break
        body.append(line)
    return body, meta


def find_period_col(header, rows):
    """Columna con el año/periodo: por nombre de cabecera o por contenido."""
    for i, h in enumerate(header):
        if h.strip().lower() in PERIOD_HEADERS:
            return i
    for i in range(len(header)):
        # Sin cabecera, o con cabecera genérica de periodo; no año de construcción
        if header[i].strip():
            continue
        vals = [r[i] for r in rows if i < len(r) and r[i].strip()]
        if vals and sum(1 for v in vals if YEAR.match(v)) / len(vals) > 0.8:
            return i
    return None


def audit_file(path):
    raw = open(path, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.splitlines()
    body, meta = split_body(lines)

    first = body[0] if body else ""
    delim = ";" if first.count(";") >= first.count(",") else ","
    rows = list(csv.reader(body, delimiter=delim))
    header, data = rows[0], rows[1:]
    ncols = len(header)

    period_idx = find_period_col(header, data)
    years = []
    if period_idx is not None:
        for r in data:
            if period_idx < len(r):
                m = YEAR.match(r[period_idx])
                if m:
                    years.append(int(m.group(1)))
    periods = {r[period_idx].strip() for r in data if period_idx is not None and period_idx < len(r)}

    cells = [(i, c) for r in data for i, c in enumerate(r)]
    empty = sum(1 for _, c in cells if c.strip() == "")
    value_cells = [c.strip() for i, c in cells if i != period_idx]
    # Solo es ambiguo "1.079" si el archivo también usa coma decimal
    has_decimal_comma = any(DECIMAL_COMMA.match(c) for c in value_cells)
    ambiguous = sum(1 for c in value_cells if AMBIGUOUS.match(c)) if has_decimal_comma else 0
    placeholders = sum(1 for c in value_cells if c == "..")
    period_in_value = sum(1 for c in value_cells if PERIOD_LIKE.match(c))
    unnamed = sum(1 for _, c in cells if "Unnamed" in c)
    bad_width = sum(1 for r in data if len(r) != ncols)
    dups = len(data) - len({tuple(r) for r in data})

    fuente = ""
    for line in meta:
        m = re.search(r'"?Fuente"?\s*[:;]\s*"?([^";]+)', line)
        if m:
            fuente = m.group(1).strip()
            break

    return {
        "archivo": os.path.basename(path),
        "bom": "sí" if bom else "no",
        "delimitador": delim,
        "filas_datos": len(data),
        "columnas": ncols,
        "filas_ancho_incorrecto": bad_width,
        "bloque_metadatos": "sí" if meta else "no",
        "fuente_metadatos": fuente,
        "col_periodo": header[period_idx].strip() if period_idx is not None else "",
        "anio_desde": min(years) if years else "",
        "anio_hasta": max(years) if years else "",
        "anios_distintos": len(set(years)),
        "periodos_distintos": len(periods),
        "celdas_vacias": empty,
        "pct_celdas_vacias": round(100 * empty / len(cells), 1) if cells else 0,
        "filas_duplicadas": dups,
        "valores_ambiguos_miles_decimal": ambiguous,
        "valores_punto_punto": placeholders,
        "celdas_con_formato_periodo_fuera_de_col_periodo": period_in_value,
        "cabeceras_Unnamed": unnamed,
        "tamano_bytes": len(raw),
        "sha256_12": hashlib.sha256(raw).hexdigest()[:12],
    }




def recoger_csv(carpeta_datos):
    """Lista (carpeta_relativa, ruta) de todos los CSV bajo carpeta_datos."""
    encontrados = []
    for raiz, _, nombres in os.walk(carpeta_datos):
        for nombre in sorted(nombres):
            if nombre.lower().endswith(".csv"):
                ruta = os.path.join(raiz, nombre)
                carpeta = os.path.relpath(raiz, carpeta_datos)
                encontrados.append((carpeta, ruta))
    return sorted(encontrados)


def generar_informe(carpeta_datos):
    """Devuelve el informe Markdown para todos los CSV de carpeta_datos."""
    archivos = recoger_csv(carpeta_datos)
    resultados = []
    for carpeta, ruta in archivos:
        r = audit_file(ruta)
        r["carpeta"] = carpeta
        resultados.append(r)

    cols = ["carpeta", "archivo", "filas_datos", "columnas", "fuente_metadatos", "col_periodo",
            "anio_desde", "anio_hasta", "pct_celdas_vacias", "filas_duplicadas",
            "valores_ambiguos_miles_decimal", "filas_ancho_incorrecto",
            "celdas_con_formato_periodo_fuera_de_col_periodo"]
    lineas = [
        "# Auditoría de inventario de datos",
        "",
        f"Archivos analizados: {len(resultados)} CSV bajo `{os.path.relpath(carpeta_datos, REPO)}`.",
        "",
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for r in resultados:
        lineas.append("| " + " | ".join(str(r[c]) for c in cols) + " |")

    incidencias = Counter()
    for r in resultados:
        if r["filas_ancho_incorrecto"]:
            incidencias["ancho de fila inconsistente"] += 1
        if r["celdas_con_formato_periodo_fuera_de_col_periodo"]:
            incidencias["periodos en columna de valores"] += 1
        if r["valores_ambiguos_miles_decimal"]:
            incidencias["valores ambiguos miles/decimal"] += 1
        if r["filas_duplicadas"]:
            incidencias["filas duplicadas"] += 1
        if r["valores_punto_punto"]:
            incidencias["placeholders '..'"] += 1
        if r["bom"] == "sí":
            incidencias["BOM UTF-8"] += 1
    lineas += ["", "## Incidencias por tipo", ""]
    for nombre, n in incidencias.most_common():
        lineas.append(f"- {nombre}: {n} archivos")
    lineas.append("")
    return "\n".join(lineas), resultados


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--datos", default=DATOS_POR_DEFECTO, help="carpeta con los CSV (por defecto data/)")
    parser.add_argument("--salida", help="ruta del informe Markdown; si se omite, se imprime en pantalla")
    args = parser.parse_args()

    informe, resultados = generar_informe(args.datos)
    if args.salida:
        os.makedirs(os.path.dirname(os.path.abspath(args.salida)), exist_ok=True)
        with open(args.salida, "w", encoding="utf-8") as f:
            f.write(informe)
        print(f"OK: {len(resultados)} archivos -> {args.salida}")
    else:
        print(informe)


if __name__ == "__main__":
    main()
