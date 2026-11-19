import io  # Leer el archivo descargado en memoria
import urllib.request  # Descargar el Excel desde Google Drive
from pathlib import Path  # Manejo de rutas de archivos

import matplotlib.pyplot as plt  # Visualización de datos en Python
import pandas as pd  # Manipulación y análisis de datos
import seaborn as sns  # Interfaz para visualización de datos estadísticos (Integra con Pandas)
import streamlit as st  # Librería para crear aplicaciones web interactivas en Python

# Configuración de la página
st.set_page_config(page_title="Dashboard TI", layout="wide")
sns.set_theme(style="whitegrid")

ENTIDAD = "Banco Unión"

# Colores para los niveles
COLORES_ESTADO = {"Cumple": "#2ca02c", "Cerca": "#ff7f0e", "Bajo meta": "#d62728"}
COLORES_NIVEL = {"Alto": "#d62728", "Medio": "#ff7f0e", "Bajo": "#2ca02c"}
COLORES_EVIDENCIA = {"Con evidencia": "#2ca02c", "Evidencia parcial": "#ff7f0e", "Sin evidencia": "#d62728"}

# ISO/IEC 38500:2024 - modelo de gobierno (6.2) y resultados del buen gobierno de TI (4.1)
TAREAS_MODELO = ["Involucrar", "Evaluar", "Dirigir", "Monitorear"]
RESULTADOS_ISO = ["Desempeño efectivo", "Administración responsable", "Comportamiento ético"]
PRINCIPIOS_ISO = {  # Sección 5 de la norma
    "Propósito": "5.2", "Generación de valor": "5.3", "Estrategia": "5.4", "Supervisión": "5.5",
    "Rendición de cuentas": "5.6", "Involucramiento de partes interesadas": "5.7", "Liderazgo": "5.8",
    "Datos y decisiones": "5.9", "Gobierno del riesgo": "5.10", "Responsabilidad social": "5.11",
    "Viabilidad y desempeño en el tiempo": "5.12",
}

# Columnas de las hojas que el banco debe llenar
COLUMNAS_DATOS = ["Dominio", "Activo de datos", "Clasificación", "Responsable asignado", "Catalogado",
                  "Calidad %", "Completitud %"]
COLUMNAS_IA = ["Caso de uso", "Área", "Estado", "Riesgo IA", "Evaluación ética", "Monitoreado", "Precisión %"]
COLUMNAS_OPERACION = ["Mes", "Tipo", "Canal", "Cantidad"]


# Cargar el conjunto de datos desde Google Drive
# (si no hay internet se usa la copia local del Excel)
ID_DRIVE = "15VJEg5OykTfv99NhHynsoqQfdea0ij2m"
URLS_DRIVE = [
    f"https://docs.google.com/spreadsheets/d/{ID_DRIVE}/export?format=xlsx",
    f"https://drive.google.com/uc?export=download&id={ID_DRIVE}",
]
ARCHIVO_LOCAL = Path(__file__).parent / "Extraido_CIO_Completo.xlsx"


@st.cache_data(ttl=300)  # Se vuelve a descargar cada 5 minutos
def cargar_excel():
    for url in URLS_DRIVE:
        try:
            with urllib.request.urlopen(url, timeout=20) as respuesta:
                contenido = respuesta.read()
            if contenido[:2] == b"PK":  # Los archivos .xlsx empiezan por "PK"
                return contenido, "Google Drive"
        except Exception:
            pass
    return ARCHIVO_LOCAL.read_bytes(), "Excel local"


@st.cache_data(ttl=300)
def leer_hojas(contenido):
    hojas = pd.read_excel(io.BytesIO(contenido), sheet_name=None)
    for nombre, df in hojas.items():
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]  # Quitar columnas vacías
        df.columns = [str(c).strip() for c in df.columns]
        hojas[nombre] = df.dropna(how="all")
    return hojas


@st.cache_data
def leer_hoja_local(nombre):
    return pd.read_excel(ARCHIVO_LOCAL, sheet_name=nombre)


with st.spinner("Cargando datos..."):
    contenido, fuente = cargar_excel()
    hojas = leer_hojas(contenido)
    presupuesto_raw = pd.read_excel(io.BytesIO(contenido), sheet_name="Presupuesto proyect", header=None)


def hoja(nombre):
    # Usa la hoja de Drive; si todavía no existe allá, la toma del Excel local
    if nombre in hojas:
        return hojas[nombre].copy()
    return leer_hoja_local(nombre)


def numero(serie):
    # Convierte a número aceptando "99.6" o "99,6" (Google Sheets en español usa coma decimal)
    return pd.to_numeric(serie.astype(str).str.replace(",", ".", regex=False).str.strip(), errors="coerce")


def millones(valor):
    return "$" + f"{valor / 1_000_000:,.0f}".replace(",", ".") + " M"


def cumplimiento(actual, meta, menor_es_mejor=False):
    # Porcentaje de cumplimiento frente a la meta (máximo 100%)
    if menor_es_mejor:
        return min(meta / actual * 100, 100)
    return min(actual / meta * 100, 100)


def estado(valor):
    if valor >= 100:
        return "Cumple"
    if valor >= 85:
        return "Cerca"
    return "Bajo meta"


def tabla_porcentaje(serie):
    # Tabla con cantidad y porcentaje, como la que acompaña a las donas
    tabla = serie.value_counts().rename("Cantidad").to_frame()
    tabla["%"] = (tabla["Cantidad"] / tabla["Cantidad"].sum() * 100).round(1)
    return tabla


def grafico_dona(conteo, colores=None):
    # Gráfico de dona con el total en el centro
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(conteo, colors=colores, startangle=90, counterclock=False,
           wedgeprops={"width": 0.35, "edgecolor": "white"}, autopct="%1.0f%%", pctdistance=0.82)
    ax.text(0, 0, f"{conteo.sum()}\nTotal", ha="center", va="center", fontsize=14)
    return fig


def hoja_opcional(nombre, columnas):
    # Hojas que el banco debe llenar; si no existen o están vacías, quedan vacías (no se inventan datos)
    try:
        df = hoja(nombre)
    except Exception:
        df = pd.DataFrame(columns=columnas)
    for col in columnas:
        if col not in df.columns:
            df[col] = pd.NA
    return df.dropna(how="all")


def mostrar_evaluacion(evaluacion, titulo):
    # Muestra los puntos de la sección 4.1 de la norma con su estado de evidencia
    with st.container(border=True):
        st.markdown(f"**{titulo}**")
        conteo = evaluacion["Estado"].value_counts().reindex(COLORES_EVIDENCIA.keys()).dropna().astype(int)
        col1, col2 = st.columns([2, 3])
        with col1:
            # Gráfico de dona con el estado de la evidencia
            fig = grafico_dona(conteo, [COLORES_EVIDENCIA[e] for e in conteo.index])
            st.pyplot(fig)
            plt.close(fig)
        with col2:
            # Gráfico de barras apiladas: estado por resultado de la norma
            por_resultado = evaluacion.groupby(["Resultado", "Estado"]).size().unstack(fill_value=0)
            por_resultado = por_resultado.reindex(columns=[c for c in COLORES_EVIDENCIA if c in por_resultado.columns])
            st.bar_chart(por_resultado, horizontal=True, color=[COLORES_EVIDENCIA[c] for c in por_resultado.columns])
        # Mostrar los puntos evaluados
        with st.expander("Ver puntos evaluados"):
            st.dataframe(evaluacion[["Resultado", "Punto", "Estado", "Evidencia"]], hide_index=True)


