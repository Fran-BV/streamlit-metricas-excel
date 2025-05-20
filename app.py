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

        # ========== GRÁFICOS PREDEFINIDOS ==========
st.subheader("📊 Gráficos Predefinidos")

# Gráfico de tareas por estado
if "Status" in df.columns:
    status_counts = df["Status"].value_counts().reset_index()
    status_counts.columns = ["Estado", "Cantidad"]
    fig = px.bar(status_counts, x="Estado", y="Cantidad", title="Tareas por Estado")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No se encontró la columna 'Status'.")

# Gráfico de SP por sprint (si existe)
if "SP" in df.columns and "Sprint" in df.columns:
    sprint_sp = df.groupby("Sprint")["SP"].sum().reset_index()
    fig = px.bar(sprint_sp, x="Sprint", y="SP", title="SP por Sprint")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No se encontraron columnas 'SP' y 'Sprint'.")

# Promedio de "Time in Progress" por estado
if "Time in Progress" in df.columns and "Status" in df.columns:
    time_avg = df.groupby("Status")["Time in Progress"].mean().reset_index()
    fig = px.bar(time_avg, x="Status", y="Time in Progress", title="Tiempo promedio en progreso por Estado")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No se encontraron columnas 'Time in Progress' y 'Status'.")
    
 except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
