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

    st.write("Columnas detectadas (tras limpieza):", df.columns.tolist())

    required_columns = ["sprint", "estado", "summary", "story points", "label"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Faltan las siguientes columnas necesarias: {missing_columns}")
    else:
        df["story points"] = pd.to_numeric(df["story points"], errors="coerce")
        df.dropna(subset=["story points"], inplace=True)
        df["estado"] = df["estado"].astype(str).str.strip().str.lower()
        df["label"] = df["label"].apply(lambda x: str(x).strip() if pd.notnull(x) else x)

        # 🧠 Agregar columna numérica para orden correcto
        df["sprint_num"] = df["sprint"].astype(str).str.extract(r"(\d+)").astype(int)
        df = df.sort_values("sprint_num")

        # Filtros
        sprints = st.multiselect("Filtrar por Sprint", sorted(df["sprint"].dropna().unique(), key=lambda x: int(str(x).split()[-1])))
        estados = st.multiselect("Filtrar por Estado", sorted(df["estado"].dropna().unique()))

        df_filtrado = df.copy()
        if sprints:
            df_filtrado = df_filtrado[df_filtrado["sprint"].isin(sprints)]
        if estados:
            df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados)]

        # Estado finalizado
        estados_finalizados = ["ready to deploy", "done", "resolved", "ready"]

        col1, col2 = st.columns(2)

        # ========== Gráfico 1 ========== (Tareas y SP por sprint ordenados)
        with col1:
            st.subheader("📊 Tareas y SP finalizados por Sprint")
            finalizado_df = df_filtrado[df_filtrado["estado"].isin(estados_finalizados)]
            finalizado_df = finalizado_df.sort_values("sprint_num")

            tareas = finalizado_df.groupby("sprint")["summary"].count()
            sps = finalizado_df.groupby("sprint")["story points"].sum()

            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(tareas.index, tareas.values, marker='o', label='Tareas Finalizadas', color='tab:blue')
            ax.plot(sps.index, sps.values, marker='s', label='Story Points Finalizados', color='tab:green')

            for x, y in zip(tareas.index, tareas.values):
                ax.text(x, y, f'{int(y)}', fontsize=8, ha='center', va='bottom')
            for x, y in zip(sps.index, sps.values):
                ax.text(x, y, f'{int(y)}', fontsize=8, ha='center', va='bottom')

            ax.set_ylabel("Cantidad")
            ax.set_xlabel("Sprint")
            ax.set_title("Tareas y SP Finalizados")
            ax.legend(fontsize=8)
            ax.grid(True)
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

        # ========== Gráfico 2 ========== (Distribución de Labels)
        with col2:
            st.subheader("📦 Distribución de Labels (%)")
            labels_unicos = df_filtrado["label"].dropna().unique()
            df_label = df_filtrado[df_filtrado["label"].isin(labels_unicos)].sort_values("sprint_num")
            if not df_label.empty:
                pivot_label = pd.crosstab(df_label["sprint"], df_label["label"], normalize="index") * 100
                fig2, ax2 = plt.subplots(figsize=(5, 4))
                pivot_label.plot(kind="bar", stacked=True, ax=ax2, colormap="Pastel1", legend=False)

                for container in ax2.containers:
                    ax2.bar_label(container, fmt='%.1f%%', fontsize=7, label_type='center')

                ax2.set_ylabel("% de Tareas", fontsize=9)
                ax2.set_title("Labels por Sprint", fontsize=10)
                ax2.tick_params(axis='x', rotation=45)
                ax2.legend(title="Label", bbox_to_anchor=(1,1), fontsize=7)
                st.pyplot(fig2)
            else:
                st.info("No hay labels en los datos filtrados.")

        # ========== Gráfico 3 ========== (Estados agrupados)
        with col3:
            st.subheader("🪧 Estados agrupados (%)")
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
            df_estado = df_estado.sort_values("sprint_num")

            pivot_estado = pd.crosstab(df_estado["sprint"], df_estado["estado_mapeado"], normalize="index") * 100
            fig3, ax3 = plt.subplots(figsize=(5, 4))
            pivot_estado.plot(kind="bar", stacked=True, ax=ax3, colormap="Set3", legend=False)

            for container in ax3.containers:
                ax3.bar_label(container, fmt='%.1f%%', fontsize=7, label_type='center')

            ax3.set_ylabel("% de Tareas", fontsize=9)
            ax3.set_title("Estados agrupados por Sprint", fontsize=10)
            ax3.tick_params(axis='x', rotation=45)
            ax3.legend(title="Estado", bbox_to_anchor=(1,1), fontsize=7)
            st.pyplot(fig3)

        # ========== Gráfico 4 ========== (Started vs Done)
        with col4:
            st.subheader("🏁 Started vs Done")
            started_df = df_filtrado[df_filtrado["estado"] != "to do"]
            done_df = df_filtrado[df_filtrado["estado"].isin(estados_finalizados)]

            started_df = started_df.sort_values("sprint_num")
            done_df = done_df.sort_values("sprint_num")

            started_count = started_df.groupby("sprint")["summary"].count()
            done_count = done_df.groupby("sprint")["summary"].count()

            combined = pd.DataFrame({
                "Started": started_count,
                "Done": done_count
            }).fillna(0)

            combined = combined.loc[sorted(combined.index, key=lambda x: int(str(x).split()[-1]))]

            fig4, ax4 = plt.subplots(figsize=(5, 4))
            combined.plot(kind="bar", ax=ax4, width=0.7, color=["#1f77b4", "#2ca02c"], legend=False)

            for container in ax4.containers:
                ax4.bar_label(container, fmt='%d', fontsize=7, label_type='center')

            ax4.set_ylabel("Cantidad de Items", fontsize=9)
            ax4.set_title("Started vs Done por Sprint", fontsize=10)
            ax4.tick_params(axis='x', rotation=45)
            ax4.legend(title="Estado", bbox_to_anchor=(1,1), fontsize=7)
            st.pyplot(fig4)
