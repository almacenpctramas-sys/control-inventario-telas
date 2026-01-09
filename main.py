import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")

st.markdown("# 📊 Sistema de Control de Inventario PC7")
st.info("Consulta de stock en tiempo real y registro de ingresos.")

url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"
url_form = "TU_LINK_DEL_FORMULARIO" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leemos la hoja completa sin procesar encabezados aún
    df_raw = conn.read(spreadsheet=url_sheet, ttl=0, header=None)
    
    # --- BUSCADOR ULTRA-FLEXIBLE DE ENCABEZADOS ---
    header_idx = None
    for i in range(len(df_raw)):
        # Buscamos en cada fila si existe la palabra 'Codigo' o 'Código'
        fila_valores = [str(x).strip().lower() for x in df_raw.iloc[i].values]
        if any('codigo' in x or 'código' in x for x in fila_valores):
            header_idx = i
            break
            
    if header_idx is not None:
        # 1. Configurar los nombres de las columnas
        columnas = [str(c).strip() for c in df_raw.iloc[header_idx]]
        
        # 2. Crear el DataFrame real con los datos debajo del encabezado
        df = df_raw.iloc[header_idx + 1:].copy()
        df.columns = columnas
        df = df.dropna(subset=[df.columns[0]], how='all').reset_index(drop=True)

        # Buscador
        busqueda = st.text_input("🔍 Buscar por Código o Descripción:").strip()
        
        if busqueda:
            # Filtro que busca el texto en cualquier columna de la tabla
            mask = df.apply(lambda row: busqueda.lower() in row.astype(str).str.lower().values, axis=1)
            resultado = df[mask]
            
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} coincidencias.")
                # Mostramos solo las columnas que vimos en tu captura
                cols_visibles = [c for c in ['Codigo', 'Descripcion', 'Almacen 18', 'Almacen 19'] if c in df.columns]
                st.table(resultado[cols_visibles])
                
                st.markdown(f'<a href="{url_form}" target="_blank"><button style="background-color: #6c63ff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">📝 Registrar Movimiento</button></a>', unsafe_allow_html=True)
            else:
                st.warning("No se encontraron resultados.")
        
        st.divider()
        with st.expander("Ver Inventario Completo"):
            st.dataframe(df, use_container_width=True)
            
    else:
        # Si falla, mostramos qué está leyendo para debuggear
        st.error("No se encontró la palabra 'Codigo' en las primeras filas.")
        st.write("Datos detectados actualmente:", df_raw.head(5))

except Exception as e:
    st.error(f"Error crítico: {str(e)}")
