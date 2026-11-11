# Dashboard TI

Dashboard estratégico de Gobierno y Servicios de TI, hecho en Python con Streamlit.
Reemplaza el reporte de Power BI y se actualiza solo desde un Excel en Google Drive.

## Páginas

- **Resumen**: presupuesto por año, BSC global, iniciativas, riesgos y retrasos.
- **Balanced Scorecard**: cumplimiento de cada indicador contra su meta.
- **Innovación y Transformación**: inversión de las iniciativas DVP y rupturas estratégicas.
- **Arquitectura Empresarial**: aplicaciones, servidores, sistemas operativos y dominios.
- **Portafolio Estratégico**: composición del portafolio, estado y retraso de los proyectos PMO.
- **Riesgos Estratégicos**: matriz de riesgos por frente e impacto.
- **Contexto estratégico**: DOFA, fuerzas de Porter e indicadores del dominio TI.
- **Calidad de datos**: inconsistencias encontradas en el Excel fuente.

## Cómo ejecutarlo

1. Instala Python 3.12 o superior.
2. Instala las librerías:
   ```
   pip install -r requirements.txt
   ```
3. Haz doble clic en `iniciar.bat`, o ejecuta:
   ```
   python -m streamlit run app.py
   ```
4. Se abre en el navegador en http://localhost:8501

## Fuente de datos

En `datos.py`:

- `URL_GOOGLE`: enlace del Excel en Google Drive, que debe estar compartido como "Cualquier persona con el enlace". Si se deja vacío (`""`), se usa el archivo local `Extraido_CIO_Completo.xlsx`.
- `MINUTOS_REFRESCO`: cada cuánto se vuelve a descargar desde Drive. El botón **Recargar datos** fuerza la descarga.

No cambies los nombres de las hojas ni de las columnas del Excel, porque el dashboard las busca por nombre.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `app.py` | El dashboard (páginas, gráficos y diseño) |
| `datos.py` | Lee y limpia el Excel y calcula los indicadores |
| `iniciar.bat` | Abre el dashboard con doble clic |
| `.streamlit/config.toml` | Tema de colores y configuración de Streamlit |
| `Extraido_CIO_Completo.xlsx` | Excel de respaldo con los datos |
