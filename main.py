import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")
st.title("📊 Control de Inventario Almacenes 18 y 19")

# Tu URL de Google Sheets
url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

# PEGA AQUÍ TU ENLACE DEL FORMULARIO
url_form = "TU_LINK_AQUI" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # LEER SIN ESPECIFICAR PESTAÑA (esto evita el error de "control characters")
    df_raw = conn.read(spreadsheet=url_sheet, ttl=0)
    
    # Limpiar columnas vacías y filas vacías
    df = df_raw.dropna(how='all').dropna(axis=1, how='all')
    
    # BUSCADOR AUTOMÁTICO DE TÍTULOS
    # Buscamos la fila donde esté la palabra 'CODIGO'
    header_row = None
    for i in range(len(df)):
        if 'CODIGO' in [str(x).upper().strip() for x in df.iloc[i].values]:
            header_row = i
            break
            
    if header_row is not None:
        # Reajustamos la tabla desde donde encontramos los títulos
        df.columns = [str(c).strip().upper() for c in df.iloc[header_row]]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        st.subheader("🔍 Localizar Tela")
        bus = st.text_input("Ingresa Código o Descripción:").upper()

        if bus:
            # Filtramos por Código o Descripción
            mask = df['CODIGO'].astype(str).str.upper().str.contains(bus) | \
                   df['DESCRIPCION'].astype(str).str.upper().str.contains(bus)
            res = df[mask]
            
            if not res.empty:
                st.success(f"✅ Artículos encontrados: {len(res)}")
                # Seleccionamos solo las columnas que queremos ver
                cols_finales = [c for c in ['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19'] if c in df.columns]
                st.dataframe(res[cols_finales], use_container_width=True)
                
                st.info("Para registrar un movimiento, usa el botón:")
                st.link_button("📝 REGISTRAR EN FORMULARIO", url_form)
            else:
                st.warning("No se encontró el artículo.")

        st.divider()
        st.subheader("📋 Inventario Completo")
        st.dataframe(df, use_container_width=True)
    else:
        st.error("No se detectaron los encabezados (CODIGO, DESCRIPCION).")
        st.write("Datos detectados:", df.head())

except Exception as e:
    st.error("Error de conexión.")
    st.write(f"Detalle técnico: {e}")
