  import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Ágil", layout="wide")

st.title("📊 Dashboard Ágil - MVP")
st.markdown("Sube un archivo Excel con métricas de tus sprints para visualizar insights automáticamente.")

uploaded_file = st.file_uploader("Carga tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Archivo cargado correctamente.")
        st.subheader("Vista previa de los datos")
        st.dataframe(df.head())

        # Intentar detectar columnas útiles
        columnas = df.columns.str.lower()

        # Identificar columnas clave
        col_sprint = next((col for col in df.columns if "sprint" in col.lower()), None)
        col_status = next((col for col in df.columns if "status" in col.lower() or "estado" in col.lower()), None)
        col_storypoints = next((col for col in df.columns if col.lower() in ["sp", "storypoints", "story points", "puntos"]), None)
        col_summary = next((col for col in df.columns if "summary" in col.lower() or "título" in col.lower()), None)

        # Conversión segura a numérico
        df[col_storypoints] = pd.to_numeric(df[col_storypoints], errors='coerce')

        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if not numeric_cols:
            st.warning("No se encontraron columnas numéricas válidas para generar gráficos.")
        else:
            st.subheader("📈 Gráficos automáticos")

            # 1. Story Points por Sprint
            if col_sprint and col_storypoints:
                st.markdown("### Story Points por Sprint")
                sp_por_sprint = df.groupby(col_sprint)[col_storypoints].sum()
                fig1, ax1 = plt.subplots()
                sp_por_sprint.plot(kind="bar", ax=ax1, color="#4CAF50")
                ax1.set_ylabel("Story Points")
                ax1.set_xlabel("Sprint")
                st.pyplot(fig1)
            else:
                st.info("No se encontraron columnas suficientes para mostrar SP por Sprint.")

            # 2. Story Points por Estado
            if col_status and col_storypoints:
                st.markdown("### Story Points por Estado")
                sp_por_estado = df.groupby(col_status)[col_storypoints].sum()
                fig2, ax2 = plt.subplots()
                sp_por_estado.plot(kind="barh", ax=ax2, color="#2196F3")
                ax2.set_xlabel("Story Points")
                ax2.set_ylabel("Estado")
                st.pyplot(fig2)
            else:
                st.info("No se encontraron columnas suficientes para mostrar SP por Estado.")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, carga un archivo Excel para comenzar.")
