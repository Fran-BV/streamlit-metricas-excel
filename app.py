import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import io

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Métricas Interactivo")

# Cargar archivo
archivo = st.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    # Leer Excel y limpiar nombres de columnas
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres

    # Renombrar columnas comunes para asegurar compatibilidad
    df = df.rename(columns={
        'sprint name': 'sprint',
        'sprint': 'sprint',
        'status': 'status',
        'assignee': 'assignee',
        'sp': 'sp',
        'summary': 'summary',
        'cycle time': 'cycle time'
    })

    # Mostrar columnas para verificar
    st.write("📋 Columnas detectadas:", df.columns.tolist())

    # Vista previa de datos
    st.subheader("Vista previa de los datos")
    st.dataframe(df)

    # === SIDEBAR ===
    st.sidebar.header("🎛️ Configuración del gráfico")

    # Tipo de gráfico
    tipo_grafico = st.sidebar.selectbox("Tipo de gráfico", ["📈 Líneas", "📊 Barras"])

    # Columnas disponibles
    columnas = df.columns.tolist()
    columna_x = st.sidebar.selectbox("Columna para eje X (agrupación)", columnas)
    columnas_y = st.sidebar.multiselect("Columnas para eje Y", columnas)

    # Filtros
    st.sidebar.header("🔍 Filtros")

    if 'sprint' in df.columns:
        sprints = df['sprint'].dropna().unique().tolist()
        sprints_seleccionados = st.sidebar.multiselect("Filtrar por Sprint", sprints)
        if sprints_seleccionados:
            df = df[df['sprint'].isin(sprints_seleccionados)]

    if 'status' in df.columns:
        status_vals = df['status'].dropna().unique().tolist()
        status_seleccionados = st.sidebar.multiselect("Filtrar por Status", status_vals)
        if status_seleccionados:
            df = df[df['status'].isin(status_seleccionados)]

    if 'assignee' in df.columns:
        assignees = df['assignee'].dropna().unique().tolist()
        assignees_seleccionados = st.sidebar.multiselect("Filtrar por Assignee", assignees)
        if assignees_seleccionados:
            df = df[df['assignee'].isin(assignees_seleccionados)]

    # === GRÁFICO ===
    if columna_x and columnas_y:
        st.subheader(f"{tipo_grafico}: {' y '.join(columnas_y)} por {columna_x}")

        # Agrupación
        agrupaciones = {}
        for col in columnas_y:
            if col == "summary":
                agrupaciones[col] = pd.NamedAgg(column=col, aggfunc=lambda x: x.nunique())
            elif pd.api.types.is_numeric_dtype(df[col]):
                agrupaciones[col] = pd.NamedAgg(column=col, aggfunc="sum")
            else:
                agrupaciones[col] = pd.NamedAgg(column=col, aggfunc="count")

        df_grouped = df.groupby(columna_x).agg(**agrupaciones).reset_index()

        st.write("📋 Datos agrupados:")
        st.dataframe(df_grouped)

        # Crear gráfico
        fig, ax = plt.subplots(figsize=(10, 5))

        for col in columnas_y:
            if tipo_grafico == "📈 Líneas":
                ax.plot(df_grouped[columna_x], df_grouped[col], marker='o', label=col)
            else:
                ax.bar(df_grouped[columna_x], df_grouped[col], label=col)

        ax.set_xlabel(columna_x.capitalize())
        ax.set_ylabel("Valor")
        ax.set_title(f"{', '.join(columnas_y)} por {columna_x}")
        ax.tick_params(axis='x', rotation=45)
        ax.legend()
        st.pyplot(fig)

        # Descargar como PDF
        buf = io.BytesIO()
        fig.savefig(buf, format="pdf")
        buf.seek(0)

        st.download_button(
            label="📥 Descargar gráfico como PDF",
            data=buf,
            file_name="grafico_dashboard.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Selecciona una columna para eje X y al menos una para eje Y.")
