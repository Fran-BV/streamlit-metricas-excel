import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Métricas Ágiles")

uploaded_file = st.file_uploader("Carga un archivo Excel", type=[".xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("Vista previa de los datos")
        st.dataframe(df.head())

        # Detectar columnas numéricas
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_columns:
            st.warning("⚠️ No se encontraron columnas numéricas en el archivo.")
        else:
            # Gráfico 1: Evolución de SP e Items por Sprint (solo cerradas)
            estados_cerrados = ["Done", "Cancelled", "Ready to deploy", "Resolved"]
            df_filtrado_cerrados = df[df["Status"].isin(estados_cerrados)]
            df_filtrado_cerrados["SP"] = pd.to_numeric(df_filtrado_cerrados["SP"], errors="coerce")

            if "Sprint" in df.columns and "SP" in df.columns and "summary" in df.columns:
                evolucion = df_filtrado_cerrados.groupby("Sprint").agg(
                    SP_total=("SP", "sum"),
                    Items_total=("summary", "count")
                ).reset_index()

                fig1 = px.bar(
                    evolucion,
                    x="Sprint",
                    y=["SP_total", "Items_total"],
                    barmode="group",
                    title="✅ SP e Items completados por Sprint (solo tareas cerradas)"
                )
                st.plotly_chart(fig1, use_container_width=True)

            # Gráfico 2: Historias Empezadas vs Terminadas por Sprint
            estados_empezadas = ["Done", "Cancelled", "Ready to deploy", "Resolved", "In Progress", "QA", "Code review"]
            estados_terminadas = ["Done", "Cancelled", "Ready to deploy", "Resolved"]

            df_empezadas = df[df["Status"].isin(estados_empezadas)]
            df_terminadas = df[df["Status"].isin(estados_terminadas)]

            if "Sprint" in df.columns and "summary" in df.columns:
                empezadas_vs_terminadas = pd.DataFrame({
                    "Sprint": sorted(df["Sprint"].dropna().unique()),
                    "Empezadas": df_empezadas.groupby("Sprint")["summary"].count(),
                    "Terminadas": df_terminadas.groupby("Sprint")["summary"].count()
                }).fillna(0).reset_index()

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
    st.info("Por favor, carga un archivo Excel para comenzar.")
    
