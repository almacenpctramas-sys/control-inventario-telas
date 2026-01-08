import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página profesional
st.set_page_config(page_title="Inventario PC7", layout="wide", initial_sidebar_state="collapsed")

st.markdown("# 📊 Sistema de Control de Inventario PC7")
st.info("Consulta de stock en tiempo real y registro de ingresos.")

# URL de tu base de datos
url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"
# Link de tu formulario (asegúrate de que sea el correcto)
url_form = "TU_LINK_DEL_FORMULARIO" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # LEER TODO EL DOCUMENTO (Sin nombres de pestañas para evitar errores)
    # Buscamos la primera pestaña que contenga datos
    data_dict = conn.read(spreadsheet=url_sheet, ttl=0, worksheet=None)
    
    # Seleccionamos la primera pestaña que tenga contenido
    first_sheet_name = list(data_dict.keys())[0]
    df = data_dict[first_sheet_name]
    
    # --- INTELIGENCIA DE DATOS: Limpieza Automática ---
    # Buscamos la fila donde realmente empiezan los títulos (CODIGO)
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    
    # Identificar la fila del encabezado buscando 'CODIGO'
    header_idx = None
    for i in range(len(df)):
        if 'CODIGO' in [str(x).upper().strip() for x in df.iloc[i]]:
            header_idx = i
            break
            
    if header_idx is not None:
        # Reconstruir la tabla correctamente
        df.columns = [str(c).strip().upper() for c in df.iloc[header_idx]]
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
        
        # Interfaz de búsqueda
        col1, col2 = st.columns([2, 1])
        with col1:
            busqueda = st.text_input("🔍 Buscar por Código o Nombre de Tela:").upper()
        
        if busqueda:
            # Filtro inteligente que busca en múltiples columnas a la vez
            resultado = df[df.apply(lambda row: busqueda in row.astype(str).get('CODIGO', '') or 
                                               busqueda in row.astype(str).get('DESCRIPCION', ''), axis=1)]
            
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} coincidencias.")
                st.table(resultado[['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19']])
                
                # Botón de acción directo al formulario
                st.markdown(f"""
                <a href="{url_form}" target="_blank">
                    <button style="background-color: #6c63ff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
                        📝 Registrar Entrada de Mercancía
                    </button>
                </a>
                """, unsafe_allow_html=True)
            else:
                st.warning("No se encontró ningún artículo con ese criterio.")
        
        st.divider()
        with st.expander("Ver Inventario Completo"):
            st.dataframe(df, use_container_width=True)
            
    else:
        st.error("No se pudo detectar la estructura de columnas en tu Excel. Revisa que diga 'CODIGO' en alguna celda.")

except Exception as e:
    st.error(f"Error de conexión: {str(e)}")
