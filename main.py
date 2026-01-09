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
    
    # 1. CAMBIO CLAVE: Leemos la hoja completa. 
    # Si sabes el nombre de la pestaña (ej. "Hoja1"), es mejor poner worksheet="Hoja1"
    df = conn.read(spreadsheet=url_sheet, ttl=0)
    
    # Si por alguna razón df es un diccionario, extraemos la primera tabla
    if isinstance(df, dict):
        first_key = list(df.keys())[0]
        df = df[first_key]

    # --- INTELIGENCIA DE DATOS: Limpieza Inicial ---
    # Eliminamos filas y columnas que estén totalmente vacías
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    
    # 2. BÚSQUEDA DEL ENCABEZADO: Identificar la fila que contiene 'CODIGO'
    header_idx = None
    for i in range(len(df)):
        # Convertimos la fila actual en una lista de strings limpios
        fila_lista = [str(x).upper().strip() for x in df.iloc[i].values]
        if 'CODIGO' in fila_lista:
            header_idx = i
            break
            
    if header_idx is not None:
        # Reasignamos los nombres de las columnas usando la fila encontrada
        nuevas_columnas = [str(c).strip().upper() for c in df.iloc[header_idx]]
        df.columns = nuevas_columnas
        
        # Nos quedamos solo con los datos que están debajo de ese encabezado
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
        
        # Limpieza de columnas "fantasma" (Unnamed)
        df = df.loc[:, ~df.columns.str.contains('^UNNAMED')]

        # Interfaz de búsqueda
        col1, col2 = st.columns([2, 1])
        with col1:
            busqueda = st.text_input("🔍 Buscar por Código o Nombre de Tela:").upper()
        
        if busqueda:
            # 3. FILTRO CORREGIDO: Usamos una función que maneja errores si faltan columnas
            def filtrar_fila(row):
                texto_fila = " ".join(row.astype(str).values).upper()
                return busqueda in texto_fila

            resultado = df[df.apply(filtrar_fila, axis=1)]
            
            if not resultado.empty:
                st.success(f"Se encontraron {len(resultado)} coincidencias.")
                
                # Seleccionamos solo las columnas importantes si existen
                columnas_ver = [c for c in ['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19'] if c in df.columns]
                st.table(resultado[columnas_ver])
                
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
        st.error("No se detectó la columna 'CODIGO'. Asegúrate de que tu Excel tenga una columna llamada exactamente así.")

except Exception as e:
    # Este bloque atrapará el error y nos dirá exactamente qué falla si persiste
    st.error(f"Error de configuración: {str(e)}")
