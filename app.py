import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")  # Mejor distribución en pantalla
st.title("Métricas de Excel")
st.info("🔄 Código actualizado el 30/06/2025")

uploaded_file = st.file_uploader("Sube un archivo Excel", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Limpieza y normalización de columnas
    df.columns = df.columns.str.strip().str.lower()
    rename_dict = {
        "status": "estado",
        "story point": "story points",
        "storypoint": "story points",
        "sp": "story points"
    }
    df.rename(columns=rename_dict, inplace=True)

    st.write("Columnas detectadas (tras limpieza):", df.columns.tolist())

    required_columns = ["sprint", "estado", "summary", "story points", "label"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Faltan las siguientes columnas necesarias: {missing_columns}")
    else:
        df["story points"] = pd.to_numeric(df["story points"], errors="coerce")
        df.dropna(subset=["story points"], inplace=True)
        df["estado"] = df["estado"].str.strip().str.lower()
        df["label"] = df["label"].str.strip()

        # Filtros
        sprints = st.multiselect("Filtrar por Sprint", sorted(df["sprint"].dropna().unique()))
        estados = st.multiselect("Filtrar por Estado", sorted(df["estado"].dropna().unique()))

        df_filtrado = df.copy()
        if sprints:
            df_filtrado = df_filtrado[df_filtrado["sprint"].isin(sprints)]
        if estados:
            df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados)]

        # ========== Gráfico 1+2 Combinado ==========
        st.subheader("📊 Cantidad de Tareas y Story Points por Sprint")
        fig, ax1 = plt.subplots(figsize=(10, 5))

        tareas_por_sprint = df_filtrado.groupby("sprint")["summary"].count().sort_index()
        sp_por_sprint = df_filtrado.groupby("sprint")["story points"].sum().sort_index()

        ax2 = ax1.twinx()
        line1 = ax1.plot(tareas_por_sprint.index, tareas_por_sprint.values, color='tab:blue', marker='o', label='Cantidad de Tareas')
        line2 = ax2.plot(sp_por_sprint.index, sp_por_sprint.values, color='tab:green', marker='s', label='Story Points')

        ax1.set_ylabel("Cantidad de Tareas", color='tab:blue')
        ax2.set_ylabel("Story Points", color='tab:green')
        ax1.set_xlabel("Sprint")
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True)

        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')

        st.pyplot(fig)

        # ========== Gráfico 3 (nuevo): % Label por Sprint ==========
        st.subheader("📦 Distribución porcentual de Labels por Sprint (BAU, Roadmap, Tech_tasks)")
        df_label = df_filtrado[df_filtrado["label"].isin(["BAU", "Roadmap", "Tech_tasks"])]
        if not df_label.empty:
            pivot_label = pd.crosstab(df_label["sprint"], df_label["label"], normalize="index") * 100
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            pivot_label.plot(kind="bar", stacked=True, ax=ax3, colormap="Pastel1")
            ax3.set_ylabel("% de Tareas")
            ax3.set_title("Distribución de Labels por Sprint")
            ax3.tick_params(axis='x', rotation=45)
            st.pyplot(fig3)
        else:
            st.info("No se encontraron Labels BAU, Roadmap o Tech_tasks en los datos filtrados.")

        # ========== Gráfico 4: Estados agrupados ==========
        st.subheader("🪧 Distribución de Estados (ToDo, In Progress, Finished) por Sprint")

        estado_mapeado = {
            "to do": "ToDo",
            "in progress": "In Progress",
            "code review": "In Progress",
            "waiting 3rd party": "In Progress",
            "qa": "In Progress",
            "ready to deploy": "Finished",
            "done": "Finished",
            "resolved": "Finished",
            "ready": "Finished"
        }

        df_estado = df_filtrado.copy()
        df_estado["estado_mapeado"] = df_estado["estado"].map(estado_mapeado).fillna("Otros")

        pivot_estado = pd.crosstab(df_estado["sprint"], df_estado["estado_mapeado"], normalize="index") * 100
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        pivot_estado.plot(kind="bar", stacked=True, ax=ax4, colormap="Set3")
        ax4.set_ylabel("% de Tareas")
        ax4.set_title("Estados agrupados por Sprint")
        ax4.tick_params(axis='x', rotation=45)
        st.pyplot(fig4)

        # ========== Gráfico 5: Started vs Done ==========
        st.subheader("🏁 Started vs Done por Sprint")

        started_df = df[df["estado"] != "to do"]
        done_df = df[df["estado"].isin(["ready to deploy", "done", "resolved", "ready"])]

        started_count = started_df.groupby("sprint")["summary"].count()
        done_count = done_df.groupby("sprint")["summary"].count()

        combined = pd.DataFrame({
            "Started": started_count,
            "Done": done_count
        }).fillna(0).sort_index()

        fig5, ax5 = plt.subplots(figsize=(10, 5))
        combined.plot(kind="bar", ax=ax5, width=0.7, color=["#1f77b4", "#2ca02c"])
        ax5.set_ylabel("Cantidad de Items")
        ax5.set_title("Started vs Done por Sprint")
        ax5.legend(loc="upper left")
        ax5.tick_params(axis='x', rotation=45)
        st.pyplot(fig5)
