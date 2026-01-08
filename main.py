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
    
    # 1. Obtenemos TODAS las pestañas del archivo
    all_sheets = conn.read(spreadsheet=url_sheet, ttl=0, worksheet=None)
    
    df = pd.DataFrame()
    sheet_encontrada = ""

    # 2. Buscamos en cada pestaña la columna 'CODIGO'
    for sheet_name, content in all_sheets.items():
        # Limpiamos nombres de columnas de esta pestaña
        content.columns = [str(c).strip().upper() for c in content.columns]
        if 'CODIGO' in content.columns:
            df = content
            sheet_encontrada = sheet_name
            break
            
    if df.empty:
        st.error("No se encontró la columna 'CODIGO' en ninguna pestaña.")
        st.info("Revisa que tus títulos en el Excel no tengan celdas combinadas.")
    else:
        # Limpieza de datos encontrados
        df = df.dropna(subset=['CODIGO']) # Quitamos filas vacías
        
        st.subheader(f"🔍 Buscador (Hoja detectada: {sheet_encontrada})")
        bus = st.text_input("Ingresa Código o Descripción:").upper()

        if bus:
            # Búsqueda en Código o Descripción
            mask = df['CODIGO'].astype(str).str.upper().str.contains(bus) | \
                   df['DESCRIPCION'].astype(str).str.upper().str.contains(bus)
            res = df[mask]
            
            if not res.empty:
                st.success(f"✅ Artículos encontrados: {len(res)}")
                # Columnas a mostrar
                cols = [c for c in ['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19'] if c in df.columns]
                st.dataframe(res[cols], use_container_width=True)
                
                st.info("Para registrar un ingreso, usa el formulario:")
                st.link_button("📝 REGISTRAR EN GOOGLE FORMS", url_form)
            else:
                st.warning("No se encontró el artículo.")

        st.divider()
        st.subheader("📋 Inventario Completo")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Error de conexión con Google Sheets.")
    st.write(f"Detalle técnico: {e}")