def pendiente(titulo, nombre_hoja, columnas, quien):
    # Panel para la información que todavía no está en el Excel (no se inventan datos)
    with st.container(border=True):
        st.markdown(f"**{titulo} - pendiente**")
        st.write(f"Esta información no está en el Excel. Se obtiene de: {quien}. "
                 f"Cuando se llene la hoja '{nombre_hoja}', aquí aparecen sus gráficos.")
        st.write("Columnas de la hoja:", pd.DataFrame(columns=columnas))


# Preparar los datos de cada hoja

# Presupuesto por año y tipo de iniciativa
fila_anios = presupuesto_raw.index[presupuesto_raw.astype(str).apply(
    lambda fila: fila.str.contains("Presupuesto 20").any(), axis=1)][0]
columnas_anio = {i: int(str(v).replace("Presupuesto", "").strip())
                 for i, v in presupuesto_raw.loc[fila_anios].items() if "Presupuesto 20" in str(v)}
filas = []
for _, fila in presupuesto_raw.loc[fila_anios + 1:].iterrows():
    tipo = str(fila[0]).strip()
    if tipo == "nan" or tipo.lower().startswith("global"):
        continue
    for i, anio in columnas_anio.items():
        filas.append({"Tipo": tipo.replace("Iniciativas ", ""), "Año": anio,
                      "Presupuesto": pd.to_numeric(fila[i], errors="coerce")})
presupuesto = pd.DataFrame(filas).fillna(0)

# Balanced Scorecard
bsc = hoja("BSC")
bsc["Actual"] = pd.to_numeric(bsc["Actual"], errors="coerce")
bsc["Meta"] = pd.to_numeric(bsc["Meta"], errors="coerce")
bsc["Cumplimiento %"] = [cumplimiento(a, m, i.strip() == "Costo Total Propiedad TI")
                         for a, m, i in zip(bsc["Actual"], bsc["Meta"], bsc["Indicador"])]

# Gobierno de datos, IA y operación de TI (hojas que se llenan con datos reales del banco)
gobierno_datos = hoja_opcional("Inventario Datos", COLUMNAS_DATOS)
gobierno_datos["Calidad %"] = numero(gobierno_datos["Calidad %"])
gobierno_datos["Completitud %"] = numero(gobierno_datos["Completitud %"])
gobierno_ia = hoja_opcional("Inventario IA", COLUMNAS_IA)
gobierno_ia["Precisión %"] = numero(gobierno_ia["Precisión %"])
operacion = hoja_opcional("Operacion TI", COLUMNAS_OPERACION)
operacion["Cantidad"] = numero(operacion["Cantidad"])
operacion["Mes"] = pd.to_datetime(operacion["Mes"], errors="coerce").dt.strftime("%Y-%m")  # Año-mes, ej. 2026-01

# Iniciativas de transformación digital (DVP)
dvp = hoja("Detalle iniciativa DVP").rename(columns={
    "Iniciativa- proyecto": "Iniciativa",
    "Presupuesto Proyeectado": "Presupuesto",
    "TIempo estimado alto nivel (semanas)": "Semanas",
})
dvp = dvp[dvp["Iniciativa"].notna()].copy()
dvp["Iniciativa"] = dvp["Iniciativa"].str.strip()
dvp["Presupuesto"] = pd.to_numeric(dvp["Presupuesto"], errors="coerce")
dvp["Semanas"] = pd.to_numeric(dvp["Semanas"], errors="coerce")
dvp["Millones"] = dvp["Presupuesto"] / 1_000_000

# Proyectos PMO con sus fechas
pmo = hoja("Detalle iniciativa pmo")
pmo = pmo[pd.to_numeric(pmo["ID"], errors="coerce").notna()]  # Quitar la fila del total
pmo = pmo.replace("#REF!", pd.NA)
pmo["Estado"] = pmo["Estado"].str.strip().str.capitalize()  # "En Proceso" y "En proceso" son lo mismo
pmo["Presupuesto"] = pd.to_numeric(pmo["PPTO PARA ROADMAP PPT"], errors="coerce")
pmo["Siglas"] = pmo["Siglas"].str.strip()
fechas = hoja("Iniciativas").iloc[:, :7]
fechas.columns = ["Siglas", "Nombre", "Inicio LB", "Fin LB", "Inicio Real", "Fecha Acta Inicio", "Fin Proyectado"]
fechas["Siglas"] = fechas["Siglas"].str.strip()
fechas["Fin LB"] = pd.to_datetime(fechas["Fin LB"], errors="coerce")
fechas["Fin Proyectado"] = pd.to_datetime(fechas["Fin Proyectado"], errors="coerce")
pmo = pmo.merge(fechas[["Siglas", "Fin LB", "Fin Proyectado"]], on="Siglas", how="left")
pmo["Retraso (días)"] = (pmo["Fin Proyectado"] - pmo["Fin LB"]).dt.days

# Maestra de iniciativas
maestra = hoja("MAESTRA_INICIATIVAS")
for col in ["Tipo", "Dominio", "CadenaValor", "Pilar"]:
    maestra[col] = maestra[col].str.strip()

# Iniciativas de datos y de IA del portafolio (se identifican por palabras clave en el nombre)
CLAVES_DATOS = "dato|información|etl|analytics|analítica"
CLAVES_IA = "chat|rpa|automatiz|minería|inteligencia artificial|machine learning|bot"


def iniciativas_por_tema(claves):
    # Junta las iniciativas DVP y los proyectos PMO cuyo nombre contiene alguna palabra clave
    de_dvp = dvp[dvp["Iniciativa"].str.contains(claves, case=False, na=False)]
    de_pmo = pmo[pmo["Iniciativa/Proyecto"].str.contains(claves, case=False, na=False)]
    return pd.concat([
        pd.DataFrame({"Origen": "DVP", "Iniciativa": de_dvp["Iniciativa"], "Categoría / Gerencia": de_dvp["Categoria"],
                      "Presupuesto": de_dvp["Presupuesto"], "Semanas": de_dvp["Semanas"], "Estado": "Sin dato en el Excel"}),
        pd.DataFrame({"Origen": "PMO", "Iniciativa": de_pmo["Iniciativa/Proyecto"], "Categoría / Gerencia": de_pmo["Gerencia"],
                      "Presupuesto": de_pmo["Presupuesto"], "Semanas": pd.NA, "Estado": de_pmo["Estado"]}),
    ], ignore_index=True)


iniciativas_datos = iniciativas_por_tema(CLAVES_DATOS)
iniciativas_ia = iniciativas_por_tema(CLAVES_IA)

