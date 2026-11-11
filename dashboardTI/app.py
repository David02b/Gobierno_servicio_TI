"""
Dashboard Estratégico de TI — versión Python (Streamlit).

Ejecutar:  doble clic en iniciar.bat   (o)   python -m streamlit run app.py
Para actualizar: edita Extraido_CIO_Completo.xlsx, guarda y presiona "Recargar datos".
"""
import datetime as dt

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import streamlit as st

import datos

ENTIDAD = "Banco Unión"   # ← nombre que aparece en la esquina y en el menú

st.set_page_config(page_title=f"Dashboard Estratégico TI · {ENTIDAD}", page_icon="📊", layout="wide")

# ============================================================ paleta y estilo
INDIGO, CIAN, VERDE, AMBAR, ROJO, GRIS = "#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#cbd5e1"
SERIE = [INDIGO, CIAN, "#8b5cf6", VERDE, AMBAR, "#ec4899", "#64748b"]
COLOR_IMPACTO = {"Alto": ROJO, "Medio": AMBAR, "Bajo": VERDE}

pio.templates["ti"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#334155"),
    title=dict(font=dict(size=16, color="#0f172a"), x=0, xanchor="left"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=SERIE, margin=dict(l=10, r=60, t=50, b=10),
    xaxis=dict(showgrid=False, linecolor="#e2e8f0", title=None),
    yaxis=dict(gridcolor="#eef2f7", zeroline=False, title=None),
    legend=dict(orientation="h", y=-0.08, yanchor="top", x=0.5, xanchor="center", title=None),
    hoverlabel=dict(bgcolor="white", font_size=13),
    bargap=0.3,
))
pio.templates.default = "plotly_white+ti"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, .stDataFrame { font-family: 'Inter', 'Segoe UI', sans-serif; }
#MainMenu, footer, [data-testid="stToolbarActions"], [data-testid="stMainMenu"], [data-testid="stStatusWidget"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent; }

/* botón para MOSTRAR la barra lateral (cuando está oculta) */
[data-testid="stExpandSidebarButton"], header [data-testid="stBaseButton-header"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; color: white !important;
    border-radius: 12px !important; width: 44px !important; height: 44px !important;
    box-shadow: 0 6px 16px -4px rgba(79,70,229,.6); opacity: 1 !important; visibility: visible !important; }
[data-testid="stExpandSidebarButton"] *, header [data-testid="stBaseButton-header"] * { color: white !important; fill: white !important; }
[data-testid="stExpandSidebarButton"]:hover, header [data-testid="stBaseButton-header"]:hover { filter: brightness(1.12); transform: scale(1.05); }

/* botón para OCULTAR la barra lateral: siempre visible */
[data-testid="stSidebarCollapseButton"] { visibility: visible !important; opacity: 1 !important; display: block !important; }
[data-testid="stSidebarCollapseButton"] button { background: rgba(255,255,255,.12) !important; border-radius: 10px !important; }
[data-testid="stSidebarCollapseButton"] button:hover { background: rgba(255,255,255,.25) !important; }
.block-container { padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1400px; }

/* barra lateral */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%); }
[data-testid="stSidebar"] * { color: #e0e7ff !important; }
[data-testid="stSidebar"] .stRadio label { padding: .45rem .6rem; border-radius: 10px; margin-bottom: 2px; transition: background .15s; }
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,.08); }
[data-testid="stSidebar"] .stRadio label:has(input:checked) { background: rgba(255,255,255,.16); font-weight: 600; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:not([data-testid="stMarkdownContainer"]) { display: none !important; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] { width: 100%; }
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] { background: rgba(255,255,255,.16); font-weight: 600; }
h4 { font-size: 1rem !important; font-weight: 700 !important; color: #0f172a; padding-top: .2rem !important; }
[data-testid="stSidebar"] .stButton button { background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.25); width: 100%; border-radius: 10px; }
[data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,.22); }
.brand { font-size: 1.35rem; font-weight: 800; letter-spacing: -.02em; margin: .2rem 0 .1rem; }
.brand-sub { font-size: .8rem; opacity: .7; margin-bottom: 1.2rem; }
.side-foot { font-size: .75rem; opacity: .65; margin-top: 1rem; line-height: 1.5; }

