import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(layout="wide")
st.title("📊 Dashboard de Métricas Ágiles")

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
        'sprint': 'sprint',
        'cycle time': 'cycle time'  # Si esta columna está presente
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

    # Sidebar: selección de gráficos
    st.sidebar.header("📌 Selecciona gráficos a mostrar")
    mostrar_grafico_1 = st.sidebar.checkbox("📈 SP e ítems por Sprint", value=True)
    mostrar_grafico_2 = st.sidebar.checkbox("📉 Tiempo promedio por ítem", value=False)
    # Puedes seguir agregando más checkboxes aquí

    # --- Gráfico 1: SP e ítems por Sprint ---
    if mostrar_grafico_1:
        st.subheader("📈 Gráfico: SP e ítems por Sprint")

        df_grouped = df.groupby('sprint').agg({
            'sp': 'sum',
            'summary': 'count'
        }).reset_index()
        df_grouped = df_grouped.rename(columns={'sp': 'Total SP', 'summary': 'Cantidad de ítems'})

        # Limitar a los últimos 5 sprints
        ultimos_sprints = df_grouped.tail(5)

        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax2 = ax1.twinx()

        ax1.bar(ultimos_sprints['sprint'], ultimos_sprints['Total SP'], color='skyblue', label='Total SP')
        ax2.plot(ultimos_sprints['sprint'], ultimos_sprints['Cantidad de ítems'], color='orange', marker='o', label='Ítems')

        ax1.set_xlabel("Sprint")
        ax1.set_ylabel("Total SP", color='skyblue')
        ax2.set_ylabel("Cantidad de Ítems", color='orange')
        fig.tight_layout()
        st.pyplot(fig)

    # --- Gráfico 2: Tiempo promedio por ítem (Cycle Time) ---
    if mostrar_grafico_2:
        if 'cycle time' not in df.columns:
            st.warning("⚠️ La columna 'Cycle TIME' no fue encontrada en el archivo.")
        else:
            st.subheader("📉 Gráfico: Tiempo promedio por ítem (Cycle TIME)")

            df_ct = df.groupby('sprint')['cycle time'].mean().reset_index()
            df_ct = df_ct.tail(5)  # Últimos 5 sprints

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df_ct['sprint'], df_ct['cycle time'], marker='o', color='green')
            ax.set_xlabel("Sprint")
            ax.set_ylabel("Tiempo promedio (Cycle TIME)")
            ax.set_title("Cycle TIME promedio por Sprint")
            st.pyplot(fig)

    # Puedes seguir agregando más bloques `if mostrar_grafico_X:` aquí
