# Tests del inventario de calidad de datos (scripts/audit_inventario.py)
import importlib.util
import os

import pytest

RUTA_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "audit_inventario.py")
spec = importlib.util.spec_from_file_location("audit_inventario", RUTA_SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def escribir(tmp_path, nombre, texto):
    ruta = tmp_path / nombre
    ruta.write_text(texto, encoding="utf-8")
    return str(ruta)


def test_detecta_separador_periodos_y_duplicados(tmp_path):
    ruta = escribir(tmp_path, "indices.csv",
                    "Año;Periodo;Índice\n"
                    "2020;Trimestre 1;100,5\n"
                    "2020;Trimestre 2;101,2\n"
                    "2020;Trimestre 2;101,2\n"
                    "2021;Trimestre 1;1.079\n")
    r = audit.audit_file(ruta)
    assert r["delimitador"] == ";"
    assert r["filas_datos"] == 4
    assert (r["anio_desde"], r["anio_hasta"]) == (2020, 2021)
    assert r["filas_duplicadas"] == 1
    # "1.079" es ambiguo porque el archivo también usa coma decimal
    assert r["valores_ambiguos_miles_decimal"] == 1


def test_separa_bloque_de_metadatos_del_final(tmp_path):
    ruta = escribir(tmp_path, "con_metadatos.csv",
                    "Año;Valor\n"
                    "2019;5\n"
                    ";;\n"
                    '"Fuente":"INE"\n'
                    '"Url":"https://example.org"\n')
    r = audit.audit_file(ruta)
    assert r["filas_datos"] == 1
    assert r["bloque_metadatos"] == "sí"
    assert r["fuente_metadatos"] == "INE"


def test_codigos_postales_no_cuentan_como_anios(tmp_path):
    ruta = escribir(tmp_path, "catastro.csv",
                    "codigo_postal,precio\n"
                    "28001,1292.95\n"
                    "47001,1100.10\n")
    r = audit.audit_file(ruta)
    assert r["anio_desde"] == "" and r["anio_hasta"] == ""


def test_recoge_csv_por_carpeta(tmp_path):
    (tmp_path / "alquiler").mkdir()
    (tmp_path / "demografia").mkdir()
    escribir(tmp_path / "alquiler", "a.csv", "Año;V\n2020;1\n")
    escribir(tmp_path / "demografia", "d.csv", "Año;V\n2020;2\n")
    escribir(tmp_path / "demografia", "no_csv.txt", "x")
    encontrados = audit.recoger_csv(str(tmp_path))
    carpetas = sorted(c for c, _ in encontrados)
    assert carpetas == ["alquiler", "demografia"]


def test_informe_incluye_cada_archivo(tmp_path):
    escribir(tmp_path, "uno.csv", "Año;V\n2020;1\n")
    informe, resultados = audit.generar_informe(str(tmp_path))
    assert len(resultados) == 1
    assert "uno.csv" in informe
    assert "## Incidencias por tipo" in informe
