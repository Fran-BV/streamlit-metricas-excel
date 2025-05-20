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

        columnas_requeridas = ["Sprint", "SP", "summary"]
        if not all(col in df.columns for col in columnas_requeridas):
            st.error(f"❌ Faltan columnas. Se requieren: {columnas_requeridas}")
            st.stop()

        df["SP"] = pd.to_numeric(df["SP"], errors="coerce")

        # Extraer fecha desde el nombre del Sprint si existe (últimos 8 dígitos del nombre)
        def extraer_fecha(sprint_name):
            match = re.search(r"(\d{8})$", str(sprint_name))
            return pd.to_datetime(match.group(1), format="%Y%m%d") if match else pd.NaT

        df["Sprint_fecha"] = df["Sprint"].apply(extraer_fecha)

        # Agrupar por Sprint y resumir
        resumen = df.groupby(["Sprint", "Sprint_fecha"]).agg(
            SP_total=("SP", "sum"),
            Items_total=("summary", "count")
        ).reset_index()

        # Ordenar por la fecha del Sprint (si existe), y limitar a últimos N
        resumen = resumen.sort_values(by="Sprint_fecha", ascending=True)
        resumen = resumen.tail(10)

        fig = px.bar(
            resumen,
            x="Sprint",
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
