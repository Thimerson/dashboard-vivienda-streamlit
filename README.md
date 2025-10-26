# 🏘️ Dashboard Final — Índice de Alquiler, Demografía y Vivienda en España

Este repositorio contiene el código fuente de un dashboard desarrollado en **Python/Streamlit** para el análisis integral del mercado de vivienda en España, incluyendo datos demográficos y precios históricos.

Características principales

- Limpieza y normalización robusta de datasets CSV
- Unificación de datos de alquiler, vivienda y demografía por comunidad autónoma y año
- Filtros interactivos por comunidad, rango de años y tipo de variable
- Visualizaciones avanzadas con **Plotly**: líneas históricas, dispersión, mapas y correlaciones
- Modelo estadístico de correlación y regresión lineal múltiple  
- Botón de descarga para exportar los datos combinados y filtrados

Cómo ejecutar el dashboard

1. Instala dependencias
(o instala manualmente: streamlit, pandas, numpy, plotly, scikit-learn, unidecode, requests)

2. Coloca tus archivos CSV en la ruta indicada o instala manualmente: streamlit, pandas, numpy, plotly, scikit-learn, unidecode, requests)

3. Coloca tus archivos CSV en la ruta indicada O ajusta las rutas en el script según tu carpeta

4. Ejecuta el dashboard

Estructura de archivos
dashboard-vivienda-streamlit/
├── app_vivienda_final.py
├── requirements.txt
├── README.md
├── /Modulo 1/
│ ├── indices_alquiler.csv
│ ├── df_mineria_datos_edades.csv
│ └── df_mineria_datos_vivienda.csv
├── /Modulo 2/
│ ├── transmisiones.csv
│ └── tasaciones_inmobiliarias.csv
└── .gitignore

Ejemplo de visualizaciones

<img width="827" height="450" alt="image" src="https://github.com/user-attachments/assets/cad107e2-7b9a-4bf6-bf85-81134293f4a7" />


Colaboradores

- Autor:Thimerson Ramirez  


Licencia

Este proyecto se distribuye bajo la licencia MIT.

---




