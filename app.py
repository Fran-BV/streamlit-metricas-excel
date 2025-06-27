import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Métricas de Excel")

uploaded_file = st.file_uploader("Sube un archivo Excel", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Limpiamos nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    st.write("Columnas detectadas:", df.columns.tolist())

    # Verificamos columnas necesarias
    required_columns = ["sprint", "estado", "summary", "story points", "label"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"El archivo no contiene las siguientes columnas necesarias: {missing_columns}")
    else:
        # Filtros generales
        sprints = st.multiselect(
            "Filtrar por Sprint (Gráfico 1 y 2)",
            df["sprint"].dropna().unique()
        )
        estados = st.multiselect(
            "Filtrar por Estado (Gráfico 1 y 2)",
            df["estado"].dropna().unique()
        )

        df_filtrado = df.copy()
        if sprints:
            df_filtrado = df_filtrado[df_filtrado["sprint"].isin(sprints)]
        if estados:
            df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados)]

        # Gráfico 1: Conteo de items por sprint
        st.subheader("Gráfico 1: Conteo de items por Sprint")
        fig1, ax1 = plt.subplots()
        df_filtrado.groupby("sprint")["summary"].count().plot(kind="bar", ax=ax1)
        ax1.set_ylabel("Cantidad de items")
        st.pyplot(fig1)

        # Gráfico 2: Sumatoria de story points por sprint
        st.subheader("Gráfico 2: Sumatoria de Story Points por Sprint")
        fig2, ax2 = plt.subplots()
        df_filtrado.groupby("sprint")["story points"].sum().plot(kind="bar", color="green", ax=ax2)
        ax2.set_ylabel("Story Points")
        st.pyplot(fig2)

        # Gráfico 3: Boxplot por label
        st.subheader("Gráfico 3: Boxplot de Story Points por Label")
        labels = st.multiselect(
            "Filtrar por Label (Gráfico 3)",
            df["label"].dropna().unique()
        )
        df_box = df.copy()
        if labels:
            df_box = df_box[df_box["label"].isin(labels)]
        if not df_box.empty:
            fig3, ax3 = plt.subplots()
            df_box.boxplot(column="story points", by="label", ax=ax3, rot=45)
            plt.suptitle("")
            ax3.set_title("Distribución de Story Points por Label")
            st.pyplot(fig3)
        else:
            st.info("No hay datos para mostrar en el boxplot con los filtros seleccionados.")
