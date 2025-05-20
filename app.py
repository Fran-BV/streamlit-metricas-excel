import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Métricas Interactivo")

# Inicializar almacenamiento de gráficos
if "graficos" not in st.session_state:
    st.session_state["graficos"] = []

# Cargar archivo
archivo = st.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()

    df = df.rename(columns={
        'sprint name': 'sprint',
        'sprint': 'sprint',
        'status': 'status',
        'assignee': 'assignee',
        'sp': 'sp',
        'summary': 'summary',
        'cycle time': 'cycle time'
    })

    st.write("📋 Columnas detectadas:", df.columns.tolist())
    st.subheader("Vista previa de los datos")
    st.dataframe(df)

    st.sidebar.header("🎛️ Configuración del gráfico")

    tipo_grafico = st.sidebar.selectbox("Tipo de gráfico", ["📈 Líneas", "📊 Barras"])
    columnas = df.columns.tolist()
    columna_x = st.sidebar.selectbox("Columna para eje X (agrupación)", columnas)
    columnas_y = st.sidebar.multiselect("Columnas para eje Y", columnas)
    metrica = st.sidebar.radio("Métrica a aplicar", ["sum", "mean", "count"])

    # Elegir color por cada métrica
    colores = {}
    if columnas_y:
        st.sidebar.subheader("🎨 Colores por métrica")
        for col in columnas_y:
            colores[col] = st.sidebar.color_picker(f"Color para {col}", "#1f77b4")

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

    if columna_x and columnas_y:
        # Solo columnas numéricas para líneas
        if tipo_grafico == "📈 Líneas":
            columnas_y = [col for col in columnas_y if pd.api.types.is_numeric_dtype(df[col])]
            if not columnas_y:
                st.warning("Selecciona columnas numéricas para gráficos de líneas.")
                st.stop()

        st.subheader(f"{tipo_grafico}: {' y '.join(columnas_y)} por {columna_x} ({metrica})")

        agrupaciones = {col: metrica for col in columnas_y}
        df_grouped = df.groupby(columna_x).agg(agrupaciones).reset_index()

        st.write("📋 Datos agrupados:")
        st.dataframe(df_grouped)

        csv = df_grouped.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar datos agrupados", data=csv, file_name="datos_agrupados.csv", mime="text/csv")

        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(10, 5))

        for col in columnas_y:
            color = colores.get(col, None)
            if tipo_grafico == "📈 Líneas":
                sns.lineplot(data=df_grouped, x=columna_x, y=col, marker='o', label=col, ax=ax, color=color)
            else:
                ax.bar(df_grouped[columna_x], df_grouped[col], label=col, color=color)

        ax.set_xlabel(columna_x.capitalize())
        ax.set_ylabel("Valor")
        ax.set_title(f"{', '.join(columnas_y)} por {columna_x}")
        ax.tick_params(axis='x', rotation=45)
        ax.legend()

        # Mostrar y guardar gráfico
        st.pyplot(fig)

        # Guardar para PDF
        buf = BytesIO()
        fig.savefig(buf, format="png")
        st.session_state["graficos"].append(buf.getvalue())  # Guardamos imagen en memoria

        # Botón para exportar todos en PDF
        if st.button("📄 Exportar todos los gráficos a PDF"):
            pdf_bytes = BytesIO()
            with PdfPages(pdf_bytes) as pdf:
                for img_bytes in st.session_state["graficos"]:
                    fig_pdf = plt.figure(figsize=(10, 5))
                    ax_pdf = fig_pdf.add_subplot(111)
                    img = plt.imread(BytesIO(img_bytes))
                    ax_pdf.imshow(img)
                    ax_pdf.axis('off')
                    pdf.savefig(fig_pdf)
                    plt.close(fig_pdf)

            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_bytes.getvalue(),
                file_name="graficos.pdf",
                mime="application/pdf"
            )

    else:
        st.info("Selecciona una columna para eje X y al menos una para eje Y.")
