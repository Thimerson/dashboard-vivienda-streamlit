# 🏘️ Dashboard Final — Índice de Alquiler, Demografía y Vivienda en España

Este repositorio contiene el código fuente de un dashboard desarrollado en **Python/Streamlit** para el análisis integral del mercado de vivienda en España, incluyendo datos demográficos y precios históricos.

## 📋 Características principales

- Limpieza y normalización robusta de datasets CSV
- Unificación de datos de alquiler, vivienda y demografía por comunidad autónoma y año
- Filtros interactivos por comunidad, rango de años y tipo de variable
- Visualizaciones avanzadas con **Plotly**: líneas históricas, dispersión, mapas y correlaciones
- Modelo estadístico de correlación y regresión lineal múltiple
- Botón de descarga para exportar los datos combinados y filtrados

## 📁 Estructura del Repositorio

El proyecto está organizado en las siguientes carpetas y archivos:

```
dashboard-vivienda-streamlit/
├── src/
│   ├── app_vivienda_final.py    # Aplicación principal del dashboard
│   └── .gitkeep
├── data/
│   ├── alquiler/                # Datos de índices de alquiler
│   │   └── indices_alquiler.csv
│   ├── demografia/              # Datos demográficos y de vivienda
│   │   ├── df_mineria_datos_edades.csv
│   │   └── df_mineria_datos_vivienda.csv
│   └── transmisiones/           # Datos de transmisiones y tasaciones
│       ├── transmisiones.csv
│       └── tasaciones_inmobiliarias.csv
├── tests/
│   └── test_data_processing.py  # Tests unitarios para procesamiento de datos
├── .gitignore                   # Archivos y carpetas ignorados por Git
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Este archivo
```

### Descripción de Carpetas

**`src/`**: Contiene el código fuente de la aplicación
- `app_vivienda_final.py`: Script principal que ejecuta el dashboard Streamlit

**`data/`**: Almacena los archivos CSV organizados por categoría
- **`alquiler/`**: Datos sobre índices de precios de alquiler
- **`demografia/`**: Información demográfica y estadísticas de vivienda
- **`transmisiones/`**: Datos de transacciones inmobiliarias y tasaciones

**`tests/`**: Contiene pruebas unitarias
- `test_data_processing.py`: Tests para validar el procesamiento de datos

**Archivos Clave**:
- **`.gitignore`**: Especifica qué archivos/carpetas no deben versionarse (ej. datos sensibles, caché)
- **`requirements.txt`**: Lista todas las dependencias Python necesarias para el proyecto

## 🚀 Cómo Ejecutar el Dashboard

### 1. Clona el repositorio

```bash
git clone https://github.com/Thimerson/dashboard-vivienda-streamlit.git
cd dashboard-vivienda-streamlit
```

### 2. Instala las dependencias

```bash
pip install -r requirements.txt
```

**Dependencias incluidas**: streamlit, pandas, numpy, plotly, scikit-learn, unidecode, requests

### 3. Prepara los datos

Coloca tus archivos CSV en las rutas correspondientes dentro de la carpeta `data/`:

**Ejemplo de rutas para los archivos CSV:**

```
data/alquiler/indices_alquiler.csv
data/demografia/df_mineria_datos_edades.csv
data/demografia/df_mineria_datos_vivienda.csv
data/transmisiones/transmisiones.csv
data/transmisiones/tasaciones_inmobiliarias.csv
```

**Nota**: Si tus archivos CSV están en otras ubicaciones, puedes ajustar las rutas en el archivo `src/app_vivienda_final.py`.

### 4. Ejecuta el dashboard

Desde la raíz del proyecto, ejecuta:

```bash
streamlit run src/app_vivienda_final.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`.

## 🧪 Ejecutar Tests

Para ejecutar las pruebas unitarias:

```bash
python -m pytest tests/
```

O ejecuta un test específico:

```bash
python -m pytest tests/test_data_processing.py
```

## 📊 Ejemplo de Visualizaciones

<img width="827" height="450" alt="image" src="https://github.com/user-attachments/assets/cad107e2-7b9a-4bf6-bf85-81134293f4a7" />

## 👥 Colaboradores

- **Autor**: Thimerson Ramirez

## 📝 Notas Adicionales

- Asegúrate de que los archivos CSV tengan el formato esperado (columnas necesarias para el análisis)
- El dashboard permite filtrar y exportar datos procesados
- Los datos se normalizan automáticamente durante la carga

---

**¿Preguntas o sugerencias?** Abre un [issue](https://github.com/Thimerson/dashboard-vivienda-streamlit/issues) en este repositorio.
