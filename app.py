import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Métricas Interactivo")

# Cargar archivo
archivo = st.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    # Leer Excel y limpiar nombres de columnas
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Quitar espacios, pasar a minúsculas

    # Renombrar columnas clave
    df = df.rename(columns={
        'summary': 'summary',
        'sp': 'sp',
        'sprint': 'sprint',
        'cycle time': 'cycle time',
        'status': 'status'  # por si se usa más adelante
    })

    # Mostrar columnas detectadas
    st.write("Columnas detectadas:", df.columns.tolist())

    # Mostrar preview
    st.subheader("Vista previa de los datos")
    st.dataframe(df)

    # Sidebar - Configuración dinámica
    st.sidebar.header("🎛️ Configuración del gráfico")

    # Tipo de gráfico
    tipo_grafico = st.sidebar.selectbox("Tipo de gráfico", ["📈 Líneas", "📊 Barras"])

    # Columnas categóricas para eje X
    columnas_cat = [col for col in df.columns if df[col].dtype == 'object']
    columna_x = st.sidebar.selectbox("Columna para eje X (agrupación)", columnas_cat)

    # Columnas numéricas para eje Y
    columnas_num = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    columnas_y = st.sidebar.multiselect("Columnas para eje Y", columnas_num, default=columnas_num[:1])

    if columna_x and columnas_y:
        st.subheader(f"📊 Gráfico: {tipo_grafico} - {', '.join(columnas_y)} por {columna_x}")

        df_grouped = df.groupby(columna_x)[columnas_y].mean().reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))

        if tipo_grafico == "📈 Líneas":
            for col in columnas_y:
                ax.plot(df_grouped[columna_x], df_grouped[col], marker='o', label=col)
        else:
            ancho = 0.8 / len(columnas_y)  # para que no se solapen
            for i, col in enumerate(columnas_y):
                ax.bar(
                    x=[x + ancho * i for x in range(len(df_grouped))],
                    height=df_grouped[col],
                    width=ancho,
                    label=col,
                    align='edge'
                )
            ax.set_xticks([x + ancho * (len(columnas_y)/2) for x in range(len(df_grouped))])
            ax.set_xticklabels(df_grouped[columna_x])

        ax.set_xlabel(columna_x.capitalize())
        ax.set_ylabel("Valor")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Selecciona una columna para el eje X y al menos una columna numérica para el eje Y.")