# ISO 38500: métricas calculadas solo con datos reales del Excel
def agregar_metrica(principio, tarea, resultado, metrica, fuente, base, actual, meta, origen_meta, menor_es_mejor=False):
    if actual is None or pd.isna(actual):
        return
    metricas_iso.append({"Principio": principio, "Sección": PRINCIPIOS_ISO[principio], "Tarea del modelo": tarea,
                         "Resultado": resultado, "Métrica": metrica, "Fuente": fuente, "Base en la norma": base,
                         "Actual": round(float(actual), 1), "Meta": meta, "Origen de la meta": origen_meta,
                         "Cumplimiento %": cumplimiento(actual, meta, menor_es_mejor)})


def agregar_bsc(principio, tarea, resultado, indicador, base, menor_es_mejor=False):
    # Usa un indicador de la hoja BSC con su meta real
    fila = bsc[bsc["Indicador"].str.strip() == indicador]
    if len(fila):
        agregar_metrica(principio, tarea, resultado, indicador, "Hoja BSC", base,
                        fila["Actual"].iloc[0], fila["Meta"].iloc[0], "Meta del BSC", menor_es_mejor)


def porcentaje_con_dato(df, columna):
    # Porcentaje de filas que tienen ese campo diligenciado
    if len(df) == 0 or columna not in df.columns:
        return None
    valores = df[columna].astype("string").str.strip()
    return float((valores.notna() & (valores != "")).mean() * 100)


def porcentaje_si(df, columna):
    # Porcentaje de filas con "Sí" en la columna
    if len(df) == 0:
        return None
    return float((df[columna].astype(str).str.strip() == "Sí").mean() * 100)


DE, AR, CE = RESULTADOS_ISO
TODOS = "100% (todos los registros)"
metricas_iso = []
agregar_metrica("Propósito", "Dirigir", DE, "Proyectos PMO asociados a una MEGA", "Hoja Detalle iniciativa pmo",
                "4.1.2 Alineación con el propósito de la organización", porcentaje_con_dato(pmo, "MEGA"), 100, TODOS)
agregar_bsc("Generación de valor", "Monitorear", DE, "Costo Total Propiedad TI", "4.1.2 Inversión apropiada en TI",
            menor_es_mejor=True)
agregar_bsc("Generación de valor", "Evaluar", DE, "Automatización", "4.1.2 Obtención de valor de los recursos de TI")
agregar_metrica("Estrategia", "Dirigir", DE, "Proyectos PMO asociados a un objetivo estratégico",
                "Hoja Detalle iniciativa pmo", "4.1.2 Alineación de las capacidades digitales",
                porcentaje_con_dato(pmo, "Objetivo Estrategico"), 100, TODOS)
agregar_metrica("Estrategia", "Evaluar", DE, "Iniciativas clasificadas por dominio estratégico", "Hoja MAESTRA_INICIATIVAS",
                "4.1.2 Alineación de las capacidades digitales",
                (maestra["Dominio"] != "Por Clasificar").mean() * 100 if len(maestra) else None, 100, TODOS)
con_fechas = pmo["Retraso (días)"].dropna()
agregar_metrica("Supervisión", "Monitorear", AR, "Proyectos PMO dentro de su línea base",
                "Hojas Detalle iniciativa pmo e Iniciativas", "3.8 Monitorear el avance frente a los planes",
                (con_fechas <= 0).mean() * 100 if len(con_fechas) else None, 100, TODOS)
agregar_bsc("Supervisión", "Monitorear", AR, "Gestión Demanda", "3.8 Monitorear el avance frente a los planes")
agregar_metrica("Rendición de cuentas", "Dirigir", AR, "Proyectos PMO con sponsor asignado", "Hoja Detalle iniciativa pmo",
                "3.3 Gobierno: dirección, supervisión y rendición de cuentas", porcentaje_con_dato(pmo, "Sponsor"), 100, TODOS)
agregar_metrica("Rendición de cuentas", "Dirigir", AR, "Proyectos PMO con gerente asignado", "Hoja Detalle iniciativa pmo",
                "3.3 Gobierno: dirección, supervisión y rendición de cuentas", porcentaje_con_dato(pmo, "Gerente"), 100, TODOS)
agregar_bsc("Involucramiento de partes interesadas", "Involucrar", CE, "Satisfacción Cliente",
            "4.1.4 Expectativas de las partes interesadas")
agregar_bsc("Liderazgo", "Dirigir", CE, "Competencias Digitales", "4.1.4 Comportamiento humano en el uso de TI")
agregar_bsc("Liderazgo", "Dirigir", DE, "OKR", "3.1 Dirigir: establecer objetivos")
agregar_metrica("Datos y decisiones", "Dirigir", CE, "Activos de datos con responsable asignado", "Hoja Inventario Datos",
                "4.1.4 Propiedad de los activos y derechos sobre los datos",
                porcentaje_si(gobierno_datos, "Responsable asignado"), 100, TODOS)
agregar_metrica("Gobierno del riesgo", "Evaluar", AR, "Casos de IA con evaluación ética", "Hoja Inventario IA",
                "4.1.3 Decisiones automatizadas razonables y justificadas (ISO/IEC 38507)",
                porcentaje_si(gobierno_ia, "Evaluación ética"), 100, TODOS)
agregar_bsc("Responsabilidad social", "Monitorear", CE, "Cumplimiento Normativo", "4.1.4 Cumplimiento de regulaciones")
agregar_bsc("Viabilidad y desempeño en el tiempo", "Monitorear", AR, "Disponibilidad Canales",
            "4.1.3 Seguridad y resiliencia de las capacidades digitales")
agregar_bsc("Viabilidad y desempeño en el tiempo", "Monitorear", DE, "Calidad Producción", "4.1.2 Desempeño efectivo de TI")
agregar_bsc("Viabilidad y desempeño en el tiempo", "Evaluar", DE, "Migración Integraciones", "4.1.2 Agilidad y adaptación")
agregar_bsc("Viabilidad y desempeño en el tiempo", "Monitorear", DE, "CSI", "4.1.2 Agilidad y adaptación (mejora continua)")
iso = pd.DataFrame(metricas_iso)
iso["Estado"] = iso["Cumplimiento %"].apply(estado)
principios_sin_datos = [p for p in PRINCIPIOS_ISO if p not in set(iso["Principio"])]


def hoja_si_existe(nombre):
    try:
        return hoja(nombre)
    except Exception:
        return None


# Si el Excel tiene las hojas ISO 38500, Gobierno de Datos y Gobierno IA, el dashboard usa lo que dicen esas hojas.
# Si todavía no están, usa lo calculado arriba con las demás hojas.
FUENTE_ISO = FUENTE_DATOS = FUENTE_IA = "calculado con las hojas del Excel"

