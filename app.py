import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tu Copiloto de Métricas", layout="wide")
st.title("📊 Tu Copiloto de Métricas en Excel")

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=1, skiprows=[2])
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        st.success("✅ Archivo cargado correctamente")
        st.subheader("📄 Vista previa de los datos")
        st.dataframe(df)

        st.subheader("📊 Filtros")
        if "Sprint" in df.columns:
            sprint_options = df["Sprint"].dropna().unique().tolist()
            selected_sprints = st.multiselect("Selecciona uno o más Sprints", options=sprint_options, default=sprint_options)
            df = df[df["Sprint"].isin(selected_sprints)]

        if "Created" in df.columns or "Date" in df.columns:
            date_column = "Created" if "Created" in df.columns else "Date"
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            min_date = df[date_column].min()
            max_date = df[date_column].max()
            start_date, end_date = st.date_input("Filtrar por rango de fechas", [min_date, max_date])
            df = df[(df[date_column] >= pd.to_datetime(start_date)) & (df[date_column] <= pd.to_datetime(end_date))]

        st.subheader("📊 Gráficos Predefinidos")

        if "Status" in df.columns:
            status_counts = df["Status"].value_counts().reset_index()
            fig = px.bar(status_counts, x="index", y="Status", labels={"index": "Estado", "Status": "Cantidad"})
            st.plotly_chart(fig, use_container_width=True)

        if "SP" in df.columns and "Sprint" in df.columns:
            sprint_sp = df.groupby("Sprint")["SP"].sum().reset_index()
            fig = px.bar(sprint_sp, x="Sprint", y="SP", title="SP por Sprint")
            st.plotly_chart(fig, use_container_width=True)

        if "Time in Progress" in df.columns and "Status" in df.columns:
            df["Time in Progress"] = pd.to_numeric(df["Time in Progress"], errors="coerce")
            df_valid = df.dropna(subset=["Time in Progress"])  # Elimina filas con NaN en 'Time in Progress'
    
        if not df_valid.empty:  # Si hay datos válidos para calcular el promedio
            time_avg = df_valid.groupby("Status")["Time in Progress"].mean().reset_index()
            fig = px.bar(time_avg, x="Status", y="Time in Progress", title="Tiempo promedio en progreso por Estado")
            st.plotly_chart(fig, use_container_width=True)
        else:  # Si no hay datos válidos
            st.warning("No hay datos válidos numéricos en 'Time in Progress' para calcular promedios.")

        if "Sprint" in df.columns and "SP" in df.columns:
            sprint_data = df.groupby("Sprint").agg(
                SP_total=("SP", "sum"),
                Items_total=("SP", "count")
            ).reset_index()
            fig = px.line(sprint_data, x="Sprint", y=["SP_total", "Items_total"],
                          labels={"value": "Cantidad", "variable": "Métrica"},
                          title="Evolución de SP e Ítems por Sprint")
            st.plotly_chart(fig, use_container_width=True)

        estados_finales = ["Done", "Cancelled", "Ready to deploy", "Resolved"]
        if "Sprint" in df.columns and "Status" in df.columns and "Summary" in df.columns:
            historias = df.groupby("Sprint").agg(
                Empezadas=("Summary", "count"),
                Terminadas=("Status", lambda x: x.isin(estados_finales).sum())
            ).reset_index()
            fig = px.line(historias, x="Sprint", y=["Empezadas", "Terminadas"],
                          labels={"value": "Cantidad de historias", "variable": "Estado"},
                          title="Historias empezadas vs terminadas por Sprint")
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

