# Referencia del código — Dashboard ISO/IEC 38500:2024

Esta guía describe el archivo `dashboard_ISO38500/app.py`, sus constantes,
funciones y secciones. Sirve como mapa para mantener el código y para ubicar
dónde cambiar una regla de negocio.

## 1. Archivos del dashboard

| Archivo | Rol |
|---|---|
| `dashboard_ISO38500/app.py` | Dashboard completo: carga, cálculos y UI |
| `dashboard_ISO38500/Extraido_CIO_Completo.xlsx` | Copia local de respaldo de los datos |
| `dashboard_ISO38500/requirements.txt` | Dependencias y versiones mínimas |
| `dashboard_ISO38500/.streamlit/config.toml` | Tema visual local |
| `dashboard_ISO38500/iniciar.bat` | Lanzador para Windows |
| `dashboard_ISO38500/README.md` | Resumen de uso e instalación |
| `.streamlit/config.toml` (raíz) | Configuración usada por Streamlit Cloud |
| `docs/` | Esta documentación |
| `CHANGELOG.md` | Historial de versiones del dashboard |

## 2. Estructura del script

`app.py` se ejecuta de arriba hacia abajo. El orden es importante:

1. **Imports y configuración**: `st.set_page_config`, tema de Seaborn y
   `__version__`.
2. **Constantes ISO**: nombres bilingües, tareas, resultados, principios y
   colores.
3. **Funciones auxiliares**: carga, limpieza, formato, tablas y gráficos.
4. **Carga del Excel**: se ejecuta al importar el script.
5. **Preparación de datos**: construye todas las tablas y métricas.
6. **Barra lateral**: entidad, menú de secciones, botón de recarga y fuente.
7. **Secciones**: un bloque `if/elif` por cada sección del menú.

## 3. Constantes de configuración

| Constante | Uso |
|---|---|
| `__version__` | Versión visible en la barra lateral (`1.0.0`) |
| `ENTIDAD` | Nombre que aparece en la barra lateral (`Banco Unión`) |
| `COLORES_ESTADO` | Verde/ámbar/rojo para Cumple/Cerca/Bajo meta |
| `COLORES_NIVEL` | Colores para Alto/Medio/Bajo |
| `COLORES_EVIDENCIA` | Colores para Con evidencia/Evidencia parcial/Sin evidencia |
| `NOMBRES_ISO` | Traducción español → nombre bilingüe de la norma |
| `TAREAS_MODELO_ES` | Involucrar, Evaluar, Dirigir, Monitorear |
| `RESULTADOS_ISO_ES` | Desempeño efectivo, Administración responsable, Comportamiento ético |
| `PRINCIPIOS_ISO_ES` | Principios y sección de la norma (5.2 a 5.12) |
| `TAREAS_MODELO`, `RESULTADOS_ISO`, `PRINCIPIOS_ISO` | Versiones con nombre bilingüe derivadas de las anteriores |
| `COLUMNAS_DATOS` | Contrato de la hoja opcional `Inventario Datos` |
| `COLUMNAS_IA` | Contrato de la hoja opcional `Inventario IA` |
| `COLUMNAS_OPERACION` | Contrato de la hoja opcional `Operacion TI` |
| `ID_DRIVE`, `URLS_DRIVE`, `ARCHIVO_LOCAL` | Origen de datos y respaldo |
| `CLAVES_DATOS`, `CLAVES_IA` | Expresiones regulares para clasificar iniciativas por nombre |
| `DE`, `AR`, `CE` | Atajos de los tres resultados ISO |
| `TODOS` | Texto usado como origen de meta: "100% (todos los registros)" |

## 4. Funciones

### 4.1 Carga y limpieza

| Función | Qué hace | Notas |
|---|---|---|
| `cargar_excel()` | Descarga el Excel de Drive o usa el local | Cacheada 5 min; valida cabecera `PK` |
| `leer_hojas(contenido)` | Lee todas las hojas y las limpia | Quita columnas `Unnamed`, recorta encabezados y filas vacías |
| `leer_hoja_local(nombre)` | Lee una hoja del Excel local | Cacheada; se usa como respaldo |
| `hoja(nombre)` | Devuelve una copia de la hoja | Prioriza Drive; si no existe, usa local |
| `hoja_si_existe(nombre)` | Devuelve la hoja o `None` | Evita excepciones por hojas opcionales |
| `hoja_opcional(nombre, columnas)` | Devuelve una hoja o un DataFrame vacío con el contrato | No inventa datos |

### 4.2 Normalización y formato

| Función | Qué hace | Notas |
|---|---|---|
| `nombre_iso(serie)` | Convierte nombres en español al nombre bilingüe | Si ya está bilingüe o no está en el diccionario, lo deja igual |
| `numero(serie)` | Convierte texto a número | Acepta coma decimal (`"99,6"`) y punto (`"99.6"`) |
| `millones(valor)` | Formatea pesos en millones | Ejemplo: `$360 M` |
| `formato_numero(valor)` | Formatea números en estilo colombiano | `1234.5 → "1.234,5"` |
| `cumplimiento(actual, meta, menor_es_mejor=False)` | Calcula % de cumplimiento topado a 100 | Si `menor_es_mejor`, usa `meta / actual` |
| `estado(valor)` | Clasifica el cumplimiento | `>=100` Cumple, `>=85` Cerca, resto Bajo meta |

### 4.3 Tablas y gráficos