/* pantalla de carga */
.overlay { position: fixed; inset: 0; z-index: 999999; background: rgba(244,246,251,.72); backdrop-filter: blur(3px);
           display: grid; place-items: center; animation: aparecer .15s ease-out; }
.loader-box { background: white; border-radius: 20px; padding: 1.8rem 2.4rem; text-align: center;
              box-shadow: 0 20px 50px -15px rgba(30,27,75,.35); border: 1px solid #e8ecf4; }
.spinner { width: 54px; height: 54px; margin: 0 auto 1rem; border-radius: 50%;
           border: 5px solid #e0e7ff; border-top-color: #4f46e5; border-right-color: #06b6d4;
           animation: girar .7s linear infinite; }
.loader-txt { font-weight: 600; color: #1e293b; font-size: .95rem; }
@keyframes girar { to { transform: rotate(360deg); } }
@keyframes aparecer { from { opacity: 0; } to { opacity: 1; } }

/* encabezado de página */
.hero { background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 55%, #06b6d4 100%); border-radius: 20px;
        padding: 1.6rem 2rem; color: white; margin-bottom: 1.4rem; box-shadow: 0 10px 30px -12px rgba(79,70,229,.55); }
.hero { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.hero .entidad { order: 2; flex-shrink: 0; white-space: nowrap; background: rgba(255,255,255,.18); backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,.35); padding: .4rem .95rem; border-radius: 999px; font-weight: 700;
        font-size: .9rem; letter-spacing: .01em; }
.hero h1 { font-size: 1.85rem; font-weight: 800; margin: 0; letter-spacing: -.02em; color: white; }
.hero p { margin: .35rem 0 0; opacity: .88; font-size: .95rem; }

/* tarjetas KPI */
.kpi { background: white; border-radius: 16px; padding: 1.1rem 1.2rem; border: 1px solid #e8ecf4;
       box-shadow: 0 1px 2px rgba(15,23,42,.04), 0 6px 18px -10px rgba(15,23,42,.12); height: 100%;
       display: flex; gap: .9rem; align-items: center; }
.kpi .ico { width: 46px; height: 46px; border-radius: 12px; display: grid; place-items: center; font-size: 1.35rem; flex-shrink: 0; }
.kpi { padding: clamp(.8rem, 1.1vw, 1.1rem) clamp(.8rem, 1.2vw, 1.2rem) !important; gap: clamp(.55rem, .9vw, .9rem) !important; }
.kpi .ico { width: clamp(36px, 3vw, 46px) !important; height: clamp(36px, 3vw, 46px) !important; font-size: clamp(1rem, 1.4vw, 1.35rem) !important; }
.kpi .val { font-size: clamp(1.15rem, 1.7vw, 1.55rem) !important; white-space: nowrap; }
.kpi .lbl { font-size: clamp(.66rem, .8vw, .78rem) !important; }
.kpi .sub { font-size: clamp(.68rem, .8vw, .78rem) !important; }
.kpi .lbl { font-size: .78rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }
.kpi .val { font-size: 1.55rem; font-weight: 800; color: #0f172a; line-height: 1.15; letter-spacing: -.02em; }
.kpi .sub { font-size: .78rem; color: #94a3b8; margin-top: 2px; }
.kpi .sub.bad { color: #ef4444; font-weight: 600; } .kpi .sub.good { color: #10b981; font-weight: 600; }

/* contenedores de gráficos */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) { }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px !important; }
.st-key-card, [class*="st-key-card"] { background: white; border-radius: 16px; border: 1px solid #e8ecf4;
       padding: .9rem 1rem .4rem; box-shadow: 0 6px 18px -12px rgba(15,23,42,.15); }
h3 { font-weight: 700 !important; color: #0f172a; letter-spacing: -.01em; }
.chip { display: inline-block; padding: .2rem .65rem; border-radius: 999px; font-size: .78rem; font-weight: 600; margin: 0 .3rem .4rem 0; }
.alerta { background: white; border-left: 4px solid #f59e0b; border-radius: 12px; padding: .9rem 1.1rem; margin-bottom: .7rem;
          box-shadow: 0 6px 18px -12px rgba(15,23,42,.15); }
</style>
""", unsafe_allow_html=True)


# ============================================================ helpers visuales
def millones(v: float) -> str:
    return f"${v / 1e6:,.0f} M".replace(",", ".")


def hero(titulo: str, sub: str):
    st.markdown(f'<div class="hero"><div><h1>{titulo}</h1><p>{sub}</p></div><div class="entidad">🏦 {ENTIDAD}</div></div>',
                unsafe_allow_html=True)


def kpi(col, icono: str, etiqueta: str, valor, sub: str = "", color: str = INDIGO, tono: str = ""):
    col.markdown(f"""
    <div class="kpi">
      <div class="ico" style="background:{color}1a;color:{color}">{icono}</div>
      <div><div class="lbl">{etiqueta}</div><div class="val">{valor}</div>
      <div class="sub {tono}">{sub}</div></div>
    </div>""", unsafe_allow_html=True)


_n = 0
def tarjeta():
    """Contenedor blanco con borde redondeado para un gráfico o tabla."""
    global _n
    _n += 1
    return st.container(key=f"card{_n}")


def grafico(fig, alto: int | None = None, contenedor=None):
    if alto:
        fig.update_layout(height=alto)
    fig.update_xaxes(title=None).update_yaxes(title=None)
    fig.update_layout(legend_title_text=None, font_family="Inter, Segoe UI, sans-serif")
    fig.update_traces(cliponaxis=False, selector=dict(type="bar"))
    if any(t.type == "pie" for t in fig.data):  # leyenda debajo de las donas, para no chocar con el título
        fig.update_layout(legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center", yanchor="top"))
    if any(t.type == "treemap" for t in fig.data):
        fig.update_layout(uniformtext=dict(minsize=11, mode="hide"), margin=dict(t=50, l=5, r=5, b=5))
    (contenedor or tarjeta()).plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})


def espacio():
    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)


# ============================================================ datos
@st.cache_data
def cargar(_mtime: float):
    return {
        "kpis": datos.kpis(), "presupuesto": datos.presupuesto(), "bsc": datos.bsc(),
        "pmo": datos.iniciativas_pmo(), "dvp": datos.iniciativas_dvp(), "maestra": datos.maestra(),
        "riesgos": datos.riesgos(), "arq": datos.arquitectura(),
        "dominios": datos.tabla_simple("Dominios Estrategicos"), "dofa": datos.tabla_simple("Dofa"),
        "porter": datos.tabla_simple("Porter"), "ind_ti": datos.tabla_simple("Indicadores Dominio TI"),
        "alertas": datos.alertas_calidad(),
    }


# ============================================================ barra lateral
PAGINAS = {
    "🏠  Resumen": "Resumen", "🎯  Balanced Scorecard": "BSC", "🚀  Innovación y Transformación": "DVP",
    "🏗️  Arquitectura Empresarial": "Arq", "📁  Portafolio Estratégico": "Port", "🛡️  Riesgos Estratégicos": "Riesgos",
    "🧭  Contexto estratégico": "Ctx", "🔍  Calidad de datos": "Calidad",
}
with st.sidebar:
    st.markdown(f'<div class="brand">📊 Dashboard TI</div><div class="brand-sub">🏦 {ENTIDAD} · Gobierno y Servicios de TI</div>',
                unsafe_allow_html=True)
    pagina = PAGINAS[st.radio("Navegación", list(PAGINAS), label_visibility="collapsed")]
    st.markdown("<br>", unsafe_allow_html=True)
    recargar = st.button("🔄  Recargar datos")
    if recargar:
        st.cache_data.clear()

mostrar_carga = recargar or "cargado" not in st.session_state
cargando = st.empty()
if mostrar_carga:
    cargando.markdown(f"""
    <div class="overlay"><div class="loader-box">
      <div class="spinner"></div>
      <div class="loader-txt">{'Actualizando datos desde Google Drive…' if datos.URL_GOOGLE else 'Cargando datos…'}</div>
    </div></div>""", unsafe_allow_html=True)
estado_fuente = datos.sincronizar(forzar=recargar)
mtime = datos.ARCHIVO.stat().st_mtime
D = cargar(mtime)
cargando.empty()
st.session_state["cargado"] = True
if recargar:
    if estado_fuente in ("Google Drive", "Excel local"):
        st.toast("Datos actualizados", icon="✅")
    else:
        st.toast("No se pudo actualizar; se muestra la última copia", icon="⚠️")
K = D["kpis"]
with st.sidebar:
    if D["alertas"]:
        st.markdown(f"<div class='side-foot'>⚠️ {len(D['alertas'])} alertas de calidad en el Excel</div>", unsafe_allow_html=True)
    origen = "☁️ Google Drive" if estado_fuente == "Google Drive" else ("⚠️ " + estado_fuente if "Drive" in estado_fuente else "📄 " + datos.ARCHIVO.name)
    st.markdown(f"<div class='side-foot'>{origen}<br>🕒 Datos del {dt.datetime.fromtimestamp(mtime):%d/%m/%Y %H:%M}</div>",
                unsafe_allow_html=True)

# ============================================================ páginas
if pagina == "Resumen":
    hero("Dashboard Estratégico", "Visión general del portafolio, presupuesto, desempeño y riesgos de TI")
    p = K["presupuesto_por_anio"]
    c = st.columns(4)
    iconos = ["💰", "💵", "🪙"]
    for i, (col, (anio, v)) in enumerate(zip(c, p.items())):
        kpi(col, iconos[i % 3], f"Presupuesto {anio}", millones(v), "Pesos colombianos", [INDIGO, CIAN, "#8b5cf6"][i % 3])
    bsc_ok = K["bsc_global"] >= 90
    kpi(c[3], "🎯", "BSC Global", f"{K['bsc_global']:.1f}%", "Cumplimiento vs meta", VERDE if bsc_ok else AMBAR,
        "good" if bsc_ok else "bad")
    espacio()
    c = st.columns(4)
    kpi(c[0], "📌", "Iniciativas", K["total_iniciativas"], f"{K['iniciativas_ppt']} PPT · {K['iniciativas_pmo']} PMO", INDIGO)
    kpi(c[1], "⚡", "Presupuesto digital", millones(K["presupuesto_digital"]), "Iniciativas DVP", CIAN)
    kpi(c[2], "🛡️", "Riesgos", K["riesgos"], f"{K['riesgos_altos']} de impacto alto", ROJO, "bad")
    kpi(c[3], "⏱️", "PMO con retraso", f"{K['pmo_con_retraso']} / {K['iniciativas_pmo']}",
        f"{K['retraso_promedio']:.0f} días en promedio", AMBAR, "bad")
    espacio()
    izq, der = st.columns(2)
    fig = px.bar(D["presupuesto"], x="Año", y="Presupuesto", color="Tipo", title="Presupuesto por año y tipo",
                 color_discrete_sequence=[INDIGO, CIAN, "#8b5cf6"])
    fig.update_xaxes(type="category").update_yaxes(tickprefix="$", tickformat=".2s")
    grafico(fig, 380, izq.container(key="card_r1"))
    b = D["bsc"].groupby("Perspectiva", as_index=False)["Cumplimiento"].mean()
    b["Cumplimiento"] *= 100
    fig = px.bar(b.sort_values("Cumplimiento"), x="Cumplimiento", y="Perspectiva", orientation="h", text="Cumplimiento",
                 title="Cumplimiento BSC por perspectiva", range_x=[0, 110])
    fig.update_traces(marker_color=[VERDE if v >= 95 else AMBAR if v >= 85 else ROJO for v in b.sort_values("Cumplimiento")["Cumplimiento"]],
                      texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_xaxes(showticklabels=False)
    grafico(fig, 380, der.container(key="card_r2"))

elif pagina == "BSC":
    hero("Balanced Scorecard", "Cumplimiento de cada indicador frente a su meta (tope 100%)")
    b = D["bsc"].copy()
    b["Cumplimiento %"] = b["Cumplimiento"] * 100
    b["Estado"] = b["Cumplimiento %"].map(lambda x: "Cumple" if x >= 100 else ("Cerca" if x >= 85 else "Bajo"))
    c = st.columns(4)
    kpi(c[0], "🎯", "BSC Global", f"{b['Cumplimiento %'].mean():.1f}%", f"{len(b)} indicadores", INDIGO)
    kpi(c[1], "✅", "Cumplen", int((b["Estado"] == "Cumple").sum()), "≥ 100% de la meta", VERDE, "good")
    kpi(c[2], "🟡", "Cerca", int((b["Estado"] == "Cerca").sum()), "85% – 99%", AMBAR)
    kpi(c[3], "🔻", "Bajo meta", int((b["Estado"] == "Bajo").sum()), "< 85%", ROJO, "bad")
    espacio()
    persp = st.pills("Perspectiva", b["Perspectiva"].unique(), selection_mode="multi", default=list(b["Perspectiva"].unique()))
    b = b[b["Perspectiva"].isin(persp or [])]
    izq, der = st.columns([3, 2])
    s = b.sort_values("Cumplimiento %")
    fig = go.Figure()
    fig.add_bar(y=s["Indicador"], x=[100] * len(s), orientation="h", marker_color="#eef2f7", hoverinfo="skip", showlegend=False)
    fig.add_bar(y=s["Indicador"], x=s["Cumplimiento %"], orientation="h", text=s["Cumplimiento %"].map(lambda v: f"{v:.0f}%" if v >= 99.95 or v == int(v) else f"{v:.1f}%"),
                textposition="inside", insidetextanchor="end", showlegend=False,
                marker_color=[{"Cumple": VERDE, "Cerca": AMBAR, "Bajo": ROJO}[e] for e in s["Estado"]],
                customdata=s[["Actual", "Meta"]], hovertemplate="%{y}<br>Actual %{customdata[0]} · Meta %{customdata[1]}<extra></extra>")
    fig.update_layout(barmode="overlay", title="Cumplimiento por indicador", bargap=.35)
    fig.update_xaxes(range=[0, 101], showticklabels=False)
    grafico(fig, 470, izq.container(key="card_b1"))
    with der.container(key="card_b2"):
        st.markdown("#### Detalle")
        st.dataframe(b[["Perspectiva", "Indicador", "Actual", "Meta", "Cumplimiento %"]], hide_index=True, width="stretch", height=400,
                     column_config={"Cumplimiento %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%")})
    st.caption("ℹ️ En *Costo Total Propiedad TI* menor es mejor (la meta es un tope), por eso se calcula Meta ÷ Actual.")

elif pagina == "DVP":
    hero("Innovación y Transformación", "Iniciativas de transformación digital (DVP), inversión y rupturas estratégicas")
    d = D["dvp"]
    cats = st.pills("Categoría", d["Categoria"].unique(), selection_mode="multi", default=list(d["Categoria"].unique()))
    d = d[d["Categoria"].isin(cats or [])]
    c = st.columns(4)
    kpi(c[0], "⚡", "Presupuesto digital", millones(d["Presupuesto"].sum()), "Total proyectado", INDIGO)
    kpi(c[1], "🚀", "Iniciativas", len(d), f"{d['Categoria'].nunique()} categorías", CIAN)
    kpi(c[2], "🗓️", "Duración promedio", f"{d['Semanas'].mean():.0f} sem", f"{d['Semanas'].sum():.0f} semanas en total", "#8b5cf6")
    top = d.nlargest(1, "Presupuesto")
    kpi(c[3], "🏆", "Mayor inversión", millones(top["Presupuesto"].iloc[0]) if len(top) else "-",
        (top["Iniciativa"].iloc[0][:32] + "…") if len(top) else "", AMBAR)
    espacio()
    izq, der = st.columns([3, 2])
    s = d.sort_values("Presupuesto").copy()
    s["Nombre"] = s["Iniciativa"].map(lambda x: x if len(x) <= 42 else x[:40].rstrip() + "…")
    fig = px.bar(s, x="Presupuesto", y="Nombre", color="Categoria", orientation="h", title="Inversión por iniciativa",
                 hover_data={"Iniciativa": True, "Nombre": False}, text="Presupuesto")
    fig.update_traces(texttemplate="$%{x:.3s}", textposition="outside", textfont_size=10)
    fig.update_xaxes(showticklabels=False, showgrid=False)
    fig.update_yaxes(tickfont=dict(size=11), categoryorder="total ascending")
    fig.update_layout(legend=dict(orientation="h", y=1.0, x=0, xanchor="left", yanchor="bottom"), margin=dict(t=80))
    grafico(fig, 720, izq.container(key="card_d1"))
    cat = d.groupby("Categoria", as_index=False)["Presupuesto"].sum()
    fig = px.pie(cat, names="Categoria", values="Presupuesto", hole=.62, title="Inversión por categoría")
    fig.update_traces(textinfo="percent", marker=dict(line=dict(color="white", width=3)))
    fig.update_layout(legend=dict(orientation="v", y=.5, x=1.02, xanchor="left", yanchor="middle"))
    grafico(fig, 340, der.container(key="card_d2"))
    with der.container(key="card_d3"):
        st.markdown("#### Top 8 OPM por presupuesto")
        st.dataframe(d.nlargest(8, "Presupuesto")[["Iniciativa", "Presupuesto", "Semanas"]], hide_index=True, width="stretch",
                     column_config={"Presupuesto": st.column_config.NumberColumn(format="$%,.0f")})
    with st.container(key="card_d4"):
        st.markdown("#### Rupturas estratégicas")
        st.dataframe(d[["Iniciativa", "RUPTURA"]], hide_index=True, width="stretch")

elif pagina == "Arq":
    hero("Arquitectura Empresarial", "Inventario tecnológico y dominios estratégicos")
    a = D["arq"].set_index("Métrica")["Valor"]
    c = st.columns(4)
    for col, (m, ico, colr) in zip(c, [("Aplicaciones", "🧩", INDIGO), ("Aplicaciones Críticas", "🔥", ROJO),
                                       ("Servidores", "🖥️", CIAN), ("Instancias", "☁️", "#8b5cf6")]):
        if m in a:
            kpi(col, ico, m, f"{a[m]:,.0f}".replace(",", "."), "", colr)
    espacio()
    c = st.columns(3)
    for col, (titulo, claves, colores) in zip(c, [
            ("Instancias por sistema operativo", ["Linux", "Windows"], [INDIGO, CIAN]),
            ("Servidores por ambiente", ["Producción", "QA"], [VERDE, AMBAR]),
            ("Aplicaciones críticas", ["Aplicaciones Críticas", "Otras"], [ROJO, GRIS])]):
        serie = a.copy()
        serie["Otras"] = a.get("Aplicaciones", 0) - a.get("Aplicaciones Críticas", 0)
        df = serie.reindex(claves).dropna().reset_index()
        df.columns = ["Métrica", "Valor"]
        fig = px.pie(df, names="Métrica", values="Valor", hole=.65, title=titulo, color="Métrica",
                     color_discrete_map=dict(zip(claves, colores)))
        fig.update_traces(textinfo="value+percent", marker=dict(line=dict(color="white", width=3)))
        fig.update_layout(legend=dict(orientation="h", y=-.1, x=.5, xanchor="center", yanchor="top"))
        grafico(fig, 340, col.container(key=f"card_a{titulo[:5]}"))
    m = D["maestra"]
    dom = m[m["Dominio"] != "Por Clasificar"].groupby("Dominio").size().rename("Iniciativas").reset_index().sort_values("Iniciativas")
    fig = px.bar(dom, x="Iniciativas", y="Dominio", orientation="h", text="Iniciativas",
                 title=f"Iniciativas por dominio estratégico ({len(D['dominios'])} dominios)", color_discrete_sequence=[INDIGO])
    fig.update_traces(textposition="outside").update_xaxes(showticklabels=False)
    grafico(fig, 320)

elif pagina == "Port":
    hero("Portafolio Estratégico", "Composición del portafolio, estado y cumplimiento de cronograma de los proyectos")
    m = D["maestra"]
    tipos = st.pills("Tipo", m["Tipo"].unique(), selection_mode="multi", default=list(m["Tipo"].unique()))
    m = m[m["Tipo"].isin(tipos or [])]
    p = D["pmo"]
    c = st.columns(4)
    kpi(c[0], "📁", "Iniciativas", len(m), " · ".join(f"{k} {v}" for k, v in m["Tipo"].value_counts().items()), INDIGO)
    ep = p["Estado"].value_counts()
    kpi(c[1], "▶️", "PMO en proceso", int(ep.get("En proceso", 0)), "", CIAN)
    kpi(c[2], "⏸️", "PMO no iniciadas", int(ep.get("No iniciado", 0)), "", GRIS.replace("cbd5e1", "64748b"))
    kpi(c[3], "⏱️", "Retraso promedio", f"{K['retraso_promedio']:.0f} días", f"{K['pmo_con_retraso']} proyectos retrasados", ROJO, "bad")
    espacio()
    izq, der = st.columns(2)
    dom = m.groupby("Dominio").size().rename("Iniciativas").reset_index().sort_values("Iniciativas")
    fig = px.bar(dom, x="Iniciativas", y="Dominio", orientation="h", text="Iniciativas", title="Iniciativas por dominio")
    fig.update_traces(textposition="outside",
                      marker_color=[GRIS if d == "Por Clasificar" else INDIGO for d in dom["Dominio"]])
    fig.update_xaxes(showticklabels=False)
    grafico(fig, 380, izq.container(key="card_p1"))
    fig = px.treemap(D["dvp"], path=["Categoria", "Iniciativa"], values="Presupuesto", title="Inversión DVP por categoría",
                     color_discrete_sequence=SERIE)
    fig.update_traces(marker=dict(cornerradius=6), textinfo="label+percent root")
    grafico(fig, 380, der.container(key="card_p2"))

    r = p.dropna(subset=["Retraso (días)"]).sort_values("Retraso (días)")
    fig = go.Figure(go.Bar(x=r["Retraso (días)"], y=r["Iniciativa/Proyecto"], orientation="h",
                           marker_color=[ROJO if v > 180 else AMBAR if v > 0 else VERDE for v in r["Retraso (días)"]],
                           text=r["Retraso (días)"].map(lambda v: f"+{v:.0f} d" if v > 0 else f"{v:.0f} d"), textposition="outside",
                           hovertemplate="%{y}<br>%{x} días<extra></extra>"))
    fig.update_layout(title="Retraso de proyectos PMO (fin proyectado vs. línea base)", margin=dict(r=60))
    fig.update_xaxes(showticklabels=False).update_yaxes(tickfont=dict(size=11))
    izq, der = st.columns([3, 2])
    grafico(fig, 680, izq.container(key="card_p3"))
    g = p.groupby("Gerencia", as_index=False)["Presupuesto"].sum().sort_values("Presupuesto")
    fig = px.bar(g, x="Presupuesto", y="Gerencia", orientation="h", title="Presupuesto PMO por gerencia",
                 color_discrete_sequence=[CIAN])
    fig.update_xaxes(tickprefix="$", tickformat=".2s")
    grafico(fig, 340, der.container(key="card_p4"))
    est = p["Estado"].value_counts().reset_index()
    fig = px.pie(est, names="Estado", values="count", hole=.65, title="Estado de proyectos PMO",
                 color_discrete_sequence=[INDIGO, GRIS])
    fig.update_traces(marker=dict(line=dict(color="white", width=3)))
    grafico(fig, 320, der.container(key="card_p5"))
    with st.container(key="card_p6"):
        st.markdown("#### Detalle del portafolio")
        st.dataframe(m, hide_index=True, width="stretch")

elif pagina == "Riesgos":
    hero("Riesgos Estratégicos", "Matriz de riesgos tecnológicos por frente, componente e impacto")
    r = D["riesgos"]
    imp = st.pills("Impacto", ["Alto", "Medio", "Bajo"], selection_mode="multi", default=["Alto", "Medio", "Bajo"])
    r = r[r["IMPACTO"].isin(imp or [])]
    c = st.columns(4)
    kpi(c[0], "🛡️", "Total riesgos", len(r), f"{r['FRENTE'].nunique()} frentes", INDIGO)
    for col, (nivel, ico) in zip(c[1:], [("Alto", "🔴"), ("Medio", "🟠"), ("Bajo", "🟢")]):
        n = int((r["IMPACTO"] == nivel).sum())
        kpi(col, ico, f"Impacto {nivel.lower()}", n, f"{n / max(len(r), 1):.0%} del total", COLOR_IMPACTO[nivel])
    espacio()
    izq, der = st.columns([3, 2])
    g = r.groupby(["FRENTE", "IMPACTO"]).size().rename("Riesgos").reset_index()
    fig = px.bar(g, y="FRENTE", x="Riesgos", color="IMPACTO", orientation="h", color_discrete_map=COLOR_IMPACTO,
                 title="Riesgos por frente tecnológico", category_orders={"IMPACTO": ["Alto", "Medio", "Bajo"]})
    grafico(fig, 380, izq.container(key="card_k1"))
    fig = px.pie(r, names="IMPACTO", hole=.65, color="IMPACTO", color_discrete_map=COLOR_IMPACTO, title="Distribución por impacto",
                 category_orders={"IMPACTO": ["Alto", "Medio", "Bajo"]})
    fig.update_traces(sort=False, direction="clockwise")
    fig.update_traces(marker=dict(line=dict(color="white", width=3)), textinfo="value+percent")
    grafico(fig, 380, der.container(key="card_k2"))
    with st.container(key="card_k3"):
        st.markdown("#### Matriz de riesgos")
        st.dataframe(r.style.map(lambda v: f"color:{COLOR_IMPACTO.get(v, '')};font-weight:600" if v in COLOR_IMPACTO else "",
                                 subset=["IMPACTO"]), hide_index=True, width="stretch", height=420)

elif pagina == "Ctx":
    hero("Contexto Estratégico", "Análisis DOFA, fuerzas de Porter e indicadores del dominio TI")
    dofa = D["dofa"]
    estilos = {"Fortaleza": ("💪", VERDE), "Debilidad": ("⚠️", AMBAR), "Oportunidad": ("🌱", CIAN), "Amenaza": ("⚡", ROJO)}
    plural = {"Fortaleza": "Fortalezas", "Debilidad": "Debilidades", "Oportunidad": "Oportunidades", "Amenaza": "Amenazas"}
    c = st.columns(4)
    for col, tipo in zip(c, estilos):
        ico, colr = estilos[tipo]
        items = "".join(f"<div class='chip' style='background:{colr}1a;color:{colr}'>{x}</div>"
                        for x in dofa.loc[dofa["Tipo"] == tipo, "Descripción"].astype(str))
        col.markdown(f"<div class='kpi' style='display:block;border-top:4px solid {colr}'>"
                     f"<div class='lbl' style='margin-bottom:.6rem'>{ico} {plural[tipo]}</div>{items}</div>", unsafe_allow_html=True)
    espacio()
    izq, der = st.columns([1, 1])
    nivel = {"Bajo": 1, "Baja": 1, "Medio-Bajo": 1.5, "Medio": 2, "Media": 2, "Medio-Alto": 2.5, "Alto": 3, "Alta": 3}
    po = D["porter"].copy()
    po["n"] = po["Nivel"].astype(str).str.strip().map(nivel)
    fig = go.Figure(go.Scatterpolar(r=list(po["n"]) + [po["n"].iloc[0]], theta=list(po["Fuerza"]) + [po["Fuerza"].iloc[0]],
                                    fill="toself", line_color=INDIGO, fillcolor="rgba(79,70,229,.2)"))
    fig.update_layout(title="Fuerzas de Porter", polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(range=[0, 3], tickvals=[1, 2, 3],
                      ticktext=["Bajo", "Medio", "Alto"], gridcolor="#e2e8f0", tickfont_size=10),
                      angularaxis=dict(gridcolor="#e2e8f0", tickfont_size=12)), margin=dict(l=130, r=130, t=60, b=40))
    fig.update_traces(customdata=list(po["Nivel"]) + [po["Nivel"].iloc[0]], hovertemplate="%{theta}: %{customdata}<extra></extra>")
    grafico(fig, 420, izq.container(key="card_c1"))
    ind = D["ind_ti"].copy()
    # filas de continuación (celdas combinadas en Excel): se pegan a la fila anterior
    for i in ind.index[ind["INDICADOR"].isna()]:
        prev = ind.index[ind.index.get_loc(i) - 1]
        ind.loc[prev, "META"] = f"{ind.loc[prev, 'META']} {ind.loc[i, 'META'] or ''}".strip()
    ind = ind.dropna(subset=["INDICADOR"])
    with der.container(key="card_c2"):
        st.markdown("#### Indicadores del dominio TI")
        st.dataframe(ind, hide_index=True, width="stretch", height=370,
                     column_config={"INDICADOR": st.column_config.TextColumn(width="large"),
                                    "FÓRMULA DE CÁLCULO": st.column_config.TextColumn(width="large")})

elif pagina == "Calidad":
    hero("Calidad de Datos", "Inconsistencias detectadas en el Excel fuente. El dashboard ya las corrige al calcular, "
                             "pero conviene arreglarlas en el archivo.")
    if not D["alertas"]:
        st.success("✅ No se encontraron inconsistencias.")
    for i, a in enumerate(D["alertas"], 1):
        st.markdown(f"<div class='alerta'><b>#{i}</b>&nbsp;&nbsp;{a}</div>", unsafe_allow_html=True)
