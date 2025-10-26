# =======================================
# DASHBOARD FINAL ROBUSTO - ÍNDICE DE ALQUILER + DEMOGRAFÍA
# =======================================

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from csv import Sniffer
from unidecode import unidecode

# --------------------------------------------------------
# CONFIGURACIÓN INICIAL
# --------------------------------------------------------
st.set_page_config(page_title="Índice de Alquiler y Demografía en España", layout="wide")
st.title("🏘️ Índice de Alquiler y Distribución Demográfica en España")

# --------------------------------------------------------
# FUNCIÓN AUXILIAR: DETECTAR DELIMITADOR
# --------------------------------------------------------
def detectar_delimitador(filepath, n_bytes=2048):
    with open(filepath, "r", encoding="utf-8") as f:
        muestra = f.read(n_bytes)
        sniffer = Sniffer()
        delimitador = sniffer.sniff(muestra).delimiter
    return delimitador

# --------------------------------------------------------
# CARGA DE DATOS
# --------------------------------------------------------
@st.cache_data
def cargar_alquiler():
    sep = detectar_delimitador('/Users/thimerson/Desktop/CSV/CSV LISTOS/Modulo 1/indices_alquiler.csv')
    df = pd.read_csv('/Users/thimerson/Desktop/CSV/CSV LISTOS/Modulo 1/indices_alquiler.csv', sep=sep, on_bad_lines="skip", encoding="utf-8")
    df.columns = df.columns.map(lambda x: unidecode(x.lower().strip().replace(" ", "_")))
    if "año" in df.columns:
        df.rename(columns={"año": "anio"}, inplace=True)
    df["anio"] = pd.to_numeric(df.get("anio"), errors="coerce")
    if "valor" in df.columns:
        df["valor"] = (
            df["valor"].astype(str)
            .str.replace(",", ".")
            .str.replace(r"[^\d.\-]", "", regex=True)
        )
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df

@st.cache_data
def cargar_demografia():
    sep = detectar_delimitador('/Users/thimerson/Desktop/CSV/CSV LISTOS/Modulo 1/df_mineria_datos_edades.csv')
    df_demo = pd.read_csv('/Users/thimerson/Desktop/CSV/CSV LISTOS/Modulo 1/df_mineria_datos_edades.csv', sep=sep, on_bad_lines="skip", encoding="utf-8")
    df_demo.columns = df_demo.columns.map(lambda x: unidecode(x.lower().strip().replace(" ", "_")))
    df_demo["anio"] = pd.to_numeric(df_demo.get("anio"), errors="coerce")
    # Normalización de texto
    for c in df_demo.select_dtypes(include="object").columns:
        df_demo[c] = df_demo[c].astype(str).str.strip()
    return df_demo

df = cargar_alquiler()
df_demo = cargar_demografia()

# --------------------------------------------------------
# VALIDACIÓN Y UNIÓN DE DATASETS
# --------------------------------------------------------
col_com_alq = next((c for c in df.columns if "comun" in c or "ccaa" in c), None)
col_com_demo = next((c for c in df_demo.columns if "comun" in c or "ccaa" in c), None)
col_anio, col_valor = "anio", "valor"

if not col_com_alq or not col_com_demo:
    st.error("❌ No se encontró una columna de comunidad / CCAA en los CSV.")
    st.write("Columnas de índices:", df.columns.tolist())
    st.write("Columnas de demografía:", df_demo.columns.tolist())
    st.stop()

# Forzar afinidad de tipos
df[col_com_alq] = df[col_com_alq].astype(str).str.strip()
df_demo[col_com_demo] = df_demo[col_com_demo].astype(str).str.strip()

df_merged = pd.merge(
    df, df_demo,
    left_on=[col_com_alq, col_anio],
    right_on=[col_com_demo, col_anio],
    how="left"
)
col_comunidad = col_com_alq

# --------------------------------------------------------
# DETECCIÓN AUTOMÁTICA DE COLUMNAS DEMOGRÁFICAS
# --------------------------------------------------------
posibles_grupos = ["adultos","boomers","estudiantes","jovenes_adultos","jubilados","menores","prejubilados","price","edad"]
col_demograficas = [c for c in posibles_grupos if c in df_merged.columns]

if not col_demograficas:
    st.warning("⚠️ No se detectaron columnas demográficas válidas en el CSV.")
    st.write("Columnas detectadas:", df_merged.columns.tolist())
    st.stop()

