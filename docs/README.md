# Documentación — Dashboard ISO/IEC 38500:2024

Documentación técnica del proyecto **`dashboard_ISO38500`** y de su automatización
complementaria de evaluación de madurez en **n8n**. El alcance de esta
documentación es únicamente ese dashboard y esa automatización: su flujo, su
código, el contrato de los Excel que consumen y el proceso de versionado.

Los demás proyectos del repositorio no forman parte de esta documentación.

| Documento | Contenido |
|---|---|
| [Flujo automatizado](FLUJO_AUTOMATIZADO.md) | Arquitectura, origen de datos, caché, respaldo, despliegue y operación |
| [Referencia del código](REFERENCIA_CODIGO.md) | Constantes, funciones, preparación de datos, secciones y puntos de extensión |
| [Contrato de datos](CONTRATO_DATOS.md) | Hojas, columnas, vocabularios y reglas de calidad que espera el código |
| [Automatización n8n](AUTOMATIZACION_N8N.md) | Formulario, cálculo de madurez, salida y puesta en marcha del flujo ISO 38500 |
| [Validación y versionado](VALIDACION_VERSIONADO.md) | Revisión de cambios, hallazgos, SemVer, etiquetas y lista de publicación |
| [Historial de cambios](https://github.com/David02b/Gobierno_servicio_TI/blob/main/CHANGELOG.md) | Versiones y cambios del dashboard ISO 38500 |

## Descripción del dashboard

`dashboard_ISO38500` es una aplicación de Streamlit para medir el Gobierno de TI,
Gobierno de Datos e IA de una organización con base en la **ISO/IEC 38500:2024**.
Lee un Excel publicado en Google Drive (con copia local de respaldo) y presenta:

- métricas asociadas a los 11 principios de la sección 5 de la norma;
- las 4 tareas del modelo de gobierno de la sección 6.2
  (Involucrar, Evaluar, Dirigir, Monitorear);
- los 3 resultados del buen gobierno de TI de la sección 4.1
  (Desempeño efectivo, Administración responsable, Comportamiento ético);
- evaluación de evidencia de los 16 puntos de la sección 4.1;
- brechas y plan de acción, portafolio, riesgos, arquitectura, BSC y contexto.

Tecnologías: Python, Streamlit, Pandas, Matplotlib y Seaborn.

## Versión documentada

- Versión del dashboard: **1.0.0** (ver
  [CHANGELOG](https://github.com/David02b/Gobierno_servicio_TI/blob/main/CHANGELOG.md)).
- Fecha de esta revisión: **2026-11-18**.
- Último commit de código revisado: `b0efb96` — *Ajuste del tamaño de tablas y
  gráficos al contenido*.

## Inicio rápido

```powershell
cd dashboard_ISO38500
pip install -r requirements.txt
python -m streamlit run app.py
```

En Windows también se puede hacer doble clic en `iniciar.bat`.

> **Importante:** los nombres de las hojas y de las columnas del Excel son parte
> del contrato de datos. Si se renombran, el dashboard deja de encontrar la
> información. Ver [CONTRATO_DATOS.md](CONTRATO_DATOS.md).
