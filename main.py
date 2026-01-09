import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")

st.markdown("# 📊 Sistema de Control de Inventario PC7")
st.info("Consulta de stock y registro de artículos.")

url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 1. Obtenemos todas las pestañas para encontrar la correcta
    all_sheets = conn.read(spreadsheet=url_sheet, ttl=0, worksheet=None)
    
    # Buscamos la pestaña que NO sea la de "Respuestas de formulario"
    nombres_pestañas = list(all_sheets.keys())
    pestaña_datos = nombres_pestañas[0]
    for nombre in nombres_pestañas:
        if "RESPUESTAS" not in nombre.upper() and "FORM" not in nombre.upper():
            pestaña_datos = nombre
            break

    df_raw = all_sheets[pestaña_datos]

    # 2. Localizar la fila 3 (donde dice 'Codigo')
    header_idx = None
    for i in range(len(df_raw)):
        fila = [str(x).strip().lower() for x in df_raw.iloc[i].values]
        if 'codigo' in fila:
            header_idx = i
            break

    if header_idx is not None:
        # Extraemos los datos reales
        df = df_raw.iloc[header_idx + 1:].copy()
        df.columns = [str(c).strip() for c in df_raw.iloc[header_idx]]
        
        # Limpiamos filas vacías y nos quedamos con las columnas de tu Excel
        df = df.dropna(subset=[df.columns[0]], how='all').reset_index(drop=True)
        columnas_visibles = ['Codigo', 'Descripcion', 'Almacen 18', 'Almacen 19']
        df_final = df[[c for c in columnas_visibles if c in df.columns]]

        # Buscador interactivo
        busqueda = st.text_input("🔍 Buscar artículo (Código o Nombre):")
        if busqueda:
            resultado = df_final[df_final.apply(lambda row: busqueda.lower() in row.astype(str).str.lower().values, axis=1)]
            if not resultado.empty:
                st.table(resultado)
            else:
                st.warning("No se encontró el artículo.")
        
        # Mostrar todo el inventario guardado
        st.subheader("📋 Artículos Inventariados")
        st.dataframe(df_final, use_container_width=True)
            
    else:
        st.error(f"No encontré la columna 'Codigo' en la pestaña: {pestaña_datos}")

except Exception as e:
    st.error(f"Error de conexión: {str(e)}")