hoja_iso = hoja_si_existe("ISO 38500")
if hoja_iso is not None and {"Principio", "Actual", "Meta", "Menor es mejor"} <= set(hoja_iso.columns):
    hoja_iso["Actual"] = numero(hoja_iso["Actual"])
    hoja_iso["Meta"] = numero(hoja_iso["Meta"])
    iso = hoja_iso.dropna(subset=["Actual", "Meta"]).copy()
    iso["Cumplimiento %"] = [cumplimiento(a, m, str(menor).strip() == "Sí")
                             for a, m, menor in zip(iso["Actual"], iso["Meta"], iso["Menor es mejor"])]
    iso["Estado"] = iso["Cumplimiento %"].apply(estado)
    principios_sin_datos = [p for p in PRINCIPIOS_ISO if p not in set(iso["Principio"])]
    FUENTE_ISO = "hoja ISO 38500 del Excel"

hoja_datos = hoja_si_existe("Gobierno de Datos")
if hoja_datos is not None and "Tipo de registro" in hoja_datos.columns:
    registros = hoja_datos[hoja_datos["Tipo de registro"] == "Iniciativa"]
    iniciativas_datos = pd.DataFrame({"Origen": registros["Hoja de origen"], "Iniciativa": registros["Nombre"],
                                      "Categoría / Gerencia": registros["Categoría o componente"],
                                      "Presupuesto": numero(registros["Presupuesto"]), "Estado": registros["Estado"]})
    registros = hoja_datos[hoja_datos["Tipo de registro"] == "Riesgo"]
    riesgos_info = pd.DataFrame({"COMPONENTE": registros["Categoría o componente"], "RIESGOS": registros["Nombre"],
                                 "IMPACTO": registros["Impacto"].astype(str).str.strip().str.capitalize()
                                 .replace({"Moderado": "Medio"})})
    FUENTE_DATOS = "hoja Gobierno de Datos del Excel"
else:
    riesgos_info = None  # se calcula en la sección con la hoja Riesgos

# Evaluación de los 16 puntos de la sección 4.1 de la ISO/IEC 38500:2024
evaluacion_iso = hoja_si_existe("ISO 38500 Evaluacion")
if evaluacion_iso is not None:
    evaluacion_iso = evaluacion_iso.rename(columns={"Traducción": "Punto", "Evidencia en el banco": "Evidencia"})

hoja_ia = hoja_si_existe("Gobierno IA")
if hoja_ia is not None and "Hoja de origen" in hoja_ia.columns:
    iniciativas_ia = pd.DataFrame({"Origen": hoja_ia["Hoja de origen"], "Iniciativa": hoja_ia["Nombre"],
                                   "Categoría / Gerencia": hoja_ia["Categoría o gerencia"],
                                   "Presupuesto": numero(hoja_ia["Presupuesto"]), "Semanas": numero(hoja_ia["Semanas"]),
                                   "Estado": hoja_ia["Estado"]})
    FUENTE_IA = "hoja Gobierno IA del Excel"

# Riesgos (el frente y el componente vienen en celdas combinadas)
riesgos = hoja("Riesgos")
riesgos[["FRENTE", "COMPONENTE"]] = riesgos[["FRENTE", "COMPONENTE"]].ffill()
riesgos["IMPACTO"] = riesgos["IMPACTO"].str.strip().str.capitalize().replace({"Moderado": "Medio"})

# Arquitectura tecnológica
arquitectura = hoja("Arquitectura tecnologica")
arquitectura["Valor"] = pd.to_numeric(arquitectura["Valor"], errors="coerce")


# Barra lateral
st.sidebar.title("Dashboard TI")
st.sidebar.write(ENTIDAD)

# Menú de secciones (lista fija en la barra lateral)
seccion = st.sidebar.radio("Secciones", [
    "Resumen",
    "ISO 38500",
    "Gobierno de Datos",
    "Gobierno de IA",
    "Operación TI",
    "BSC",
    "Portafolio",
    "Innovación",
    "Riesgos",
    "Arquitectura",
    "Contexto",
])
st.sidebar.divider()
if st.sidebar.button("Recargar datos"):
    st.cache_data.clear()
    st.rerun()
st.sidebar.caption(f"Fuente de datos: {fuente}")

# Título del dashboard
st.title("Dashboard Estratégico de Gobierno de TI")
st.write("Métricas de Gobierno de Datos, IA y TI · ISO/IEC 38500:2024")




# ---------------------------------------------------------------- Resumen
if seccion == "Resumen":
    col_izq, col_centro, col_der = st.columns(3)

    # ---------- Columna izquierda: filtros y línea de tiempo
    with col_izq.container(border=True):
        # Filtro interactivo para la evaluación ISO 38500
        st.markdown("**Filtros**")
        tema = st.selectbox("Tema", ["Todos", "Datos", "IA", "TI"], key="r_tema")
        resultado = st.selectbox("Resultado ISO 38500", ["Todos"] + RESULTADOS_ISO, key="r_resultado")
        evaluacion = evaluacion_iso if evaluacion_iso is not None else pd.DataFrame(
            columns=["Tema", "Resultado", "Estado"])
        if tema != "Todos":
            evaluacion = evaluacion[evaluacion["Tema"] == tema]
        if resultado != "Todos":
            evaluacion = evaluacion[evaluacion["Resultado"] == resultado]
        st.caption(f"{len(evaluacion)} puntos de la norma encontrados")

    with col_izq.container(border=True):
        # Gráfico de líneas: proyectos PMO que terminan en cada trimestre (línea base vs. proyectado)
        st.markdown("**Proyectos PMO por trimestre de finalización**")
        fechas_fin = pd.DataFrame({
            "Fin según línea base": pmo["Fin LB"].dt.to_period("Q").astype(str).value_counts(),
            "Fin proyectado": pmo["Fin Proyectado"].dt.to_period("Q").astype(str).value_counts(),
        }).fillna(0).sort_index()
        fechas_fin = fechas_fin[fechas_fin.index != "NaT"]
        st.line_chart(fechas_fin)

    # ---------- Columna central: riesgos y cajas por tema
    with col_centro.container(border=True):
        # Gráfico de barras apiladas: riesgos por frente e impacto
        st.markdown("**Riesgos por frente e impacto**")
        riesgos_frente = riesgos.groupby(["FRENTE", "IMPACTO"]).size().unstack(fill_value=0)
        riesgos_frente = riesgos_frente.reindex(columns=[c for c in COLORES_NIVEL if c in riesgos_frente.columns])
        fig, ax = plt.subplots(figsize=(4, 3))
        riesgos_frente.plot(kind="barh", stacked=True, ax=ax, color=[COLORES_NIVEL[c] for c in riesgos_frente.columns])
        etiquetas = [n.replace(" de ", chr(10) + "de ", 1) if len(n) > 25 else n for n in riesgos_frente.index]
        ax.set_yticklabels(etiquetas, fontsize=9)
        ax.set_ylabel("")
        ax.set_xlabel("Riesgos")
        ax.legend(title="", fontsize=8)
        st.pyplot(fig)
        plt.close(fig)

    with col_centro.container(border=True):
        # Cajas con el presupuesto de cada tema y su porcentaje del portafolio
        st.markdown("**Portafolio por tema**")
        portafolio_total = dvp["Presupuesto"].sum() + pmo["Presupuesto"].sum()
        nombres_datos = set(iniciativas_datos["Iniciativa"])
        nombres_ia = set(iniciativas_ia["Iniciativa"])
        presupuesto_ti = portafolio_total - pd.concat([iniciativas_datos, iniciativas_ia]).drop_duplicates(
            "Iniciativa")["Presupuesto"].sum()
        cajas = [("Datos", len(nombres_datos), iniciativas_datos["Presupuesto"].sum()),
                 ("IA", len(nombres_ia), iniciativas_ia["Presupuesto"].sum()),
                 ("TI (demás)", len(dvp) + len(pmo) - len(nombres_datos | nombres_ia), presupuesto_ti)]
        columnas = st.columns(3)
        for col, (nombre, cantidad, valor) in zip(columnas, cajas):
            with col.container(border=True):
                st.markdown(f"**{nombre}**")
                st.markdown(f"##### {millones(valor)}")
                st.caption(f"{valor / portafolio_total:.1%} del portafolio · {cantidad} iniciativas")

    # ---------- Columna derecha: evaluación ISO y cumplimiento por resultado
    with col_der.container(border=True):
        # Gráfico de dona con el estado de la evidencia (sección 4.1 de la norma)
        st.markdown("**ISO 38500:2024 - Evaluación (sección 4.1)**")
        conteo = evaluacion["Estado"].value_counts().reindex(COLORES_EVIDENCIA.keys()).dropna().astype(int)
        if len(conteo):
            fig = grafico_dona(conteo, [COLORES_EVIDENCIA[e] for e in conteo.index])
            st.pyplot(fig)
            plt.close(fig)
            st.write(tabla_porcentaje(evaluacion["Estado"]))
        else:
            st.write("No hay puntos con esos filtros.")

    with col_der.container(border=True):
        # Gráfico de barras con tabla: cumplimiento de las métricas ISO por resultado
        st.markdown("**ISO 38500:2024 - Cumplimiento por resultado**")
        metricas = iso if resultado == "Todos" else iso[iso["Resultado"] == resultado]
        por_resultado = metricas.groupby("Resultado").agg(Métricas=("Métrica", "count"),
                                                          Cumplimiento=("Cumplimiento %", "mean")).round(1)
        fig, ax = plt.subplots(figsize=(3.6, 1.6))
        ax.barh(por_resultado.index, por_resultado["Cumplimiento"],
                color=[COLORES_ESTADO[estado(v)] for v in por_resultado["Cumplimiento"]])
        ax.set_xlim(0, 100)
        ax.tick_params(labelsize=8)
        st.pyplot(fig)
        plt.close(fig)
        st.write(por_resultado)
        st.caption(f"Promedio: {metricas['Cumplimiento %'].mean():.1f}% · "
                   f"{len(PRINCIPIOS_ISO) - len(principios_sin_datos)} de {len(PRINCIPIOS_ISO)} principios con datos.")


