import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Métricas Ágiles", layout="wide")

st.title("📊 Dashboard de Métricas Ágiles")

archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    try:
        df = pd.read_excel(archivo)

        st.success("✅ Archivo cargado correctamente")

        if st.checkbox("🔍 Mostrar tabla de datos"):
            st.dataframe(df, use_container_width=True)

        columnas_requeridas = ["Sprint", "Status", "summary", "SP"]
        if not all(col in df.columns for col in columnas_requeridas):
            st.warning(f"⚠️ El archivo debe contener las siguientes columnas: {columnas_requeridas}")
            st.stop()

        # -----------------------------
        # 1. Evolución de SP e ítems cerrados por Sprint
        # -----------------------------

        st.markdown("### ✅ Evolución de SP e ítems completados por Sprint")

        estados_cerrados = ["Done", "Cancelled", "Ready to deploy", "Resolved"]
        df_cerrados = df[df["Status"].isin(estados_cerrados)].copy()
        df_cerrados["SP"] = pd.to_numeric(df_cerrados["SP"], errors="coerce")

        evolucion = df_cerrados.groupby("Sprint").agg(
            SP_total=("SP", "sum"),
            Items_total=("summary", "count")
        ).reset_index()

        fig1 = px.bar(
            evolucion,
            x="Sprint",
            y=["SP_total", "Items_total"],
            barmode="group",
            title="SP e Ítems completados por Sprint",
            height=400
        )
        fig1.update_layout(
            xaxis_title="Sprint",
            yaxis_title="Cantidad",
            legend_title_text="Métrica",
            margin=dict(l=20, r=20, t=60, b=20)
        )
        st.plotly_chart(fig1, use_container_width=True)

        # -----------------------------
        # 2. Historias empezadas vs. terminadas por Sprint
        # -----------------------------

        st.markdown("### 📈 Historias empezadas vs. terminadas por Sprint")

        estados_empezadas = estados_cerrados + ["In Progress", "QA", "Code review"]
        df_empezadas = df[df["Status"].isin(estados_empezadas)]
        df_terminadas = df[df["Status"].isin(estados_cerrados)]

        sprints_unicos = sorted(df["Sprint"].dropna().unique())

        empezadas = df_empezadas.groupby("Sprint")["summary"].count()
        terminadas = df_terminadas.groupby("Sprint")["summary"].count()

        data_empezadas_vs_terminadas = pd.DataFrame({
            "Sprint": sprints_unicos,
            "Empezadas": [empezadas.get(s, 0) for s in sprints_unicos],
            "Terminadas": [terminadas.get(s, 0) for s in sprints_unicos]
        })

        fig2 = px.bar(
            data_empezadas_vs_terminadas,
            x="Sprint",
            y=["Empezadas", "Terminadas"],
            barmode="group",
            title="Historias empezadas vs. terminadas",
            height=400
        )
        fig2.update_layout(
            xaxis_title="Sprint",
            yaxis_title="Cantidad de historias",
            legend_title_text="Estado",
            margin=dict(l=20, r=20, t=60, b=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("💡 Sube un archivo .xlsx con tus métricas para comenzar.")
