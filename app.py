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
        st.success("✅ Archivo cargado correctamente.")
        st.subheader("Vista previa de los datos")
        st.dataframe(df.head())

        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        # Detectar columnas clave
        col_sprint = next((col for col in df.columns if "sprint" in col.lower()), None)
        col_status = next((col for col in df.columns if "status" in col.lower() or "estado" in col.lower()), None)
        col_storypoints = next((col for col in df.columns if col.lower() in ["sp", "storypoints", "story points", "puntos"]), None)

        # Mostrar columnas detectadas
        st.markdown("### 🔍 Columnas detectadas:")
        st.write(f"• Sprint: `{col_sprint}`")
        st.write(f"• Estado: `{col_status}`")
        st.write(f"• Story Points: `{col_storypoints}`")

        if not col_storypoints:
            st.warning("No se encontró una columna de Story Points (SP, storypoints, puntos...).")
        else:
            df[col_storypoints] = pd.to_numeric(df[col_storypoints], errors='coerce')
            if df[col_storypoints].dropna().empty:
                st.warning("La columna de Story Points no contiene datos numéricos válidos.")

        # GRÁFICO 1: SP por Sprint
        if col_sprint and col_storypoints and not df[col_storypoints].dropna().empty:
            st.markdown("### 📊 Story Points por Sprint")
            sp_sprint = df.groupby(col_sprint)[col_storypoints].sum()
            fig1, ax1 = plt.subplots()
            sp_sprint.plot(kind="bar", ax=ax1, color="#4CAF50")
            ax1.set_ylabel("Story Points")
            ax1.set_xlabel("Sprint")
            st.pyplot(fig1)
        else:
            st.info("No se puede generar 'SP por Sprint'. Faltan columnas necesarias o datos.")

        # GRÁFICO 2: SP por Estado
        if col_status and col_storypoints and not df[col_storypoints].dropna().empty:
            st.markdown("### 📊 Story Points por Estado")
            sp_estado = df.groupby(col_status)[col_storypoints].sum()
            fig2, ax2 = plt.subplots()
            sp_estado.plot(kind="barh", ax=ax2, color="#2196F3")
            ax2.set_xlabel("Story Points")
            ax2.set_ylabel("Estado")
            st.pyplot(fig2)
        else:
            st.info("No se puede generar 'SP por Estado'. Faltan columnas necesarias o datos.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

else:
    st.info("Por favor, carga un archivo Excel para comenzar.")
