import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")
st.title("📊 Control de Inventario Almacenes 18 y 19")

# --- CONFIGURACIÓN ---
url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

# PEGA AQUÍ EL ENLACE DE TU FORMULARIO (el que copiaste de "Opciones publicadas")
url_form = "TU_LINK_AQUI" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leemos la hoja sin saltar filas para analizarla
    df_raw = conn.read(spreadsheet=url_sheet, ttl=0)
    
    if df_raw.empty:
        st.error("La hoja de cálculo parece estar vacía.")
    else:
        # --- BUSCADOR INTELIGENTE DE ENCABEZADOS ---
        # Buscamos la fila que contiene la palabra 'CODIGO'
        header_row = None
        for i in range(len(df_raw)):
            if 'CODIGO' in [str(x).upper().strip() for x in df_raw.iloc[i].values]:
                header_row = i
                break
        
        if header_row is not None:
            # Reconfiguramos el dataframe desde esa fila
            df = df_raw.iloc[header_row:].copy()
            df.columns = [str(c).strip().upper() for c in df.iloc[0]]
            df = df[1:].reset_index(drop=True)
            # Limpiamos columnas vacías
            df = df.loc[:, df.columns.notna()]
            
            st.subheader("🔍 Localizar Tela")
            bus = st.text_input("Ingresa Código o Descripción:").upper()

            if bus:
                # Búsqueda flexible
                mask = df['CODIGO'].astype(str).str.upper().str.contains(bus) | \
                       df['DESCRIPCION'].astype(str).str.upper().str.contains(bus)
                res = df[mask]
                
                if not res.empty:
                    st.success(f"✅ Se encontraron {len(res)} artículos")
                    st.dataframe(res[['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19']])
                    
                    st.info("Para registrar, usa el formulario:")
                    st.link_button("📝 REGISTRAR EN GOOGLE FORMS", url_form)
                else:
                    st.warning("No se encontró el artículo.")

            st.divider()
            st.subheader("📋 Vista de Inventario")
            st.dataframe(df, use_container_width=True)
        else:
            st.error("No se encontró la columna 'CODIGO'. Revisa que tus títulos estén en la hoja.")
            st.write("Datos leídos actualmente:", df_raw.head())

except Exception as e:
    st.error("Error crítico de conexión.")
    st.write(f"Detalle: {e}")
