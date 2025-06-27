import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Métricas Interactivo")

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

    # Filtros comunes
    st.sidebar.header("🔍 Filtros globales")

    if 'sprint' in df.columns:
        sprints_seleccionados = st.sidebar.multiselect("Filtrar por Sprint", df['sprint'].dropna().unique())
        if sprints_seleccionados:
            df = df[df['sprint'].isin(sprints_seleccionados)]

    if 'status' in df.columns:
        status_seleccionados = st.sidebar.multiselect("Filtrar por Status", df['status'].dropna().unique())
        if status_seleccionados:
            df = df[df['status'].isin(status_seleccionados)]

    if 'assignee' in df.columns:
        assignees_seleccionados = st.sidebar.multiselect("Filtrar por Assignee", df['assignee'].dropna().unique())
        if assignees_seleccionados:
            df = df[df['assignee'].isin(assignees_seleccionados)]

    # Cantidad de gráficos
    st.sidebar.header("🎨 Configuración de gráficos")
    num_graficos = st.sidebar.number_input("¿Cuántos gráficos quieres mostrar?", min_value=1, max_value=5, value=2)

    for i in range(num_graficos):
        st.markdown(f"## 📊 Gráfico {i + 1}")
        col1, col2 = st.columns([3, 1])

        with col2:
            tipo = st.selectbox(f"Tipo de gráfico {i+1}", ["Líneas", "Barras", "Área", "Boxplot", "Scatter"], key=f"tipo_{i}")
            x = st.selectbox(f"Eje X {i+1}", df.columns, key=f"x_{i}")
            y = st.multiselect(f"Ejes Y {i+1}", df.columns, key=f"y_{i}")
            color = st.color_picker(f"Color base {i+1}", "#1f77b4", key=f"color_{i}")

        with col1:
            if x and y:
                df_grouped = df.groupby(x)[y].sum().reset_index()

                fig, ax = plt.subplots(figsize=(8, 4))

                for col in y:
                    if tipo == "Líneas":
                        ax.plot(df_grouped[x], df_grouped[col], marker="o", label=col, color=color)
                    elif tipo == "Barras":
                        ax.bar(df_grouped[x], df_grouped[col], label=col, color=color)
                    elif tipo == "Área":
                        ax.fill_between(df_grouped[x], df_grouped[col], label=col, color=color, alpha=0.4)
                    elif tipo == "Boxplot":
                        sns.boxplot(data=df, x=x, y=col, color=color, ax=ax)
                    elif tipo == "Scatter":
                        ax.scatter(df_grouped[x], df_grouped[col], label=col, color=color)

                ax.set_title(f"{tipo} - {', '.join(y)} por {x}")
                ax.set_xlabel(x.capitalize())
                ax.set_ylabel("Valor")
                ax.tick_params(axis='x', rotation=45)
                ax.legend()
                st.pyplot(fig)

    # Exportar todo a PDF
    st.markdown("---")
    st.subheader("📤 Exportar gráficos")
    if st.button("Descargar como PDF"):
        from matplotlib.backends.backend_pdf import PdfPages
        import io

        buf = io.BytesIO()
        with PdfPages(buf) as pdf:
            for i in range(num_graficos):
                x = st.session_state.get(f"x_{i}")
                y = st.session_state.get(f"y_{i}")
                tipo = st.session_state.get(f"tipo_{i}")
                color = st.session_state.get(f"color_{i}")

                if x and y:
                    df_grouped = df.groupby(x)[y].sum().reset_index()
                    fig, ax = plt.subplots(figsize=(8, 4))
                    for col in y:
                        if tipo == "Líneas":
                            ax.plot(df_grouped[x], df_grouped[col], marker="o", label=col, color=color)
                        elif tipo == "Barras":
                            ax.bar(df_grouped[x], df_grouped[col], label=col, color=color)
                        elif tipo == "Área":
                            ax.fill_between(df_grouped[x], df_grouped[col], label=col, color=color, alpha=0.4)
                        elif tipo == "Boxplot":
                            sns.boxplot(data=df, x=x, y=col, color=color, ax=ax)
                        elif tipo == "Scatter":
                            ax.scatter(df_grouped[x], df_grouped[col], label=col, color=color)
                    ax.set_title(f"{tipo} - {', '.join(y)} por {x}")
                    ax.set_xlabel(x.capitalize())
                    ax.set_ylabel("Valor")
                    ax.legend()
                    pdf.savefig(fig)
                    plt.close(fig)

        st.download_button(
            label="📥 Descargar PDF",
            data=buf.getvalue(),
            file_name="graficos_dashboard.pdf",
            mime="application/pdf"
        )
