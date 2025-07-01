import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📈 Métricas de Excel")
st.caption("🔄 Código actualizado el 30/06/2025")

uploaded_file = st.file_uploader("Sube un archivo Excel", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Limpieza y normalización
    df.columns = df.columns.str.strip().str.lower()
    rename_dict = {
        "status": "estado",
        "story point": "story points",
        "storypoint": "story points",
        "sp": "story points"
    }
    df.rename(columns=rename_dict, inplace=True)

    st.write("📌 **Columnas detectadas (tras limpieza):**", df.columns.tolist())

    required_columns = ["sprint", "estado", "summary", "story points", "label"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"⚠️ Faltan las siguientes columnas necesarias: {missing_columns}")
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

        st.caption(f"📂 Filtros aplicados → Sprint: {sprints if sprints else 'Todos'}, Estado: {estados if estados else 'Todos'}")

        if df_filtrado.empty:
            st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados.")
        else:
            st.download_button(
                "⬇️ Descargar datos filtrados",
                df_filtrado.to_csv(index=False).encode("utf-8"),
                "datos_filtrados.csv",
                "text/csv"
            )

            # ===== Gráficos =====
            col1, col2 = st.columns(2)

            # Gráfico 1
            with col1:
                st.markdown("### 📊 Cantidad de Tareas y Story Points")
                fig, ax = plt.subplots(figsize=(6, 3))

                tareas_por_sprint = df_filtrado.groupby("sprint")["summary"].count().sort_index()
                sp_por_sprint = df_filtrado.groupby("sprint")["story points"].sum().sort_index()

                ax.plot(tareas_por_sprint.index, tareas_por_sprint.values, marker='o', label='Tareas', color='tab:blue')
                ax.plot(sp_por_sprint.index, sp_por_sprint.values, marker='s', label='Story Points', color='tab:green')

                ax.set_ylabel("Cantidad", fontsize=8)
                ax.set_xlabel("Sprint", fontsize=8)
                ax.set_title("Tareas y Story Points por Sprint", fontsize=10)
                ax.legend(fontsize=6)
                ax.grid(True, linestyle="--", alpha=0.5)
                ax.tick_params(axis='x', rotation=45, labelsize=7)
                ax.tick_params(axis='y', labelsize=7)

                st.pyplot(fig)
                st.dataframe(pd.DataFrame({"Tareas": tareas_por_sprint, "Story Points": sp_por_sprint}))

            # Gráfico 2
            with col2:
                st.markdown("### 📦 % Labels por Sprint")
                df_label = df_filtrado[df_filtrado["label"].isin(["BAU", "Roadmap", "Tech_tasks"])]
                if not df_label.empty:
                    pivot_label = pd.crosstab(df_label["sprint"], df_label["label"], normalize="index") * 100
                    fig2, ax2 = plt.subplots(figsize=(6, 3))
                    pivot_label.plot(kind="bar", stacked=True, ax=ax2, colormap="Pastel1")

                    ax2.set_ylabel("%", fontsize=8)
                    ax2.set_title("% Labels (BAU, Roadmap, Tech_tasks)", fontsize=10)
                    ax2.tick_params(axis='x', rotation=45, labelsize=7)
                    ax2.tick_params(axis='y', labelsize=7)
                    ax2.legend(fontsize=6)

                    st.pyplot(fig2)
                    st.dataframe(pivot_label.round(2))
                else:
                    st.info("ℹ️ No se encontraron Labels BAU, Roadmap o Tech_tasks en los datos filtrados.")

            col3, col4 = st.columns(2)

            # Gráfico 3
            with col3:
                st.markdown("### 🪧 Estados agrupados por Sprint")
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
                fig3, ax3 = plt.subplots(figsize=(6, 3))
                pivot_estado.plot(kind="bar", stacked=True, ax=ax3, colormap="Set3")

                ax3.set_ylabel("%", fontsize=8)
                ax3.set_title("Estados agrupados", fontsize=10)
                ax3.tick_params(axis='x', rotation=45, labelsize=7)
                ax3.tick_params(axis='y', labelsize=7)
                ax3.legend(fontsize=6)

                st.pyplot(fig3)
                st.dataframe(pivot_estado.round(2))

            # Gráfico 4
            with col4:
                st.markdown("### 🏁 Started vs Done por Sprint")

                started_df = df_filtrado[df_filtrado["estado"] != "to do"]
                done_df = df_filtrado[df_filtrado["estado"].isin(["ready to deploy", "done", "resolved", "ready"])]

                started_count = started_df.groupby("sprint")["summary"].count()
                done_count = done_df.groupby("sprint")["summary"].count()

                combined = pd.DataFrame({
                    "Started": started_count,
                    "Done": done_count
                }).fillna(0).sort_index()

                fig4, ax4 = plt.subplots(figsize=(6, 3))
                combined.plot(kind="bar", ax=ax4, width=0.7, color=["#1f77b4", "#2ca02c"])

                ax4.set_ylabel("Cantidad", fontsize=8)
                ax4.set_title("Started vs Done", fontsize=10)
                ax4.tick_params(axis='x', rotation=45, labelsize=7)
                ax4.tick_params(axis='y', labelsize=7)
                ax4.legend(fontsize=6)

                st.pyplot(fig4)
                st.dataframe(combined.astype(int))
