# Validación y versionado — Dashboard ISO/IEC 38500:2024

## 1. Alcance de la revisión

| Elemento | Valor |
|---|---|
| Proyecto revisado | `dashboard_ISO38500` |
| Fecha | 2026-11-18 |
| Commit de código revisado | `b0efb96` — *Ajuste del tamaño de tablas y gráficos al contenido* |
| Rama | `main` |
| Remoto | `https://github.com/MonicaGalvis27/Gobierno_servicios_TI.git` |
| Versión propuesta | **1.0.0** |
| Estado del árbol antes de esta revisión | Limpio (`git status` sin cambios) |

Esta revisión cubre únicamente el dashboard ISO/IEC 38500:2024: su aplicación,
su lógica de datos, el contrato del Excel que consume y su documentación.

## 2. Cambios validados

| Commit | Fecha | Cambio | Impacto en el dashboard ISO |
|---|---|---|---|
| `7fd4e24` | 2026-11-17 | Versión inicial | Crea el dashboard, Excel, README y requirements |
| `50e5864` | 2026-11-17 | Configuración para Streamlit Cloud | `.streamlit/config.toml` y versiones mínimas |
| `3ea01e6` | 2026-11-18 | Corrección de datos y secciones | Actualiza Excel y simplifica secciones |
| `9ae12d2` | 2026-11-18 | Plan de acción desde Excel | Lee la hoja `Plan de accion`; deja el cálculo como respaldo |
| `a8a5074` | 2026-11-18 | Nombres ISO bilingües | Agrega `NOMBRES_ISO` y normaliza principios, resultados y tareas |
| `b0efb96` | 2026-11-18 | Tamaño de tablas y gráficos | Reemplaza `st.dataframe`/`st.write` por `mostrar_tabla` y `barras_horizontales` |

Los commits iniciales de otros proyectos del repositorio no forman parte de esta
revisión.

## 3. Comprobaciones realizadas

### 3.1 Estructura del proyecto

- [x] El dashboard tiene `app.py`, Excel local, `requirements.txt`,
      `.streamlit/config.toml`, `iniciar.bat` y `README.md`.
- [x] El repositorio tiene un único remoto y una sola rama (`main`).
- [x] No existían etiquetas (`tags`) de versión; se creó `v1.0.0`.
- [x] `.gitignore` excluye `__pycache__`, `.venv`, temporales de Excel,
      `PETI/` y `hojas_para_drive/`.
- [x] El libro de Excel del dashboard está versionado en
      `dashboard_ISO38500/Extraido_CIO_Completo.xlsx`.

### 3.2 Análisis estático

Se ejecutó `pyright` sobre `dashboard_ISO38500/app.py`. Resultado:

- **Sin errores de sintaxis**: el archivo se parsea correctamente.
- 3 errores y 1 advertencia, todos por imports no resueltos (`pandas`,
  `streamlit`, `matplotlib`; `seaborn` sin código fuente) porque las
  dependencias no están instaladas en esta máquina. No hay errores de lógica
  detectados por el analizador.

### 3.3 Validación del Excel

Se abrió el `.xlsx` como archivo ZIP y se leyó `xl/workbook.xml` para verificar
las hojas reales:

- **22 hojas** en total.
- Todas las hojas obligatorias están presentes.
- Las hojas opcionales `Inventario Datos`, `Inventario IA` y `Operacion TI`
  **no existen** todavía; el código las trata como vacías.
- Las hojas `ISO 38500`, `ISO 38500 Evaluacion`, `Gobierno de Datos`,
  `Gobierno IA` y `Plan de accion` **sí existen**, por lo que el dashboard usa
  los datos oficiales en lugar de los cálculos de respaldo.

Conteos verificados:

| Hoja | Filas con datos | Interpretación |
|---|---:|---|
| `ISO 38500` | 20 | 1 encabezado + 19 métricas |
| `ISO 38500 Evaluacion` | 17 | 1 encabezado + 16 puntos |
| `Plan de accion` | 4 | 1 encabezado + 3 acciones |
| `Gobierno de Datos` | 13 | 1 encabezado + 12 registros |
| `Gobierno IA` | 5 | 1 encabezado + 4 registros |
| `BSC` | 12 | 1 encabezado + 11 indicadores |
| `Riesgos` | 25 | 1 encabezado + 24 riesgos |
| `Detalle iniciativa pmo` | 27 | 1 encabezado + 26 proyectos + total |
| `Detalle iniciativa DVP` | 28 | 1 encabezado + 27 iniciativas |
| `MAESTRA_INICIATIVAS` | 52 | 1 encabezado + 51 iniciativas |

### 3.4 Contraste código ↔ datos

| Punto revisado | Resultado |
|---|---|
| `ISO 38500` tiene las 4 columnas mínimas (`Principio`, `Actual`, `Meta`, `Menor es mejor`) | ✅ Se usa la hoja oficial |
| `ISO 38500 Evaluacion` usa `Punto` y `Evidencia`; el código también acepta `Traducción` y `Evidencia en el banco` | ✅ Compatible |
| `Plan de accion` ya usa nombres bilingües; el `rename` del código no hace daño | ✅ Compatible |
| `Gobierno de Datos` tiene `Tipo de registro`, `Categoría o componente`, `Impacto` | ✅ Se usa la hoja oficial |
| `Gobierno IA` tiene `Hoja de origen`, `Categoría o gerencia`, `Semanas` | ✅ Se usa la hoja oficial |
| `Detalle iniciativa pmo` tiene `MEGA`, `Objetivo Estrategico`, `Sponsor`, `Gerente` | ✅ Métricas ISO calculables |
| `BSC` tiene los indicadores usados por ISO (`Costo Total Propiedad TI`, `Automatización`, etc.) | ✅ Métricas ISO calculables |
| Hojas opcionales de inventario/operación | ⚠️ Ausentes; secciones quedan vacías o pendientes |

