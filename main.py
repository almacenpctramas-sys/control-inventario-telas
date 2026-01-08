import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")
st.title("📊 Control de Inventario Almacenes 18 y 19")

# --- CONFIGURACIÓN ---
url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

# PEGA AQUÍ EL ENLACE QUE COPIASTE DE "OPCIONES PUBLICADAS"
url_form = "TU_LINK_AQUI" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Intentamos leer el archivo completo primero
    df_raw = conn.read(spreadsheet=url_sheet, ttl=0)
    
    # Limpiamos filas y columnas vacías automáticamente
    df = df_raw.dropna(how='all').dropna(axis=1, how='all')
    
    # Buscamos la fila que contiene los títulos reales (CODIGO, DESCRIPCION)
    # Si tus datos empiezan en la fila 3, esto lo detectará solo.
    df.columns = df.iloc[0] # Tomamos la primera fila con datos como encabezado
    df = df[1:].reset_index(drop=True) # Quitamos esa fila de los datos
    
    # Estandarizamos nombres de columnas para evitar errores de tildes o espacios
    df.columns = [str(c).strip().upper() for c in df.columns]

    st.subheader("🔍 Localizar Tela")
    bus = st.text_input("Ingresa Código o Descripción:").upper()

    if bus:
        # Verificamos que las columnas existan antes de buscar
        if 'CODIGO' in df.columns and 'DESCRIPCION' in df.columns:
            mask = df['CODIGO'].astype(str).str.upper().str.contains(bus) | \
                   df['DESCRIPCION'].astype(str).str.upper().str.contains(bus)
            res = df[mask]
            
            if not res.empty:
                st.success(f"✅ Se encontraron {len(res)} artículos")
                # Mostramos solo las columnas importantes
                cols_mostrar = [c for c in ['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19'] if c in df.columns]
                st.dataframe(res[cols_mostrar])
                
                st.info("Para registrar un ingreso, usa el botón de abajo:")
                st.link_button("📝 REGISTRAR EN GOOGLE FORMS", url_form)
            else:
                st.warning("No se encontró ninguna tela.")
        else:
            st.error("No se encontraron las columnas 'CODIGO' o 'DESCRIPCION'. Revisa tu Excel.")

    st.divider()
    st.subheader("📋 Inventario Completo")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Error al conectar con la base de datos.")
    st.write(f"Detalle técnico: {e}")
