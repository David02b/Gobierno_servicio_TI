# Gobierno y Servicios de TI

Repositorio de proyectos de gobierno y servicios de TI.

| Proyecto | Descripción |
|---|---|
| [dashboardTI](dashboardTI/) | Dashboard estratégico de TI (Streamlit) que lee los datos desde Excel / Google Drive |
| [dashboard_ISO38500](dashboard_ISO38500/) | Dashboard de métricas de Gobierno de TI, Datos e IA según la ISO/IEC 38500:2024 |

## Documentación

La documentación de este repositorio cubre **únicamente** el dashboard
`dashboard_ISO38500` y su automatización de evaluación de madurez en n8n
(versión documentada: **1.0.0**, ver [CHANGELOG](CHANGELOG.md)).

| Documento | Contenido |
|---|---|
| [docs/README.md](docs/README.md) | Índice y descripción del dashboard ISO 38500 |
| [docs/FLUJO_AUTOMATIZADO.md](docs/FLUJO_AUTOMATIZADO.md) | Arquitectura, origen de datos, caché, respaldo y operación |
| [docs/REFERENCIA_CODIGO.md](docs/REFERENCIA_CODIGO.md) | Constantes, funciones, preparación de datos y puntos de extensión |
| [docs/CONTRATO_DATOS.md](docs/CONTRATO_DATOS.md) | Hojas, columnas y reglas de calidad del Excel |
| [docs/AUTOMATIZACION_N8N.md](docs/AUTOMATIZACION_N8N.md) | Flujo de evaluación de madurez en n8n, entrada, cálculo y salida |
| [docs/VALIDACION_VERSIONADO.md](docs/VALIDACION_VERSIONADO.md) | Validación de cambios, SemVer, etiquetas y publicación |
| [CHANGELOG.md](CHANGELOG.md) | Historial de versiones del dashboard ISO 38500 |

## Inicio rápido

```powershell
# Dashboard ISO/IEC 38500:2024
cd dashboard_ISO38500
pip install -r requirements.txt
python -m streamlit run app.py
```

En Windows también se puede hacer doble clic en `dashboard_ISO38500/iniciar.bat`.