# ---------------------------------------------------------------- ISO 38500
elif seccion == "ISO 38500":
    st.header("ISO/IEC 38500:2024 - Gobierno de TI para la organización")

    # Filtro interactivo para seleccionar el principio, la tarea del modelo y el resultado
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        principio = col1.selectbox("Seleccione un principio", ["Todos"] + list(iso["Principio"].unique()))
        tarea = col2.selectbox("Seleccione una tarea del modelo", ["Todas"] + TAREAS_MODELO)
        resultado = col3.selectbox("Seleccione un resultado", ["Todos"] + RESULTADOS_ISO)
    datos = iso.copy()
    if principio != "Todos":
        datos = datos[datos["Principio"] == principio]
    if tarea != "Todas":
        datos = datos[datos["Tarea del modelo"] == tarea]
    if resultado != "Todos":
        datos = datos[datos["Resultado"] == resultado]

    if len(datos) == 0:
        st.warning("No hay métricas con esos filtros.")
    else:
        # Cajas con el cumplimiento de cada resultado del buen gobierno de TI (sección 4.1)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cumplimiento promedio", f"{datos['Cumplimiento %'].mean():.1f}%", border=True)
        for col, r in zip([col2, col3, col4], RESULTADOS_ISO):
            del_resultado = datos[datos["Resultado"] == r]
            valor = f"{del_resultado['Cumplimiento %'].mean():.1f}%" if len(del_resultado) else "-"
            col.metric(r, valor, f"{len(del_resultado)} métricas", delta_color="off", delta_arrow="off", border=True)

        col1, col2 = st.columns([3, 2])
        with col1.container(border=True):
            # Gráfico de barras para mostrar el cumplimiento de los 11 principios
            st.markdown("**Cumplimiento por principio (%)**")
            por_principio = datos.groupby("Principio")["Cumplimiento %"].mean().sort_values()
            fig, ax = plt.subplots(figsize=(7, max(2.5, len(por_principio) * 0.45)))
            ax.barh(por_principio.index, por_principio.values,
                    color=[COLORES_ESTADO[estado(v)] for v in por_principio.values])
            ax.set_xlim(0, 105)
            ax.set_xlabel("Cumplimiento (%)")
            st.pyplot(fig)
            plt.close(fig)
        with col2.container(border=True):
            # Gráfico de dona con el estado de las métricas
            st.markdown("**Estado de las métricas**")
            conteo = datos["Estado"].value_counts().reindex(COLORES_ESTADO.keys()).dropna().astype(int)
            fig = grafico_dona(conteo, [COLORES_ESTADO[e] for e in conteo.index])
            st.pyplot(fig)
            plt.close(fig)
            st.write(tabla_porcentaje(datos["Estado"]))

        # Cajas con el número de métricas por tarea del modelo (sección 6.2)
        st.markdown("**Métricas por tarea del modelo de gobierno**")
        columnas = st.columns(4)
        for col, t in zip(columnas, TAREAS_MODELO):
            n = int((datos["Tarea del modelo"] == t).sum())
            col.metric(t, n, f"{n / len(datos):.0%} de las métricas", delta_color="off", delta_arrow="off", border=True)

        # Mostrar los datos filtrados
        with st.container(border=True):
            st.markdown("**Métricas por principio**")
            st.dataframe(datos[["Principio", "Métrica", "Actual", "Meta", "Cumplimiento %", "Estado"]].round(1),
                         hide_index=True)

    # Evaluación según los puntos de la sección 4.1 de la norma
    if evaluacion_iso is not None:
        st.subheader("Evaluación de los resultados del buen gobierno de TI (sección 4.1)")
        resultado_eval = st.selectbox("Seleccione un resultado de la norma", ["Todos"] + RESULTADOS_ISO,
                                      key="resultado_eval")
        datos_eval = evaluacion_iso if resultado_eval == "Todos" else \
            evaluacion_iso[evaluacion_iso["Resultado"] == resultado_eval]
        mostrar_evaluacion(datos_eval, f"Puntos de la norma evaluados: {len(datos_eval)}")

    # Brechas y plan de acción (hoja "Plan de accion" del Excel)
    hoja_plan = hoja_si_existe("Plan de accion")
    if hoja_plan is not None and "Acción en el portafolio" in hoja_plan.columns:
        hoja_plan["Presupuesto"] = numero(hoja_plan["Presupuesto"]).apply(lambda v: millones(v) if pd.notna(v) else "")
        with st.container(border=True):
            st.markdown("**Brechas y plan de acción**")
            st.dataframe(hoja_plan, hide_index=True)
    elif principios_sin_datos:
        BRECHAS = {
            "Datos y decisiones": ("No hay indicadores de calidad ni de uso de los datos",
                                   ["gobernanza del dato", "Analytics"]),
            "Gobierno del riesgo": ("La matriz de riesgos no tiene tratamiento ni seguimiento",
                                    ["SIAR"]),
        }
        filas_plan = []
        for principio in principios_sin_datos:
            brecha, claves = BRECHAS.get(principio, ("Sin indicadores", []))
            for clave in claves:
                for _, f in dvp[dvp["Iniciativa"].str.contains(clave, case=False, na=False)].iterrows():
                    filas_plan.append([principio, brecha, f["Iniciativa"], "DVP", millones(f["Presupuesto"]), "Propuesta"])
                for _, f in pmo[pmo["Iniciativa/Proyecto"].str.contains(clave, case=False, na=False)].iterrows():
                    filas_plan.append([principio, brecha, f["Iniciativa/Proyecto"], "PMO", millones(f["Presupuesto"]),
                                       f["Estado"]])
        with st.container(border=True):
            st.markdown("**Brechas y plan de acción**")
            st.dataframe(pd.DataFrame(filas_plan, columns=["Principio", "Brecha", "Acción en el portafolio",
                                                           "Origen", "Presupuesto", "Estado"]), hide_index=True)


