# Changelog — Dashboard ISO/IEC 38500:2024

Todos los cambios relevantes de `dashboard_ISO38500` se documentan en este
archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el versionado sigue [SemVer](https://semver.org/lang/es/).

## [Unreleased]

### Agregado

- Documentación técnica del dashboard en `docs/`: flujo automatizado,
  referencia del código, contrato de datos y validación/versionado.
- `__version__` y docstrings en `dashboard_ISO38500/app.py`.
- Versión visible en la barra lateral del dashboard.
- Configuración para publicar esta documentación en GitBook
  (`.gitbook.yaml` y `docs/SUMMARY.md`).

### Corregido

- El README de `dashboard_ISO38500` listaba una sección "Calidad de datos" que
  no existe en la aplicación; se reemplazó por las secciones reales.
- El README de `dashboard_ISO38500` ahora explica el origen de datos, el
  respaldo local y el contrato del Excel, y enlaza esta documentación.

## [1.0.0] - 2026-11-18

Primera versión estable documentada del dashboard de Gobierno de TI
ISO/IEC 38500:2024. Lee sus datos de un Excel en Google Drive, con respaldo
local.

### Agregado

- 11 secciones: Resumen, ISO 38500, Gobierno de Datos, Gobierno de IA,
  Operación TI, BSC, Portafolio, Innovación, Riesgos, Arquitectura y Contexto.
- Métricas de los 11 principios de la sección 5 de la norma.
- Tareas del modelo de gobierno de la sección 6.2 (Involucrar, Evaluar,
  Dirigir, Monitorear).
- Resultados del buen gobierno de TI de la sección 4.1 (Desempeño efectivo,
  Administración responsable, Comportamiento ético).
- Evaluación de evidencia de los 16 puntos de la sección 4.1.
- Brechas y plan de acción leídos de la hoja `Plan de accion`.
- Inventarios opcionales de datos, IA y operación.
- Lectura del Excel desde Google Drive con dos URLs de descarga y validación de
  cabecera `PK`.
- Respaldo automático al Excel local cuando Drive falla o no está disponible.
- Caché de datos de 5 minutos y botón **Recargar datos**.
- Configuración para publicar en Streamlit Community Cloud.
- `iniciar.bat` para ejecución local en Windows.

### Cambiado

- Nombres de principios, resultados y tareas de la ISO/IEC 38500:2024 en
  español y en el nombre original del documento.
- Tablas y gráficos ajustados al contenido, con formato de números colombiano.
- Versiones mínimas de dependencias fijadas en
  `dashboard_ISO38500/requirements.txt`.
- Plan de acción leído desde la hoja `Plan de accion` del Excel, con cálculo de
  respaldo si la hoja no existe.

### Corregido

- Datos del Excel de `dashboard_ISO38500` actualizados y secciones
  simplificadas.
- Estados de PMO normalizados (`En Proceso` / `En proceso`).
- Riesgos normalizados (`Moderado` se trata como `Medio`).
- Celdas combinadas de `FRENTE` y `COMPONENTE` rellenadas hacia abajo.
- Fila de total de PMO excluida de los cálculos.
- Columnas vacías (`Unnamed`) y filas vacías eliminadas.
- Valores `#REF!` tratados como nulos.
- Números con coma decimal aceptados.

### Seguridad

- `gatherUsageStats = false` para no enviar estadísticas de uso a Streamlit.
- La aplicación es de solo lectura: no escribe en Google Drive ni en el Excel.

[Unreleased]: https://github.com/MonicaGalvis27/Gobierno_servicios_TI/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/MonicaGalvis27/Gobierno_servicios_TI/releases/tag/v1.0.0
