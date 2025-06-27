import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.set_page_config(page_title="Dashboard Ágil", layout="wide")

st.title("📊 Dashboard Ágil - Métricas de Sprints")

# Subida del archivo
archivo = st.file_uploader("Sube un archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    st.success("Archivo cargado correctamente.")

    columnas_disponibles = df.columns.tolist()

    def aplicar_filtros(df, filtros):
        for col, vals in filtros.items():
            if vals:
                df = df[df[col].isin(vals)]
        return df

    # GRAFICO 1
    st.header("Gráfico 1")
    with st.expander("🎛️ Configuración Gráfico 1"):
        filtros_1 = {
            "sprint": st.multiselect("Filtrar por Sprint (Gráfico 1)", df["sprint"].unique()),
            "status": st.multiselect("Filtrar por Status (Gráfico 1)", df["status"].unique()),
            "assignee": st.multiselect("Filtrar por Assignee (Gráfico 1)", df["assignee"].unique()),
        }
        tipo_1 = st.selectbox("Tipo de gráfico (Gráfico 1)", ["Barras", "Líneas", "Boxplot"], key="tipo1")
        x_1 = st.selectbox("Eje X (Gráfico 1)", columnas_disponibles, key="x1")
        y_1 = st.multiselect("Eje Y (Gráfico 1)", columnas_disponibles, key="y1")
    df1 = aplicar_filtros(df, filtros_1)
    
    # GRAFICO 2
    st.header("Gráfico 2")
    with st.expander("🎛️ Configuración Gráfico 2"):
        filtros_2 = {
            "sprint": st.multiselect("Filtrar por Sprint (Gráfico 2)", df["sprint"].unique()),
            "status": st.multiselect("Filtrar por Status (Gráfico 2)", df["status"].unique()),
            "assignee": st.multiselect("Filtrar por Assignee (Gráfico 2)", df["assignee"].unique()),
        }
        tipo_2 = st.selectbox("Tipo de gráfico (Gráfico 2)", ["Barras", "Líneas", "Boxplot"], key="tipo2")
        x_2 = st.selectbox("Eje X (Gráfico 2)", columnas_disponibles, key="x2")
        y_2 = st.multiselect("Eje Y (Gráfico 2)", columnas_disponibles, key="y2")
    df2 = aplicar_filtros(df, filtros_2)

    # GRAFICO 3
    st.header("Gráfico 3")
    with st.expander("🎛️ Configuración Gráfico 3"):
        filtros_3 = {
            "sprint": st.multiselect("Filtrar por Sprint (Gráfico 3)", df["sprint"].unique()),
            "status": st.multiselect("Filtrar por Status (Gráfico 3)", df["status"].unique()),
            "assignee": st.multiselect("Filtrar por Assignee (Gráfico 3)", df["assignee"].unique()),
            "label": st.multiselect("Filtrar por Label (Gráfico 3)", df["label"].unique()) if "label" in df.columns else [],
        }
        tipo_3 = st.selectbox("Tipo de gráfico (Gráfico 3)", ["Barras", "Líneas", "Boxplot"], key="tipo3")
        x_3 = st.selectbox("Eje X (Gráfico 3)", columnas_disponibles, key="x3")
        y_3 = st.multiselect("Eje Y (Gráfico 3)", columnas_disponibles, key="y3")
    df3 = aplicar_filtros(df, filtros_3)

    def plot_grafico(df_filtrado, tipo, x_col, y_cols):
        fig, ax = plt.subplots(figsize=(10,6))
        for y_col in y_cols:
            if pd.api.types.is_numeric_dtype(df_filtrado[y_col]):
                data = df_filtrado.groupby(x_col)[y_col].sum()
            else:
                data = df_filtrado.groupby(x_col)[y_col].count()

            if tipo == "Barras":
                data.plot(kind="bar", ax=ax)
            elif tipo == "Líneas":
                data.plot(kind="line", marker="o", ax=ax)
            elif tipo == "Boxplot":
                sns.boxplot(x=x_col, y=y_col, data=df_filtrado, ax=ax)
        ax.set_title(f"{tipo} - {', '.join(y_cols)} por {x_col}")
        st.pyplot(fig)
        buf = BytesIO()
        fig.savefig(buf, format="pdf")
        st.download_button("📥 Descargar PDF", buf.getvalue(), file_name="grafico.pdf", mime="application/pdf")

    if y_1:
        plot_grafico(df1, tipo_1, x_1, y_1)
    if y_2:
        plot_grafico(df2, tipo_2, x_2, y_2)
    if y_3:
        plot_grafico(df3, tipo_3, x_3, y_3)
