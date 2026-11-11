"""
Carga y limpieza de datos del Excel del Dashboard Estratégico de TI.

Todo el cálculo vive aquí, separado del dashboard, para que se pueda
reutilizar (por ejemplo en un notebook o para exportar a Excel).
"""
import os
import re
import tempfile
import time
import urllib.request
from functools import lru_cache
from pathlib import Path

import pandas as pd

CARPETA = Path(__file__).parent
EXCEL_LOCAL = CARPETA / "Extraido_CIO_Completo.xlsx"

# ── Fuente de datos ──────────────────────────────────────────────────────────
# Para leer desde Google Drive, pega aquí el enlace de la hoja de cálculo
# (compartida como "Cualquier persona con el enlace"). Déjalo vacío ("") para
# usar el Excel local de esta carpeta.
URL_GOOGLE = "https://docs.google.com/spreadsheets/d/15VJEg5OykTfv99NhHynsoqQfdea0ij2m/edit"
MINUTOS_REFRESCO = 5          # cada cuánto se vuelve a descargar desde Drive
# Las copias descargadas se guardan FUERA de OneDrive (OneDrive bloquea los archivos mientras sincroniza).
CACHE_DRIVE = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "DashboardTI"

ARCHIVO = EXCEL_LOCAL           # archivo que se está usando (se ajusta en sincronizar)
ESTADO_FUENTE = "Excel local"


def _urls_descarga(url: str) -> list[str]:
    m = re.search(r"/d/([\w-]+)", url) or re.search(r"[?&]id=([\w-]+)", url)
    if not m:
        raise ValueError("No se reconoce el enlace de Google Drive.")
    fid = m.group(1)
    return [f"https://docs.google.com/spreadsheets/d/{fid}/export?format=xlsx",   # Google Sheets
            f"https://drive.google.com/uc?export=download&id={fid}"]              # .xlsx subido tal cual


def _ultima_copia() -> Path | None:
    copias = sorted(CACHE_DRIVE.glob("copia_*.xlsx"))
    return copias[-1] if copias else None


def _descargar() -> Path:
    error = None
    for u in _urls_descarga(URL_GOOGLE):
        try:
            with urllib.request.urlopen(u, timeout=20) as r:
                contenido = r.read()
            if contenido[:2] != b"PK":   # un .xlsx es un zip; si no, Drive devolvió una página de login
                raise ValueError("Drive no devolvió un Excel (¿está compartido con 'Cualquier persona con el enlace'?)")
            CACHE_DRIVE.mkdir(parents=True, exist_ok=True)
            destino = CACHE_DRIVE / f"copia_{time.strftime('%Y%m%d_%H%M%S')}_{time.time_ns() % 10**6:06d}.xlsx"
            destino.write_bytes(contenido)   # archivo nuevo: nunca se sobrescribe uno en uso
            for vieja in sorted(CACHE_DRIVE.glob("copia_*.xlsx"))[:-3]:   # limpia copias antiguas
                try:
                    vieja.unlink()
                except OSError:
                    pass
            return destino
        except Exception as e:  # noqa: BLE001
            error = e
    raise error


def sincronizar(forzar: bool = False) -> str:
    """Descarga el Excel desde Drive si hay URL configurada y la copia es vieja.
    Devuelve un texto con el estado de la fuente."""
    global ARCHIVO, ESTADO_FUENTE
    if not URL_GOOGLE.strip():
        ARCHIVO, ESTADO_FUENTE = EXCEL_LOCAL, "Excel local"
        return ESTADO_FUENTE
    copia = _ultima_copia()
    vieja = copia is None or (time.time() - copia.stat().st_mtime > MINUTOS_REFRESCO * 60)
    if forzar or vieja:
        try:
            copia = _descargar()
        except Exception as e:  # noqa: BLE001
            if copia:
                ARCHIVO, ESTADO_FUENTE = copia, f"Google Drive (sin conexión, usando última copia): {e}"
            else:
                ARCHIVO, ESTADO_FUENTE = EXCEL_LOCAL, f"No se pudo leer Drive, usando Excel local: {e}"
            return ESTADO_FUENTE
    ARCHIVO, ESTADO_FUENTE = copia, "Google Drive"
    return ESTADO_FUENTE

# Indicadores del BSC donde un valor MENOR es mejor (la meta es un tope).
MENOR_ES_MEJOR = {"Costo Total Propiedad TI"}


