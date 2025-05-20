import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visualizador de Excel", layout="wide")

st.title("📊 Visualizador de métricas desde Excel")

# Cargar archivo Excel
uploaded_file = st.file_uploader("Sube un archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Archivo cargado correctamente ✅")

        st.subheader("Vista previa de los datos")
        st.dataframe(df, use_container_width=True)

        # Selección de columnas para gráficas
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()

        if numeric_columns:
            st.subheader("Generar gráfico")

            col1 = st.selectbox("Selecciona columna para eje X", df.columns, key="x")
            col2 = st.selectbox("Selecciona columna para eje Y", numeric_columns, key="y")

            chart_type = st.radio("Tipo de gráfico", ["Línea", "Barras", "Pastel"])

            fig, ax = plt.subplots()

            if chart_type == "Línea":
                ax.plot(df[col1], df[col2])
                ax.set_xlabel(col1)
                ax.set_ylabel(col2)
                ax.set_title(f"{col2} vs {col1}")

            elif chart_type == "Barras":
                ax.bar(df[col1], df[col2])
                ax.set_xlabel(col1)
                ax.set_ylabel(col2)
                ax.set_title(f"{col2} por {col1}")
                plt.xticks(rotation=45)

            elif chart_type == "Pastel":
                if len(df[col2].unique()) <= 10:
                    ax.pie(df[col2].value_counts(), labels=df[col2].value_counts().index, autopct="%1.1f%%")
                    ax.set_title(f"Distribución de {col2}")
                else:
                    st.warning("Demasiados valores únicos para gráfico de pastel.")

            st.pyplot(fig)

        else:
            st.warning("No se encontraron columnas numéricas en el archivo.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