### 3.5 Consistencia de documentación

| Hallazgo | Acción |
|---|---|
| El README de `dashboard_ISO38500` listaba "Calidad de datos", pero esa sección no existe en la app | Corregido: se reemplazó por la lista real de secciones |
| El README no explicaba el origen de datos, el respaldo ni el contrato del Excel | Se agregó enlace a esta documentación |
| No existía un documento de arquitectura ni de contrato de datos | Creados en `docs/` |
| No existía documentación de la automatización de madurez en n8n | Creada en `docs/EVALUACION_DE_MADUREZ.md` |
| No existía `CHANGELOG.md` | Creado con el historial del dashboard ISO |

## 4. Hallazgos y recomendaciones

| Prioridad | Hallazgo | Recomendación |
|---|---|---|
| **Alta** | El Excel con información interna del banco está versionado en el repositorio | Verificar si el repositorio es público; si lo es, mover el Excel a almacenamiento privado o usar datos anonimizados |
| **Alta** | No hay pruebas automatizadas ni CI | Agregar al menos una prueba de humo que valide hojas y columnas obligatorias |
| **Media** | No se pudo ejecutar la app en esta revisión (Python no está instalado en el entorno) | Ejecutar `streamlit run app.py` en una máquina con dependencias antes de etiquetar |
| **Media** | `app.py` supera las 1.000 líneas y mezcla carga, cálculo y UI | Evaluar separar la lógica de datos en un módulo `datos.py` |
| **Baja** | `pendiente()` no se usa | Eliminarla o usarla en las secciones pendientes |
| **Baja** | `cumplimiento()` divide por cero si `meta` o `actual` es cero | Agregar guardas y devolver `None` |
| **Baja** | `leer_hoja_local()` se cachea sin TTL ni clave de fecha | Incluir `mtime` en la clave o limpiar la caché al recargar |
| **Baja** | Hojas opcionales de inventario y operación ausentes | Completarlas en el Excel cuando el banco tenga los datos |

Los dos primeros hallazgos deben resolverse antes de una publicación amplia.

## 5. Versionado propuesto

### 5.1 Esquema

Se usa **SemVer** (`MAYOR.MENOR.PARCHE`):

- **MAYOR**: cambios incompatibles en el contrato de datos o en la forma de
  consumir el dashboard.
- **MENOR**: nuevas secciones, nuevas métricas o nuevas hojas compatibles.
- **PARCHE**: correcciones de cálculos, textos, estilos o errores.

Versión actual: **1.0.0**, porque el dashboard ya está publicado en Streamlit
Cloud y su contrato de datos está estable.

### 5.2 Convención de commits

Se recomienda Conventional Commits:

```text
feat(iso38500): agregar métrica de gobierno del riesgo
fix(iso38500): corregir cálculo de retraso PMO
docs(iso38500): actualizar contrato de datos
chore: actualizar requirements
```

Tipos sugeridos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

### 5.3 Ramas

```text
main          # estable, protegida
feat/...      # nueva funcionalidad
fix/...       # corrección
docs/...      # documentación
```

### 5.4 Etiquetas

Después de aprobar y probar una versión:

```powershell
git tag -a v1.0.0 -m "Dashboard Gobierno de TI ISO/IEC 38500:2024 v1.0.0"
git push origin main
git push origin v1.0.0
```

### 5.5 CHANGELOG

Actualizar `CHANGELOG.md` antes de cada etiqueta. El formato recomendado es
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/):

- `Agregado` para funcionalidad nueva.
- `Cambiado` para cambios de comportamiento.
- `Corregido` para errores.
- `Eliminado` para funcionalidad retirada.
- `Seguridad` para vulnerabilidades.

## 6. Lista de verificación para publicar

Antes de crear una etiqueta:

- [ ] `git status` limpio.
- [ ] `pip install -r dashboard_ISO38500/requirements.txt` sin errores.
- [ ] `python -m streamlit run dashboard_ISO38500/app.py` abre sin excepciones.
- [ ] La barra lateral muestra la fuente correcta (Google Drive o Excel local).
- [ ] Las 11 secciones del dashboard se abren sin errores.
- [ ] Las hojas obligatorias existen y conservan sus nombres.
- [ ] El `CHANGELOG.md` describe los cambios de la versión.
- [ ] La versión de la app coincide con la etiqueta.
- [ ] El repositorio no expone datos sensibles si es público.

## 7. Próximos pasos sugeridos

1. Resolver la exposición del Excel (privacidad).
2. Ejecutar la app con dependencias instaladas y registrar la evidencia.
3. Crear la etiqueta `v1.0.0`.
4. Agregar una prueba de humo del contrato de datos.
5. Evaluar la separación de la lógica de datos en un módulo propio.
