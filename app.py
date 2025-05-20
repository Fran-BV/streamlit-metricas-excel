import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tu Copiloto de Métricas", layout="wide")
st.title("📊 Tu Copiloto de Métricas en Excel")

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Leer el archivo Excel con encabezado en la fila 2 (índice 1) y omitir fila 3 (índice 2)
        df = pd.read_excel(uploaded_file, header=1, skiprows=[2])
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Eliminar columnas sin nombre

        st.success("✅ Archivo cargado correctamente")
        st.subheader("📄 Vista previa de los datos")
        st.dataframe(df)

        st.subheader("📊 Gráficos Predefinidos")

        # Tareas por Estado
        if "Status" in df.columns:
            status_counts = df["Status"].value_counts().reset_index()
            status_counts.columns = ["Estado", "Cantidad"]
            fig1 = px.bar(status_counts, x="Estado", y="Cantidad", title="Tareas por Estado")
            st.plotly_chart(fig1, use_container_width=True)

        # Evolución de SP e Items por Sprint
        if "Sprint" in df.columns and "SP" in df.columns:
            df_sp = df[["Sprint", "SP"]].dropna()
            df_sp["SP"] = pd.to_numeric(df_sp["SP"], errors="coerce")
            sp_sum = df_sp.groupby("Sprint").agg(
                Total_SP=("SP", "sum"),
                Cantidad_Items=("SP", "count")
            ).reset_index()
            fig2 = px.bar(sp_sum, x="Sprint", y=["Total_SP", "Cantidad_Items"],
                          title="Evolución de SP e Items por Sprint",
                          barmode="group")
            st.plotly_chart(fig2, use_container_width=True)

        # SP promedio por responsable
        if "Responsable" in df.columns and "SP" in df.columns:
            df_resp = df[["Responsable", "SP"]].dropna()
            df_resp["SP"] = pd.to_numeric(df_resp["SP"], errors="coerce")
            sp_avg = df_resp.groupby("Responsable").mean(numeric_only=True).reset_index()
            fig3 = px.bar(sp_avg, x="Responsable", y="SP", title="SP Promedio por Responsable")
            st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
