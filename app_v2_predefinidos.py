import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Métricas Dinámicas", layout="wide")
st.title("📊 Tu Copiloto de Métricas en Excel")
st.write("Sube un archivo Excel y genera métricas automáticamente.")

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [col.strip() for col in df.columns]

    st.success("✅ Archivo cargado correctamente")
    st.write("Vista previa de los primeros registros:")
    st.dataframe(df.head())

    # GRÁFICOS PREDEFINIDOS

    st.markdown("## 📈 Gráficos Predefinidos")

    # 1. Tiempo promedio en progreso por Sprint
    if 'Sprint' in df.columns and 'Time in Progress' in df.columns:
        df_grouped = df[['Sprint', 'Time in Progress']].dropna().groupby('Sprint', as_index=False).mean()
        st.subheader("⏱️ Tiempo promedio en progreso por Sprint")
        chart = alt.Chart(df_grouped).mark_bar().encode(
            x='Sprint:N',
            y='Time in Progress:Q',
            tooltip=['Sprint', 'Time in Progress']
        ).properties(width=700, height=400)
        st.altair_chart(chart)

    # 2. Número de issues por Estado
    if 'Status' in df.columns:
        df_status = df['Status'].value_counts().reset_index()
        df_status.columns = ['Status', 'Cantidad']
        st.subheader("📌 Número de issues por Estado")
        chart2 = alt.Chart(df_status).mark_bar().encode(
            x='Status:N',
            y='Cantidad:Q',
            tooltip=['Status', 'Cantidad']
        ).properties(width=700, height=400)
        st.altair_chart(chart2)

    # 3. Número de issues por Asignado
    if 'Assignee' in df.columns:
        df_assignee = df['Assignee'].value_counts().reset_index()
        df_assignee.columns = ['Assignee', 'Cantidad']
        st.subheader("👤 Número de issues por Asignado")
        chart3 = alt.Chart(df_assignee).mark_bar().encode(
            x='Assignee:N',
            y='Cantidad:Q',
            tooltip=['Assignee', 'Cantidad']
        ).properties(width=700, height=400)
        st.altair_chart(chart3)

    # 4. Promedio de días por Tipo de Issue
    if 'Issue Type' in df.columns and 'Time in Progress' in df.columns:
        df_type = df[['Issue Type', 'Time in Progress']].dropna().groupby('Issue Type', as_index=False).mean()
        st.subheader("📎 Tiempo promedio por Tipo de Issue")
        chart4 = alt.Chart(df_type).mark_bar().encode(
            x='Issue Type:N',
            y='Time in Progress:Q',
            tooltip=['Issue Type', 'Time in Progress']
        ).properties(width=700, height=400)
        st.altair_chart(chart4)

    # 5. Distribución por Prioridad
    if 'Priority' in df.columns:
        df_priority = df['Priority'].value_counts().reset_index()
        df_priority.columns = ['Prioridad', 'Cantidad']
        st.subheader("⚠️ Distribución por Prioridad")
        chart5 = alt.Chart(df_priority).mark_bar().encode(
            x='Prioridad:N',
            y='Cantidad:Q',
            tooltip=['Prioridad', 'Cantidad']
        ).properties(width=700, height=400)
        st.altair_chart(chart5)