# --------------------------------------------------------
# BARRA LATERAL DE FILTROS MEJORADA
# --------------------------------------------------------
st.sidebar.header("🎚️ Filtros Interactivos")

# --- Detección de columnas de comunidad y provincia ---
col_comunidad = next((c for c in df_merged.columns if "comun" in c or "comunidad autónoma" in c), None)
col_provincia = next((c for c in df_merged.columns if "prov" in c and "cod" not in c), None)
col_anio = "anio"
col_valor = "valor"

# --- Filtro de Comunidad Autónoma ---
if col_comunidad:
    comunidades = st.sidebar.multiselect(
        "Selecciona comunidad(es) autónoma(s):",
        sorted(df_merged[col_comunidad].dropna().unique())
    )
    if comunidades:
        df_merged = df_merged[df_merged[col_comunidad].isin(comunidades)]

# --- Filtro de Provincia ---
if col_provincia:
    provincias = st.sidebar.multiselect(
        "Selecciona provincia(s):",
        sorted(df_merged[col_provincia].dropna().unique())
    )
    if provincias:
        df_merged = df_merged[df_merged[col_provincia].isin(provincias)]

# --- Filtro de Años ---
anios = sorted(df_merged[col_anio].dropna().unique())
if anios:
    anio_min, anio_max = int(anios[0]), int(anios[-1])
    anio_rango = st.sidebar.slider("Rango de años:", anio_min, anio_max, (anio_min, anio_max))
    df_merged = df_merged[df_merged[col_anio].between(anio_rango[0], anio_rango[1])]
    anio_top = st.sidebar.selectbox("Selecciona año para el Top 5:", anios, index=len(anios)-1)

# --- Filtro de Variable Demográfica ---
grupo_dem = st.sidebar.selectbox(
    "Selecciona grupo demográfico o variable de análisis:",
    col_demograficas
)

# --------------------------------------------------------
# GRÁFICO 1 — EVOLUCIÓN TEMPORAL
# --------------------------------------------------------
st.subheader("📈 Evolución temporal del valor medio del índice de alquiler")
fig_line = px.line(df_merged, x=col_anio, y=col_valor, color=col_comunidad, markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# --------------------------------------------------------
# GRÁFICO 2 — RELACIÓN ÍNDICE vs GRUPO DEMOGRÁFICO
# --------------------------------------------------------
st.subheader(f"👥 Relación entre índice de alquiler y {grupo_dem}")
fig_scatter = px.scatter(
    df_merged, x=grupo_dem, y=col_valor, color=col_comunidad, trendline="ols",
    title=f"Relación entre {grupo_dem} y el índice de alquiler"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# --------------------------------------------------------
# GRÁFICO 3 — MAPA INTERACTIVO
# --------------------------------------------------------
st.subheader(f"🗺️ Distribución de {grupo_dem} por comunidad ({anio_top})")
df_mapa = (
    df_merged[df_merged[col_anio] == anio_top]
    .groupby(col_comunidad, as_index=False)[grupo_dem]
    .mean()
    .rename(columns={grupo_dem: "valor"})
)

@st.cache_data
def cargar_geojson():
    url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson"
    r = requests.get(url)
    return r.json()

geojson = cargar_geojson()
if not df_mapa.empty:
    fig_map = px.choropleth(
        df_mapa,
        geojson=geojson,
        locations=col_comunidad,
        featureidkey="properties.name",
        color="valor",
        color_continuous_scale="Tealgrn"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ No hay datos válidos para el mapa.")

# --------------------------------------------------------
# TOP 5 COMUNIDADES
# --------------------------------------------------------
st.subheader(f"🏅 Top 5 comunidades por valor medio de alquiler ({anio_top})")
top_df = (
    df_merged[df_merged[col_anio] == anio_top]
    .groupby(col_comunidad, as_index=False)[col_valor]
    .mean()
    .sort_values(by=col_valor, ascending=False)
    .head(5)
)
fig_top = px.bar(
    top_df, x=col_comunidad, y=col_valor, text_auto=".2f", color_continuous_scale="Plasma"
)
st.plotly_chart(fig_top, use_container_width=True)

# --------------------------------------------------------
# DESCARGA DE DATOS
# --------------------------------------------------------
st.subheader("💾 Descargar datos combinados filtrados")
csv = df_merged.to_csv(index=False)
st.download_button(
    label="⬇️ Descargar CSV",
    data=csv,
    file_name="alquiler_demografia_filtrado.csv",
    mime="text/csv"
)
