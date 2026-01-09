import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página profesional
st.set_page_config(page_title="Inventario PC7", layout="wide", initial_sidebar_state="collapsed")

st.markdown("# 📊 Sistema de Control de Inventario PC7")
st.info("Consulta de stock en tiempo real y registro de ingresos.")

# URL de tu base de datos
url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"
url_form = "TU_LINK_DEL_FORMULARIO" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leemos la hoja (sin encabezados iniciales para encontrarlos manualmente)
    df_raw = conn.read(spreadsheet=url_sheet, ttl=0, header=None)
    
    # --- BUSCADOR DE ENCABEZADOS DINÁMICO ---
    header_idx = None
    # Buscamos en las primeras 10 filas para encontrar "Codigo"
    for i in range(min(len(df_raw), 10)):
        fila = [str(x).strip().lower() for x in df_raw.iloc[i].values]
        if 'codigo' in fila:
            header_idx = i
            break
            
    if header_idx is not None:
        # Definimos los nombres de las columnas basados en esa fila 3
        df = df_raw.iloc[header_idx + 1:].copy()
        df.columns = [str(c).strip() for c in df_raw.iloc[header_idx]]
        df = df.reset_index(drop=True)

        # Buscador visual
        busqueda = st.text_input("🔍 Buscar por Código o Descripción:").strip()
        
        if busqueda:
            # Filtro flexible: busca en cualquier parte de la fila
            mask = df.apply(lambda row: busqueda.lower() in row.astype(str).str.lower().values, axis=1)
            resultado = df[mask]
            
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} artículos.")
                # Mostramos la tabla con tus columnas exactas
                columnas_a_mostrar = ['Codigo', 'Descripcion', 'Almacen 18', 'Almacen 19']
                # Solo mostramos columnas que existan realmente en el archivo
                cols_validas = [c for c in columnas_a_mostrar if c in df.columns]
                st.table(resultado[cols_validas])
                
                st.markdown(f"""
                <a href="{url_form}" target="_blank">
                    <button style="background-color: #6c63ff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                        📝 Registrar Movimiento
                    </button>
                </a>
                """, unsafe_allow_html=True)
            else:
                st.warning("No se encontraron coincidencias.")
        
        st.divider()
        with st.expander("Ver Inventario Completo"):
            st.dataframe(df, use_container_width=True)
            
    else:
        st.error("No se encontró la fila de encabezados. Asegúrate de que la celda diga 'Codigo'.")

except Exception as e:
    st.error(f"Error de conexión o datos: {str(e)}")