| Función | Qué hace |
|---|---|
| `mostrar_tabla(df, titulo=None, mostrar_indice=False)` | Tabla Streamlit con números formateados y altura según el contenido |
| `barras_horizontales(datos, colores=None, apiladas=True)` | Barras horizontales Matplotlib con etiquetas largas en varias líneas |
| `tabla_porcentaje(serie)` | Tabla de cantidad y porcentaje que acompaña a las donas |
| `grafico_dona(conteo, colores=None)` | Dona Matplotlib con el total al centro; devuelve la figura |
| `mostrar_evaluacion(evaluacion, titulo)` | Dona + barras apiladas + tabla de puntos evaluados |
| `pendiente(titulo, nombre_hoja, columnas, quien)` | Panel de información pendiente (**no se usa actualmente**) |

### 4.4 Métricas ISO

| Función | Qué hace | Notas |
|---|---|---|
| `iniciativas_por_tema(claves)` | Filtra DVP y PMO por palabras clave | Devuelve columnas homogéneas de ambos orígenes |
| `agregar_metrica(...)` | Agrega una fila a `metricas_iso` | Omite la métrica si `actual` es nulo |
| `agregar_bsc(...)` | Agrega una métrica tomada de la hoja BSC | Busca el indicador por nombre exacto |
| `porcentaje_con_dato(df, columna)` | % de filas con el campo diligenciado | Devuelve `None` si no hay filas |
| `porcentaje_si(df, columna)` | % de filas con valor `"Sí"` | Devuelve `None` si no hay filas |

## 5. Preparación de datos

El bloque de preparación se ejecuta antes de la barra lateral. Orden aproximado:

1. **Presupuesto**: detecta la fila de años (`Presupuesto 20...`) y convierte a
   formato largo (`Tipo`, `Año`, `Presupuesto`).
2. **BSC**: normaliza `Actual`, `Meta` y calcula `Cumplimiento %` con
   `cumplimiento()`.
3. **Inventarios opcionales**: datos, IA y operación.
4. **DVP**: renombra columnas mal escritas (`Presupuesto Proyeectado`,
   `TIempo estimado alto nivel (semanas)`), limpia textos y calcula `Millones`.
5. **PMO**: quita la fila de total, normaliza estados, une fechas de
   `Iniciativas` y calcula `Retraso (días)`.
6. **Maestra**: recorta `Tipo`, `Dominio`, `CadenaValor`, `Pilar`.
7. **Iniciativas de datos/IA**: primero desde hojas específicas, luego por
   palabras clave en DVP y PMO.
8. **Métricas ISO**: se agregan con `agregar_metrica` y `agregar_bsc`; cada una
   queda asociada a un principio, una tarea, un resultado y una fuente.
9. **Sustitución por hoja `ISO 38500`**: si existe y tiene las columnas mínimas,
   reemplaza las métricas calculadas.
10. **Sustitución por hojas `Gobierno de Datos`, `Gobierno IA` e
    `ISO 38500 Evaluacion`**.
11. **Riesgos y arquitectura**: rellena celdas combinadas y normaliza valores.

## 6. Secciones de la interfaz

| Sección | Contenido principal |
|---|---|
| Resumen | Filtros, línea de tiempo PMO, riesgos por frente, portafolio por tema, evaluación ISO |
| ISO 38500 | Cumplimiento por principio, estado de métricas, tareas del modelo, tabla de métricas, evaluación 4.1, plan de acción |
| Gobierno de Datos | Iniciativas de datos, presupuesto, riesgos de información, contexto, evaluación ISO de datos, inventario opcional |
| Gobierno de IA | Iniciativas de IA, presupuesto, dispersión duración/presupuesto, evaluación ISO de IA, inventario opcional |
| Operación TI | Indicadores de operación, servidores, aplicaciones, mesa de servicio |
| BSC | Cumplimiento por indicador y tabla filtrada por perspectiva |
| Portafolio | Iniciativas por dominio, estado PMO, retrasos, detalle |
| Innovación | Inversión por categoría e iniciativa, rupturas estratégicas |
| Riesgos | Filtros por frente/impacto, barras apiladas, dona, matriz |
| Arquitectura | Aplicaciones, servidores, instancias, sistemas operativos, dominios |
| Contexto | DOFA, Porter, indicadores del dominio TI |

## 7. Puntos de extensión

- **Nueva métrica ISO**: agregar una llamada a `agregar_metrica(...)` o
  `agregar_bsc(...)` en el bloque de métricas.
- **Nuevo principio**: agregarlo a `NOMBRES_ISO` y `PRINCIPIOS_ISO_ES`; la norma
  actual tiene 11.
- **Nuevo umbral de estado**: cambiar `estado()` (hoy 100 y 85).
- **Nueva sección**: agregar el nombre al `st.sidebar.radio` y un `elif` con el
  mismo nombre.
- **Nueva hoja opcional**: usar `hoja_opcional("Nombre", ["Columna1", ...])`.
- **Cambiar la fuente de datos**: editar `ID_DRIVE`, `URLS_DRIVE` y
  `ARCHIVO_LOCAL`.

## 8. Convenciones del código

- Nombres de funciones y variables en español; nombres de columnas del Excel
  conservan su escritura original (incluidas las erratas).
- Los encabezados se recortan con `.str.strip()`.
- Los textos se normalizan con `.str.strip()` y `.str.capitalize()`.
- Los números se convierten con `pd.to_numeric(..., errors="coerce")`.
- Las fechas se convierten con `pd.to_datetime(..., errors="coerce")`.
- Los datos faltantes se representan con `pd.NA` o `None`; no se rellenan con
  valores inventados.
- Las secciones de la UI se separan con comentarios `# ---- Sección ----`.
- Las funciones nuevas deben llevar docstring y, si aplica, una nota en este
  documento.
