import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Métricas Ágiles", layout="wide")

st.title("📊 Dashboard de Métricas Ágiles")

# Subida del archivo
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    try:
        df = pd.read_excel(archivo)

        st.success("✅ Archivo cargado exitosamente.")

        # Mostrar el DataFrame si el usuario quiere
        if st.checkbox("📄 Mostrar datos cargados"):
            st.dataframe(df)

        columnas_requeridas = ["Sprint", "Status", "summary", "SP"]
        if not all(col in df.columns for col in columnas_requeridas):
            st.warning(f"El archivo debe contener las siguientes columnas: {columnas_requeridas}")
            st.stop()

        # ============================
        # 1. Evolución de SP e Items por Sprint (solo tareas cerradas)
        # ============================

        estados_cerrados = ["Done", "Cancelled", "Ready to deploy", "Resolved"]
        df_filtrado_cerrados = df[df["Status"].isin(estados_cerrados)].copy()
        df_filtrado_cerrados["SP"] = pd.to_numeric(df_filtrado_cerrados["SP"], errors="coerce")

        evolucion = df_filtrado_cerrados.groupby("Sprint").agg(
            SP_total=("SP", "sum"),
            Items_total=("summary", "count")
        ).reset_index()

        st.subheader("✅ SP e Items completados por Sprint (solo tareas cerradas)")
        fig1 = px.bar(
            evolucion,
            x="Sprint",
            y=["SP_total", "Items_total"],
            barmode="group",
            title="✅ SP e Items completados por Sprint"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ============================
        # 2. Historias Empezadas vs Terminadas por Sprint
        # ============================

        estados_empezadas = ["In Progress", "QA", "Code review"] + estados_cerrados
        df_empezadas = df[df["Status"].isin(estados_empezadas)].copy()
        df_terminadas = df[df["Status"].isin(estados_cerrados)].copy()

        sprints_unicos = sorted(df["Sprint"].dropna().unique())

        empezadas = df_empezadas.groupby("Sprint")["summary"].count()
        terminadas = df_terminadas.groupby("Sprint")["summary"].count()

        empezadas_vs_terminadas = pd.DataFrame({
            "Sprint": sprints_unicos,
            "Empezadas": [empezadas.get(s, 0) for s in sprints_unicos],
            "Terminadas": [terminadas.get(s, 0) for s in sprints_unicos]
        })

        st.subheader("📈 Historias Empezadas vs Terminadas por Sprint")
        fig2 = px.bar(
            empezadas_vs_terminadas,
            x="Sprint",
            y=["Empezadas", "Terminadas"],
            barmode="group",
            title="📈 Historias Empezadas vs Terminadas por Sprint"
        )
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("📂 Por favor, sube un archivo Excel para continuar.")
