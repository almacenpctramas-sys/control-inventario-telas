import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")

st.markdown("# 📊 Sistema de Control de Inventario PC7")
st.info("Consulta de stock y artículos registrados.")

url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 1. Intentamos leer la hoja de "Inventario" directamente
    # Si tu pestaña tiene otro nombre, cámbialo aquí abajo donde dice worksheet="..."
    try:
        df_raw = conn.read(spreadsheet=url_sheet, ttl=0, worksheet="Hoja 1", header=None)
    except:
        # Si falla, lee la primera que encuentre
        df_raw = conn.read(spreadsheet=url_sheet, ttl=0, header=None)

    # 2. Buscador de la fila de títulos (Codigo, Descripcion...)
    header_idx = None
    for i in range(len(df_raw)):
        # Limpiamos la fila de espacios y buscamos la palabra clave
        fila = [str(x).strip().lower() for x in df_raw.iloc[i].values]
        if 'codigo' in fila:
            header_idx = i
            break

    if header_idx is not None:
        # Extraemos encabezados y datos
        df = df_raw.iloc[header_idx + 1:].copy()
        df.columns = [str(c).strip() for c in df_raw.iloc[header_idx]]
        
        # Limpiar filas vacías
        df = df.dropna(subset=[df.columns[0]], how='all').reset_index(drop=True)
        
        # Definimos las columnas que queremos ver (según tu imagen)
        columnas_finales = ['Codigo', 'Descripcion', 'Almacen 18', 'Almacen 19']
        # Filtramos solo las que existan para evitar errores
        df_ver = df[[c for c in columnas_finales if c in df.columns]]

        # Buscador
        busqueda = st.text_input("🔍 Buscar por Código o Descripción:")
        if busqueda:
            res = df_ver[df_ver.apply(lambda row: busqueda.lower() in row.astype(str).str.lower().values, axis=1)]
            if not res.empty:
                st.table(res)
            else:
                st.warning("No se encontró el artículo.")

        st.subheader("📋 Lista de Artículos en Inventario")
        st.dataframe(df_ver, use_container_width=True)
        
    else:
        st.error("⚠️ No se encontró la columna 'Codigo'. Revisa que la pestaña seleccionada sea la correcta.")
        # Muestra una ayuda para saber qué está leyendo el sistema
        with st.expander("Ver qué está leyendo el sistema"):
            st.write(df_raw.head(10))

except Exception as e:
    st.error(f"Error de conexión: {str(e)}")