# ---------------------------------------------------------------- Gobierno de Datos
elif seccion == "Gobierno de Datos":
    st.header("Gobierno de Datos")

    # Riesgos de información (componentes Procesamiento de Información y Seguridad Informática)
    if riesgos_info is None:
        riesgos_info = riesgos[riesgos["COMPONENTE"].str.contains("Información|Seguridad", case=False, na=False)]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Iniciativas de datos", len(iniciativas_datos), border=True)
    col2.metric("Presupuesto en datos", millones(iniciativas_datos["Presupuesto"].sum()), border=True)
    col3.metric("Riesgos de información", len(riesgos_info), border=True)
    col4.metric("Riesgos de información altos", int((riesgos_info["IMPACTO"] == "Alto").sum()), border=True)

    col1, col2 = st.columns([3, 2])
    with col1.container(border=True):
        # Gráfico de barras: presupuesto de cada iniciativa de datos
        st.markdown("**Presupuesto por iniciativa de datos (millones)**")
        grafico = iniciativas_datos.set_index("Iniciativa")["Presupuesto"].sort_values() / 1_000_000
        fig, ax = plt.subplots(figsize=(7, max(2.5, len(grafico) * 0.5)))
        ax.barh(grafico.index, grafico.values, color="#4c72b0")
        ax.set_xlabel("Millones de pesos")
        st.pyplot(fig)
        plt.close(fig)
    with col2.container(border=True):
        # Gráfico de dona con el impacto de los riesgos de información
        st.markdown("**Riesgos de información por impacto**")
        conteo = riesgos_info["IMPACTO"].value_counts().reindex(COLORES_NIVEL.keys()).dropna().astype(int)
        if len(conteo):
            fig = grafico_dona(conteo, [COLORES_NIVEL[n] for n in conteo.index])
            st.pyplot(fig)
            plt.close(fig)
            st.write(tabla_porcentaje(riesgos_info["IMPACTO"]))

    # Mostrar los datos
    with st.container(border=True):
        st.write("Iniciativas de datos:", iniciativas_datos)
    with st.container(border=True):
        st.write("Riesgos de información:", riesgos_info)

    # Contexto estratégico relacionado con los datos
    with st.container(border=True):
        st.markdown("**Contexto estratégico**")
        objetivos = hoja("Objetivos estrategicos")
        st.write(objetivos[objetivos.astype(str).apply(
            lambda fila: fila.str.contains("Información|Analítica", case=False).any(), axis=1)])
        dofa = hoja("Dofa")
        st.write(dofa[dofa["Descripción"].astype(str).str.contains("Dato|Data", case=False)])

    # Puntos de la ISO/IEC 38500:2024 relacionados con los datos
    if evaluacion_iso is not None:
        mostrar_evaluacion(evaluacion_iso[evaluacion_iso["Tema"] == "Datos"],
                           "ISO/IEC 38500:2024 - puntos de la sección 4.1 sobre datos")

    # Inventario de activos de datos (si la hoja tiene datos)
    if len(gobierno_datos):
        with st.container(border=True):
            st.markdown("**Inventario de activos de datos**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Activos de datos", len(gobierno_datos), border=True)
            col2.metric("Con responsable", f"{(gobierno_datos['Responsable asignado'] == 'Sí').mean():.0%}", border=True)
            col3.metric("Catalogados", f"{(gobierno_datos['Catalogado'] == 'Sí').mean():.0%}", border=True)
            st.bar_chart(gobierno_datos.groupby(["Dominio", "Clasificación"]).size().unstack(fill_value=0))
            st.write(gobierno_datos)


