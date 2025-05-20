import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Suma de SP e Ítems por Sprint")

# Cargar archivo
archivo = st.file_uploader("Carga tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    # Leer Excel y limpiar nombres de columnas
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.lower()  # Quitar espacios, pasar a minúsculas

    # Mostrar columnas detectadas
    st.write("Columnas detectadas:", df.columns.tolist())

    # Renombrar columnas si es necesario
    df = df.rename(columns={
        'summary': 'summary',
        'sp': 'sp',
        'sprint': 'sprint'
    })

    # Verificar columnas requeridas
    requeridas = ['sprint', 'sp', 'summary']
    faltantes = [col for col in requeridas if col not in df.columns]
    if faltantes:
        st.error(f"❌ Faltan columnas requeridas: {faltantes}")
        st.stop()

    # Mostrar DataFrame
    st.subheader("Vista previa de los datos")
    st.dataframe(df)

    # Agrupar datos por Sprint
    df_grouped = df.groupby('sprint').agg({
        'sp': 'sum',
        'summary': 'count'
    }).reset_index()
    df_grouped = df_grouped.rename(columns={'sp': 'Total SP', 'summary': 'Cantidad de ítems'})

    # Mostrar agrupación
    st.subheader("Resumen por Sprint")
    st.dataframe(df_grouped)

    # Limitar a los últimos 5 sprints
    ultimos_sprints = df_grouped.tail(5)

    # Mostrar gráfico
    st.subheader("📈 Gráfico: SP e ítems por Sprint")
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax2 = ax1.twinx()
    ax1.bar(ultimos_sprints['sprint'], ultimos_sprints['Total SP'], color='skyblue', label='Total SP')
    ax2.plot(ultimos_sprints['sprint'], ultimos_sprints['Cantidad de ítems'], color='orange', marker='o', label='Ítems')

    ax1.set_xlabel("Sprint")
    ax1.set_ylabel("Total SP", color='skyblue')
    ax2.set_ylabel("Cantidad de Ítems", color='orange')
    fig.tight_layout()
    st.pyplot(fig)
