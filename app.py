import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Métricas de Excel")

uploaded_file = st.file_uploader("Sube un archivo Excel", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Limpieza y estandarización de nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    # Mapeo de nombres comunes de columnas a estándar esperado
    rename_dict = {
        "status": "estado",
        "story point": "story points",
        "storypoint": "story points",
        "sp": "story points",  # Agregado para tu caso
    }
    df.rename(columns=rename_dict, inplace=True)

    st.write("Columnas detectadas (tras limpieza):", df.columns.tolist())

    # Validación de columnas necesarias
    required_columns = ["sprint", "estado", "summary", "story points", "label"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"El archivo no contiene las siguientes columnas necesarias: {missing_columns}")
    else:
        # Limpieza de datos
        df["story points"] = pd.to_numeric(df["story points"], errors="coerce")
        df.dropna(subset=["story points"], inplace=True)
        df["estado"] = df["estado"].str.lower().str.strip()

        # Filtros interactivos
        sprints = st.multiselect("Filtrar por Sprint", sorted(df["sprint"].dropna().unique()))
        estados = st.multiselect("Filtrar por Estado", sorted(df["estado"].dropna().unique()))

        df_filtrado = df.copy()
        if sprints:
            df_filtrado = df_filtrado[df_filtrado["sprint"].isin(sprints)]
        if estados:
            df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados)]

        # Gráfico 1: Conteo de Items por Sprint
        st.subheader("Gráfico 1: Conteo de Items por Sprint")
        fig1, ax1 = plt.subplots()
        conteo = df_filtrado.groupby("sprint")["summary"].count().sort_index()
        bars = ax1.bar(conteo.index, conteo.values, color="skyblue")
        ax1.set_ylabel("Cantidad de Items")
        ax1.set_title("Cantidad de Items por Sprint")
        ax1.bar_label(bars)
        st.pyplot(fig1)

        # Gráfico 2: Story Points por Sprint
        st.subheader("Gráfico 2: Sumatoria de Story Points por Sprint")
        fig2, ax2 = plt.subplots()
        suma_sp = df_filtrado.groupby("sprint")["story points"].sum().sort_index()
        bars2 = ax2.bar(suma_sp.index, suma_sp.values, color="green")
        ax2.set_ylabel("Story Points")
        ax2.set_title("Story Points por Sprint")
        ax2.bar_label(bars2)
        st.pyplot(fig2)

        # Gráfico 3: Boxplot por Label
        st.subheader("Gráfico 3: Boxplot de Story Points por Label")
        labels = st.multiselect("Filtrar por Label", sorted(df["label"].dropna().unique()))
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

        # Gráfico 4: Porcentaje de tareas por Estado por Sprint
        st.subheader("Gráfico 4: % de Tareas por Estado por Sprint")
        pivot_estado = pd.crosstab(df_filtrado["sprint"], df_filtrado["estado"], normalize="index") * 100
        fig4, ax4 = plt.subplots()
        pivot_estado.plot(kind="bar", stacked=True, ax=ax4, colormap="tab20")
        ax4.set_ylabel("% de Tareas")
        ax4.set_title("Distribución Porcentual de Estados por Sprint")
        st.pyplot(fig4)

        # Gráfico 5: Started vs Done por Sprint
        st.subheader("Gráfico 5: Started vs Done por Sprint")

        started_statuses = [
            "in progress", "code review", "ready to deploy", "waiting 3rd party", "resolved", "done"
        ]
        done_statuses = ["ready to deploy", "resolved", "done"]

        started_df = df[df["estado"].isin(started_statuses)]
        done_df = df[df["estado"].isin(done_statuses)]

        started_count = started_df.groupby("sprint")["summary"].count()
        done_count = done_df.groupby("sprint")["summary"].count()

        combined = pd.DataFrame({
            "Started": started_count,
            "Done": done_count
        }).fillna(0).sort_index()

        fig5, ax5 = plt.subplots()
        combined.plot(kind="bar", ax=ax5)
        ax5.set_ylabel("Cantidad de Items")
        ax5.set_title("Comparativa Started vs Done por Sprint")
        ax5.legend(["Started", "Done"])
        st.pyplot(fig5)