# ---------------------------------------------------------------- Gobierno de IA
elif seccion == "Gobierno de IA":
    st.header("Gobierno de Inteligencia Artificial")

    automatizacion = bsc[bsc["Indicador"].str.strip() == "Automatización"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Iniciativas de IA y automatización", len(iniciativas_ia), border=True)
    col2.metric("Presupuesto en IA", millones(iniciativas_ia["Presupuesto"].sum()), border=True)
    col3.metric("% del presupuesto digital",
                f"{iniciativas_ia['Presupuesto'].sum() / dvp['Presupuesto'].sum():.1%}", border=True)
    if len(automatizacion):
        col4.metric("Automatización (BSC)", f"{automatizacion['Actual'].iloc[0]:.0f} de {automatizacion['Meta'].iloc[0]:.0f}",
                    border=True)

    col1, col2 = st.columns(2)
    with col1.container(border=True):
        # Gráfico de barras: presupuesto de cada iniciativa de IA
        st.markdown("**Presupuesto por iniciativa (millones)**")
        grafico = iniciativas_ia.set_index("Iniciativa")["Presupuesto"].sort_values() / 1_000_000
        grafico.index = [n if len(n) <= 45 else n[:42] + "..." for n in grafico.index]
        fig, ax = plt.subplots(figsize=(6, max(2.5, len(grafico) * 0.6)))
        ax.barh(grafico.index, grafico.values, color="#8172b3")
        ax.set_xlabel("Millones de pesos")
        st.pyplot(fig)
        plt.close(fig)
    with col2.container(border=True):
        # Gráfico de dispersión entre la duración y el presupuesto
        st.markdown("**Relación entre duración y presupuesto**")
        con_semanas = iniciativas_ia.dropna(subset=["Semanas"])
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(con_semanas["Semanas"].astype(float), con_semanas["Presupuesto"] / 1_000_000)
        for _, fila in con_semanas.iterrows():
            ax.annotate(fila["Iniciativa"][:20], (float(fila["Semanas"]), fila["Presupuesto"] / 1_000_000), fontsize=8)
        ax.set_xlabel("Duración estimada (semanas)")
        ax.set_ylabel("Presupuesto (millones)")
        st.pyplot(fig)
        plt.close(fig)

    # Mostrar los datos
    with st.container(border=True):
        st.write("Iniciativas de IA y automatización:", iniciativas_ia)

    # Puntos de la ISO/IEC 38500:2024 relacionados con decisiones automatizadas (IA)
    if evaluacion_iso is not None:
        mostrar_evaluacion(evaluacion_iso[evaluacion_iso["Tema"] == "IA"],
                           "ISO/IEC 38500:2024 - puntos de la sección 4.1 sobre decisiones automatizadas")

    # Inventario de casos de uso de IA (si la hoja tiene datos)
    if len(gobierno_ia):
        with st.container(border=True):
            st.markdown("**Inventario de casos de uso de IA**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Casos de uso", len(gobierno_ia), border=True)
            col2.metric("Con evaluación ética", f"{(gobierno_ia['Evaluación ética'] == 'Sí').mean():.0%}", border=True)
            col3.metric("Monitoreados", f"{(gobierno_ia['Monitoreado'] == 'Sí').mean():.0%}", border=True)
            st.write(gobierno_ia)


# ---------------------------------------------------------------- Operación TI
elif seccion == "Operación TI":
    st.header("Operación de TI")

    operacion_bsc = bsc[bsc["Perspectiva"].isin(["Internal Process", "Customers"])]
    valores = arquitectura.set_index("Métrica")["Valor"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cumplimiento indicadores de operación", f"{operacion_bsc['Cumplimiento %'].mean():.1f}%", border=True)
    col2.metric("Servidores", int(valores.get("Servidores", 0)), border=True)
    col3.metric("Servidores en producción", int(valores.get("Producción", 0)), border=True)
    col4.metric("Aplicaciones críticas", int(valores.get("Aplicaciones Críticas", 0)), border=True)

    col1, col2 = st.columns([3, 2])
    with col1.container(border=True):
        # Gráfico de barras: indicadores de operación, actual frente a meta
        st.markdown("**Indicadores de operación: actual vs. meta**")
        st.bar_chart(operacion_bsc.set_index("Indicador")[["Actual", "Meta"]], stack=False, horizontal=True)
    with col2.container(border=True):
        # Gráfico de dona: servidores por ambiente
        st.markdown("**Servidores por ambiente**")
        ambiente = valores.reindex(["Producción", "QA"]).dropna().astype(int)
        fig = grafico_dona(ambiente, ["#2ca02c", "#ff7f0e"])
        st.pyplot(fig)
        plt.close(fig)
        st.write(ambiente.rename("Cantidad").to_frame())

    # Mostrar los indicadores del dominio TI con su fórmula y meta
    with st.container(border=True):
        st.write("Indicadores del dominio TI (fórmula y meta):",
                 hoja("Indicadores Dominio TI").dropna(subset=["INDICADOR"]).astype(str))

    # Solicitudes de la mesa de servicio (si la hoja tiene datos)
    if len(operacion):
        with st.container(border=True):
            st.markdown("**Solicitudes de la mesa de servicio por mes**")
            st.line_chart(operacion.groupby(["Mes", "Tipo"])["Cantidad"].sum().unstack())
            st.write(operacion.head(12))


# ---------------------------------------------------------------- Balanced Scorecard
elif seccion == "BSC":
    st.header("Balanced Scorecard")

    # Filtro interactivo para seleccionar la perspectiva
    perspectiva = st.selectbox("Seleccione una perspectiva", ["Todas"] + list(bsc["Perspectiva"].unique()))
    datos = bsc if perspectiva == "Todas" else bsc[bsc["Perspectiva"] == perspectiva]

    col1, col2 = st.columns([1, 3])
    col1.metric("Cumplimiento promedio", f"{datos['Cumplimiento %'].mean():.1f}%", border=True)
    with col2.container(border=True):
        # Gráfico de barras para mostrar el cumplimiento de cada indicador
        st.markdown("**Cumplimiento por indicador (%)**")
        ordenados = datos.sort_values("Cumplimiento %")
        fig, ax = plt.subplots(figsize=(9, max(2.5, len(ordenados) * 0.4)))
        ax.barh(ordenados["Indicador"], ordenados["Cumplimiento %"],
                color=[COLORES_ESTADO[estado(v)] for v in ordenados["Cumplimiento %"]])
        ax.set_xlim(0, 105)
        st.pyplot(fig)
        plt.close(fig)

    # Mostrar los datos filtrados
    with st.container(border=True):
        st.write(f"Indicadores de la perspectiva {perspectiva}:",
                 datos[["Perspectiva", "Indicador", "Actual", "Meta", "Cumplimiento %"]].round(1))


# ---------------------------------------------------------------- Portafolio
elif seccion == "Portafolio":
    st.header("Portafolio Estratégico")

    # Filtro interactivo para seleccionar el tipo de iniciativa
    tipo = st.selectbox("Seleccione un tipo de iniciativa", ["Todos"] + list(maestra["Tipo"].dropna().unique()))
    datos = maestra if tipo == "Todos" else maestra[maestra["Tipo"] == tipo]

    retrasados = pmo[pmo["Retraso (días)"] > 0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Iniciativas", len(datos), border=True)
    col2.metric("Proyectos PMO", len(pmo), border=True)
    col3.metric("PMO con retraso", f"{len(retrasados)} de {len(pmo)}", border=True)
    col4.metric("Retraso promedio", f"{retrasados['Retraso (días)'].mean():.0f} días", border=True)

    col1, col2 = st.columns(2)
    with col1.container(border=True):
        # Gráfico de barras: iniciativas por dominio
        st.markdown("**Iniciativas por dominio**")
        st.bar_chart(datos["Dominio"].value_counts(), horizontal=True)
    with col2.container(border=True):
        # Gráfico de dona con el estado de los proyectos PMO
        st.markdown("**Estado de los proyectos PMO**")
        conteo = pmo["Estado"].value_counts()
        fig = grafico_dona(conteo, ["#4c72b0", "#c7c7c7"])
        st.pyplot(fig)
        plt.close(fig)
        st.write(tabla_porcentaje(pmo["Estado"]))

    with st.container(border=True):
        # Gráfico de barras: retraso de cada proyecto frente a su línea base
        st.markdown("**Retraso: fin proyectado vs. línea base (días)**")
        con_fechas = pmo.dropna(subset=["Retraso (días)"]).sort_values("Retraso (días)")
        fig, ax = plt.subplots(figsize=(10, max(3, len(con_fechas) * 0.3)))
        ax.barh(con_fechas["Iniciativa/Proyecto"], con_fechas["Retraso (días)"],
                color=["#d62728" if v > 0 else "#2ca02c" for v in con_fechas["Retraso (días)"]])
        st.pyplot(fig)
        plt.close(fig)

    # Mostrar los datos filtrados
    with st.container(border=True):
        st.write("Detalle del portafolio:", datos)


# ---------------------------------------------------------------- Innovación
elif seccion == "Innovación":
    st.header("Innovación y Transformación Digital")

    # Filtro interactivo para seleccionar la categoría
    categoria = st.selectbox("Seleccione una categoría", ["Todas"] + list(dvp["Categoria"].dropna().unique()))
    datos = dvp if categoria == "Todas" else dvp[dvp["Categoria"] == categoria]

    col1, col2, col3 = st.columns(3)
    col1.metric("Presupuesto digital", millones(datos["Presupuesto"].sum()), border=True)
    col2.metric("Iniciativas", len(datos), border=True)
    col3.metric("Duración promedio", f"{datos['Semanas'].mean():.0f} semanas", border=True)

    col1, col2 = st.columns(2)
    with col1.container(border=True):
        # Gráfico de barras: inversión por categoría
        st.markdown("**Inversión por categoría (millones)**")
        st.bar_chart(datos.groupby("Categoria")["Millones"].sum().sort_values())
    with col2.container(border=True):
        # Gráfico de dispersión entre la duración y el presupuesto
        st.markdown("**Relación entre duración y presupuesto**")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(datos["Semanas"], datos["Millones"])
        ax.set_xlabel("Duración estimada (semanas)")
        ax.set_ylabel("Presupuesto (millones)")
        st.pyplot(fig)
        plt.close(fig)

    with st.container(border=True):
        # Gráfico de barras: inversión de cada iniciativa
        st.markdown("**Inversión por iniciativa (millones)**")
        fig, ax = plt.subplots(figsize=(10, max(3, len(datos) * 0.3)))
        sns.barplot(data=datos.sort_values("Presupuesto", ascending=False), x="Millones", y="Iniciativa",
                    hue="Categoria", dodge=False, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("")
        st.pyplot(fig)
        plt.close(fig)

    # Mostrar los datos filtrados
    with st.container(border=True):
        st.write("Rupturas estratégicas:", datos[["Iniciativa", "RUPTURA"]])


# ---------------------------------------------------------------- Riesgos
elif seccion == "Riesgos":
    st.header("Riesgos Estratégicos")

    # Filtro interactivo para seleccionar el frente y el impacto
    with st.container(border=True):
        col1, col2 = st.columns(2)
        frente = col1.selectbox("Seleccione un frente", ["Todos"] + list(riesgos["FRENTE"].dropna().unique()))
        impacto = col2.selectbox("Seleccione un impacto", ["Todos", "Alto", "Medio", "Bajo"])
    datos = riesgos.copy()
    if frente != "Todos":
        datos = datos[datos["FRENTE"] == frente]
    if impacto != "Todos":
        datos = datos[datos["IMPACTO"] == impacto]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total riesgos", len(datos), border=True)
    col2.metric("Impacto alto", int((datos["IMPACTO"] == "Alto").sum()), border=True)
    col3.metric("Impacto medio", int((datos["IMPACTO"] == "Medio").sum()), border=True)
    col4.metric("Impacto bajo", int((datos["IMPACTO"] == "Bajo").sum()), border=True)

    col1, col2 = st.columns([3, 2])
    with col1.container(border=True):
        # Gráfico de barras apiladas: riesgos por frente e impacto
        st.markdown("**Riesgos por frente tecnológico**")
        por_frente = datos.groupby(["FRENTE", "IMPACTO"]).size().unstack(fill_value=0)
        por_frente = por_frente.reindex(columns=[c for c in COLORES_NIVEL if c in por_frente.columns])
        if len(por_frente):
            st.bar_chart(por_frente, horizontal=True, color=[COLORES_NIVEL[c] for c in por_frente.columns])
    with col2.container(border=True):
        # Gráfico de dona con la distribución por impacto
        st.markdown("**Distribución por impacto**")
        conteo = datos["IMPACTO"].value_counts().reindex(COLORES_NIVEL.keys()).dropna().astype(int)
        if len(conteo):
            fig = grafico_dona(conteo, [COLORES_NIVEL[n] for n in conteo.index])
            st.pyplot(fig)
            plt.close(fig)
            st.write(tabla_porcentaje(datos["IMPACTO"]))

    # Mostrar los datos filtrados
    with st.container(border=True):
        st.write("Matriz de riesgos:", datos)


# ---------------------------------------------------------------- Arquitectura
elif seccion == "Arquitectura":
    st.header("Arquitectura Empresarial")
    valores = arquitectura.set_index("Métrica")["Valor"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Aplicaciones", int(valores.get("Aplicaciones", 0)), border=True)
    col2.metric("Aplicaciones críticas", int(valores.get("Aplicaciones Críticas", 0)), border=True)
    col3.metric("Servidores", int(valores.get("Servidores", 0)), border=True)
    col4.metric("Instancias", int(valores.get("Instancias", 0)), border=True)

    col1, col2, col3 = st.columns(3)
    with col1.container(border=True):
        # Gráfico de dona: instancias por sistema operativo
        st.markdown("**Instancias por sistema operativo**")
        so = valores.reindex(["Linux", "Windows"]).dropna().astype(int)
        fig = grafico_dona(so)
        st.pyplot(fig)
        plt.close(fig)
    with col2.container(border=True):
        # Gráfico de dona: servidores por ambiente
        st.markdown("**Servidores por ambiente**")
        ambiente = valores.reindex(["Producción", "QA"]).dropna().astype(int)
        fig = grafico_dona(ambiente, ["#2ca02c", "#ff7f0e"])
        st.pyplot(fig)
        plt.close(fig)
    with col3.container(border=True):
        # Gráfico de barras: iniciativas por dominio estratégico
        st.markdown("**Iniciativas por dominio estratégico**")
        clasificadas = maestra[maestra["Dominio"] != "Por Clasificar"]
        st.bar_chart(clasificadas["Dominio"].value_counts(), horizontal=True)

    with st.container(border=True):
        # Gráfico de barras: capacidades tecnológicas
        st.markdown("**Capacidades tecnológicas**")
        st.bar_chart(arquitectura.set_index("Métrica")["Valor"], horizontal=True)


# ---------------------------------------------------------------- Contexto
elif seccion == "Contexto":
    st.header("Contexto estratégico")

    # Análisis DOFA
    dofa = hoja("Dofa")
    columnas = st.columns(4)
    for col, (tipo, titulo) in zip(columnas, [("Fortaleza", "Fortalezas"), ("Debilidad", "Debilidades"),
                                              ("Oportunidad", "Oportunidades"), ("Amenaza", "Amenazas")]):
        with col.container(border=True):
            st.markdown(f"**{titulo}**")
            for item in dofa.loc[dofa["Tipo"] == tipo, "Descripción"]:
                st.write(f"- {item}")

    col1, col2 = st.columns([1, 2])
    with col1.container(border=True):
        st.write("Fuerzas de Porter:", hoja("Porter"))
    with col2.container(border=True):
        st.write("Indicadores del dominio TI:", hoja("Indicadores Dominio TI").dropna(subset=["INDICADOR"]).astype(str))


