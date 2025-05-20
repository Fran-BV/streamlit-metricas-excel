import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tu Copiloto de Métricas", layout="wide")

st.title("📊 Tu Copiloto de Métricas en Excel")

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Leer con encabezado en la fila 2, ignorando la fila 3
        df = pd.read_excel(uploaded_file, header=1, skiprows=[2])

        # Limpiar columnas sin nombre
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        st.success("✅ Archivo cargado correctamente")
        st.subheader("📄 Vista previa de los datos")
        st.dataframe(df)

        st.subheader("📊 Gráficos Predefinidos")

        # Gráfico de tareas por estado
        if "Status" in df.columns:
            status_counts = df["Status"].value_counts().reset_index()
            fig = px.bar(status_counts, x="index", y="Status",
                         labels={"index": "Estado", "Status": "Cantidad"},
                         title="Tareas por Estado")
            st.plotly_chart(fig, use_container_width=True)

        # SP por Sprint
        if "SP" in df.columns and "Sprint" in df.columns:
            df["SP"] = pd.to_numeric(df["SP"], errors="coerce").fillna(0)
            sprint_sp = df.groupby("Sprint")["SP"].sum().reset_index()
            fig = px.bar(sprint_sp, x="Sprint", y="SP", title="SP por Sprint")
            st.plotly_chart(fig, use_container_width=True)

        # Tiempo promedio en progreso por estado
        if "Time in Progress" in df.columns and "Status" in df.columns:
            df["Time in Progress"] = pd.to_numeric(df["Time in Progress"], errors="coerce").fillna(0)
            time_avg = df.groupby("Status")["Time in Progress"].mean().reset_index()
            fig = px.bar(time_avg, x="Status", y="Time in Progress", title="Tiempo promedio en progreso por Estado")
            st.plotly_chart(fig, use_container_width=True)

        # === Gráfico 1: Evolución de SP e Items por Sprint (CORREGIDO) ===
        if {"Sprint", "SP", "Status"}.issubset(df.columns):
            estados_finalizados = ["Done", "Cancelled", "Ready to deploy", "Resolved"]

            df_filtrado = df[df["Status"].isin(estados_finalizados)].copy()
            df_filtrado["SP"] = pd.to_numeric(df_filtrado["SP"], errors="coerce").fillna(0)

            sp_por_sprint = df_filtrado.groupby("Sprint")["SP"].sum()
            items_por_sprint = df_filtrado.groupby("Sprint").size()

            evolucion = pd.DataFrame({
                "SP": sp_por_sprint,
                "Items": items_por_sprint
            }).reset_index()

            fig = px.line(evolucion, x="Sprint", y=["SP", "Items"], markers=True,
                          title="Evolución de SP e Items por Sprint")
            st.plotly_chart(fig, use_container_width=True)

        # === Gráfico 2: Historias Empezadas vs Terminadas por Sprint (CORREGIDO) ===
        if {"Sprint", "Status"}.issubset(df.columns):
            estados_terminados = ["Done", "Cancelled", "Ready to deploy", "Resolved"]
            estados_empezados = estados_terminados + ["In Progress"]

            df_empezadas = df[df["Status"].isin(estados_empezados)]
            df_terminadas = df[df["Status"].isin(estados_terminados)]

            empezadas_por_sprint = df_empezadas.groupby("Sprint").size()
            terminadas_por_sprint = df_terminadas.groupby("Sprint").size()

            historias = pd.DataFrame({
                "Empezadas": empezadas_por_sprint,
                "Terminadas": terminadas_por_sprint
            }).fillna(0).astype(int).reset_index()

            fig = px.line(historias, x="Sprint", y=["Empezadas", "Terminadas"], markers=True,
                          title="Historias empezadas vs terminadas por Sprint")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
