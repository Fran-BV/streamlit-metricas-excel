import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Métricas Dinámicas", layout="wide")

st.title("📊 Tu Copiloto de Métricas en Excel")
st.write("Sube un archivo Excel y genera gráficos automáticamente con prompts en lenguaje natural.")

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [col.strip() for col in df.columns]
    
    st.success("✅ Archivo cargado correctamente")
    st.write("Vista previa de los primeros registros:")
    st.dataframe(df.head())

    prompt = st.text_input("🧠 ¿Qué gráfico necesitas?", placeholder="Ej: Gráfico de tiempo promedio en progreso por Sprint")

    if prompt:
        # Lógica simple (temporal): si en el prompt aparece "sprint" y "tiempo", hacemos gráfico básico
        if "sprint" in prompt.lower() and "tiempo" in prompt.lower():
            if "Sprint" in df.columns and "Time in Progress" in df.columns:
                df_viz = df[['Sprint', 'Time in Progress']].dropna()
                df_viz_grouped = df_viz.groupby('Sprint', as_index=False).mean()

                chart = alt.Chart(df_viz_grouped).mark_bar().encode(
                    x='Sprint:N',
                    y='Time in Progress:Q',
                    tooltip=['Sprint', 'Time in Progress']
                ).properties(
                    width=700,
                    height=400,
                    title='Tiempo promedio en progreso por Sprint'
                )
                st.altair_chart(chart)
            else:
                st.error("No se encontraron columnas llamadas 'Sprint' y 'Time in Progress'.")
        else:
            st.info("Esta versión MVP solo soporta el gráfico de tiempo por Sprint por ahora. Pronto se conectará con GPT para interpretar prompts más libres.")