def _limpiar_texto(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)


@lru_cache(maxsize=4)
def _libro(ruta: str, mtime: float, header) -> dict[str, pd.DataFrame]:
    """Lee TODAS las hojas de una vez; se vuelve a leer solo si el Excel cambia."""
    return pd.read_excel(ruta, sheet_name=None, header=header)


def _hoja(hoja: str, header=0) -> pd.DataFrame:
    return _libro(str(ARCHIVO), ARCHIVO.stat().st_mtime, header)[hoja].copy()


def _leer(hoja: str) -> pd.DataFrame:
    df = _hoja(hoja)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]  # columnas vacías
    df.columns = [str(c).strip() for c in df.columns]
    return df.dropna(how="all")


# --------------------------------------------------------------------------
# Tablas
# --------------------------------------------------------------------------
def presupuesto() -> pd.DataFrame:
    """Presupuesto por tipo de iniciativa y año (formato largo)."""
    raw = _hoja("Presupuesto proyect", header=None)
    fila_anios = raw.index[raw.apply(lambda r: r.astype(str).str.contains("Presupuesto 20").any(), axis=1)][0]
    cols = {i: str(v).replace("Presupuesto", "").strip()
            for i, v in raw.loc[fila_anios].items() if "Presupuesto 20" in str(v)}
    filas = []
    for _, r in raw.loc[fila_anios + 1:].iterrows():
        tipo = str(r[0]).strip()
        if tipo in ("nan", "") or tipo.lower().startswith("global"):
            continue  # se omite el total: se recalcula
        for i, anio in cols.items():
            filas.append({"Tipo": tipo.replace("Iniciativas ", ""), "Año": int(anio),
                          "Presupuesto": pd.to_numeric(r[i], errors="coerce")})
    return pd.DataFrame(filas).fillna({"Presupuesto": 0})


def bsc() -> pd.DataFrame:
    df = _leer("BSC")
    df["Perspectiva"] = _limpiar_texto(df["Perspectiva"])
    df["Indicador"] = _limpiar_texto(df["Indicador"])
    df[["Actual", "Meta"]] = df[["Actual", "Meta"]].apply(pd.to_numeric, errors="coerce")

    def cumplimiento(r):
        if r["Indicador"] in MENOR_ES_MEJOR:
            return min(r["Meta"] / r["Actual"], 1.0) if r["Actual"] else None
        return min(r["Actual"] / r["Meta"], 1.0) if r["Meta"] else None

    df["Cumplimiento"] = df.apply(cumplimiento, axis=1)
    return df


def iniciativas_pmo() -> pd.DataFrame:
    """Detalle PMO + fechas de la hoja Iniciativas, con retraso calculado."""
    pmo = _leer("Detalle iniciativa pmo")
    pmo = pmo[pd.to_numeric(pmo["ID"], errors="coerce").notna()].copy()  # quita fila de total
    pmo = pmo.replace("#REF!", pd.NA)
    pmo["Estado"] = _limpiar_texto(pmo["Estado"]).str.capitalize()  # "En proceso" == "En Proceso"
    pmo["Presupuesto"] = pd.to_numeric(pmo["PPTO PARA ROADMAP PPT"], errors="coerce")
    pmo["Siglas"] = _limpiar_texto(pmo["Siglas"])

    fechas = _leer("Iniciativas").iloc[:, :7]
    fechas.columns = ["Siglas", "Nombre", "Inicio LB", "Fin LB", "Inicio Real", "Fecha Acta Inicio", "Fin Proyectado"]
    fechas["Siglas"] = _limpiar_texto(fechas["Siglas"])
    for c in fechas.columns[2:]:
        fechas[c] = pd.to_datetime(fechas[c], errors="coerce")

    df = pmo.merge(fechas.drop(columns="Nombre"), on="Siglas", how="left")
    df["Retraso (días)"] = (df["Fin Proyectado"] - df["Fin LB"]).dt.days
    return df


def iniciativas_dvp() -> pd.DataFrame:
    df = _leer("Detalle iniciativa DVP")
    df = df.rename(columns={"Presupuesto Proyeectado": "Presupuesto",
                            "Iniciativa- proyecto": "Iniciativa",
                            "TIempo estimado alto nivel (semanas)": "Semanas"})
    df = df[df["Iniciativa"].notna()].copy()
    for c in ["Categoria", "Iniciativa", "Tipo", "RUPTURA"]:
        df[c] = _limpiar_texto(df[c])
    df[["Presupuesto", "Semanas", "OPM"]] = df[["Presupuesto", "Semanas", "OPM"]].apply(pd.to_numeric, errors="coerce")
    return df


