import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="Gráfico de SP e Ítems", layout="centered")
st.title("📊 SP e Ítems por Sprint")

archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    try:
        df = pd.read_excel(archivo)

        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()

        # Mapear nombres comunes a lo que necesitamos
        columnas_alias = {
            "sprint": "sprint",
            "sp": "sp",
            "story point": "sp",
            "story points": "sp",
            "summary": "summary",
            "resumen": "summary",
        }

        # Crear nuevo DataFrame con nombres esperados
        df = df.rename(columns={col: columnas_alias.get(col, col) for col in df.columns})

        columnas_requeridas = ["sprint", "sp", "summary"]
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"❌ Faltan columnas. Se requieren: {columnas_requeridas}")
            st.write("Columnas encontradas:", df.columns.tolist())
            st.stop()

        df["sp"] = pd.to_numeric(df["sp"], errors="coerce")

        def extraer_fecha(sprint_name):
            match = re.search(r"(\d{8})$", str(sprint_name))
            return pd.to_datetime(match.group(1), format="%Y%m%d") if match else pd.NaT

        df["sprint_fecha"] = df["sprint"].apply(extraer_fecha)

        resumen = df.groupby(["sprint", "sprint_fecha"]).agg(
            SP_total=("sp", "sum"),
            Items_total=("summary", "count")
        ).reset_index()

        resumen = resumen.sort_values(by="sprint_fecha", ascending=True)
        resumen = resumen.tail(10)

        fig = px.bar(
            resumen,
            x="sprint",
            y=["SP_total", "Items_total"],
            barmode="group",
            title="✅ Suma de SP e Ítems por Sprint",
            height=400
        )
        fig.update_layout(
            xaxis_title="Sprint",
            yaxis_title="Cantidad",
            legend_title="Métrica",
            margin=dict(l=40, r=40, t=60, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("⬆️ Sube un archivo Excel para comenzar.")
