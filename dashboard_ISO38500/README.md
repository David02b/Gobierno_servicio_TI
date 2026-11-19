# Dashboard ISO/IEC 38500:2024

Dashboard estratégico de métricas de Gobierno de TI, Gobierno de Datos e IA,
basado en la ISO/IEC 38500:2024.

Hecho con Python, Streamlit, Pandas, Matplotlib y Seaborn. Los datos se leen de
un Excel en Google Drive, con copia local de respaldo.

Versión: **1.0.0** · Ver [CHANGELOG](../CHANGELOG.md).

## Secciones

- Resumen
- ISO 38500
- Gobierno de Datos
- Gobierno de IA
- Operación TI
- BSC
- Portafolio
- Innovación
- Riesgos
- Arquitectura
- Contexto

## Instalación

```
pip install -r requirements.txt
```

## Ejecución

```
streamlit run app.py
```

En Windows también se puede abrir con doble clic en `iniciar.bat`.

## Fuente de datos

- El Excel se descarga desde Google Drive (ID configurado en `app.py`).
- Si no hay internet o Drive no responde, se usa `Extraido_CIO_Completo.xlsx`.
- Los datos se refrescan cada 5 minutos o al pulsar **Recargar datos**.
- No cambies los nombres de las hojas ni de las columnas: el dashboard las busca
  por nombre exacto.

El contrato completo de hojas y columnas está en
[docs/CONTRATO_DATOS.md](../docs/CONTRATO_DATOS.md). La arquitectura y el flujo
automatizado están en
[docs/FLUJO_AUTOMATIZADO.md](../docs/FLUJO_AUTOMATIZADO.md).