def maestra() -> pd.DataFrame:
    df = _leer("MAESTRA_INICIATIVAS")
    for c in df.columns[1:]:
        df[c] = _limpiar_texto(df[c])
    return df


def riesgos() -> pd.DataFrame:
    df = _leer("Riesgos")
    df[["FRENTE", "COMPONENTE"]] = df[["FRENTE", "COMPONENTE"]].ffill()  # celdas combinadas
    for c in df.columns:
        df[c] = _limpiar_texto(df[c])
    df["IMPACTO"] = df["IMPACTO"].str.capitalize().replace({"Moderado": "Medio"})
    return df


def arquitectura() -> pd.DataFrame:
    df = _leer("Arquitectura tecnologica")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    return df


def tabla_simple(hoja: str) -> pd.DataFrame:
    df = _leer(hoja)
    for c in df.columns:  # columnas con texto y números mezclados
        if not pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].astype("string")
    return df


# --------------------------------------------------------------------------
# Indicadores resumen
# --------------------------------------------------------------------------
def kpis() -> dict:
    b, p, pmo, dvp, m, r = bsc(), presupuesto(), iniciativas_pmo(), iniciativas_dvp(), maestra(), riesgos()
    por_anio = p.groupby("Año")["Presupuesto"].sum()
    return {
        "presupuesto_por_anio": por_anio.to_dict(),
        "total_iniciativas": len(m),
        "iniciativas_pmo": int((m["Tipo"] == "PMO").sum()),
        "iniciativas_ppt": int((m["Tipo"] == "PPT").sum()),
        "riesgos": len(r),
        "riesgos_altos": int((r["IMPACTO"] == "Alto").sum()),
        "bsc_global": float(b["Cumplimiento"].mean() * 100),
        "pmo_con_retraso": int((pmo["Retraso (días)"] > 0).sum()),
        "retraso_promedio": float(pmo.loc[pmo["Retraso (días)"] > 0, "Retraso (días)"].mean()),
        "presupuesto_digital": float(dvp["Presupuesto"].sum()),
    }


def alertas_calidad() -> list[str]:
    """Inconsistencias encontradas en el Excel original (para corregir en la fuente)."""
    out = []
    pmo_raw = _leer("Detalle iniciativa pmo")
    n_ref = int((pmo_raw == "#REF!").any(axis=1).sum())
    if n_ref:
        out.append(f"Hoja 'Detalle iniciativa pmo': {n_ref} filas con #REF! (MEGA / Objetivo Estratégico).")
    estados = pmo_raw["Estado"].dropna().astype(str).str.strip().unique()
    if len(estados) != len({e.lower() for e in estados}):
        out.append("Estados escritos con distinta mayúscula ('En Proceso' vs 'En proceso'); se unificaron.")
    if (_leer("Riesgos")["IMPACTO"].astype(str).str.strip() == "Moderado").any():
        out.append("Riesgos: se usa 'Moderado' y 'Medio'; se trataron como 'Medio'.")
    resumen = tabla_simple("Resumen Ejecutivo").set_index("Indicador")["Valor"]
    n_pmo = int((maestra()["Tipo"] == "PMO").sum())
    if "Total Iniciativas PMO" in resumen and int(resumen["Total Iniciativas PMO"]) != n_pmo:
        out.append(f"'Resumen Ejecutivo' dice {int(resumen['Total Iniciativas PMO'])} iniciativas PMO, pero hay {n_pmo}.")
    if "BSC Global" in resumen:
        out.append(f"'Resumen Ejecutivo' trae BSC Global = {resumen['BSC Global']} (valor fijo). "
                   f"Recalculado como % de cumplimiento vs meta: {kpis()['bsc_global']:.1f}.")
    sin_clasif = int((maestra()["Dominio"] == "Por Clasificar").sum())
    if sin_clasif:
        out.append(f"MAESTRA_INICIATIVAS: {sin_clasif} iniciativas 'Por Clasificar' en Dominio/Cadena/Pilar.")
    return out


if __name__ == "__main__":
    from pprint import pprint
    pprint(kpis())
    print("\nAlertas de calidad:")
    for a in alertas_calidad():
        print(" -", a)
