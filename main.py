import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")
st.title("📊 Control de Inventario Almacenes 18 y 19")

# --- CONFIGURACIÓN ---
url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

# PEGA AQUÍ TU ENLACE DEL FORMULARIO
url_form = "TU_LINK_AQUI" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Intentamos leer la "Hoja 1" específicamente, que es la que tiene tus datos
    try:
        df_raw = conn.read(spreadsheet=url_sheet, worksheet="Hoja 1", ttl=0)
    except:
        # Si falla, leemos la pestaña por defecto
        df_raw = conn.read(spreadsheet=url_sheet, ttl=0)
    
    if df_raw.empty:
        st.error("No se encontraron datos. Revisa que la pestaña con las telas se llame 'Hoja 1'.")
    else:
        # --- BUSCADOR DE TÍTULOS ---
        header_row = None
        for i in range(min(len(df_raw), 10)): # Buscamos en las primeras 10 filas
            fila_texto = [str(x).upper().strip() for x in df_raw.iloc[i].values]
            if 'CODIGO' in fila_texto:
                header_row = i
                break
        
        if header_row is not None:
            df = df_raw.iloc[header_row:].copy()
            df.columns = [str(c).strip().upper() for c in df.iloc[0]]
            df = df[1:].reset_index(drop=True)
            df = df.loc[:, df.columns.notna()]
            
            st.subheader("🔍 Localizar Tela")
            bus = st.text_input("Ingresa Código o Descripción:").upper()

            if bus:
                mask = df['CODIGO'].astype(str).str.upper().str.contains(bus) | \
                       df['DESCRIPCION'].astype(str).str.upper().str.contains(bus)
                res = df[mask]
                
                if not res.empty:
                    st.success(f"✅ Se encontraron {len(res)} artículos")
                    st.dataframe(res[['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19']])
                    
                    st.info("Para registrar, haz clic en el botón:")
                    st.link_button("📝 REGISTRAR EN GOOGLE FORMS", url_form)
                else:
                    st.warning("No se encontró el artículo.")

            st.divider()
            st.subheader("📋 Vista de Inventario")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No encontré la columna 'CODIGO'. Mostrando datos detectados:")
            st.dataframe(df_raw.head(10))

except Exception as e:
    st.error("Error de conexión.")
    st.write(f"Detalle: {e}")
