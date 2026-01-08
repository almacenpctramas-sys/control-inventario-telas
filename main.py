import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")
st.title("📊 Control de Inventario Almacenes 18 y 19")

# --- CONFIGURACIÓN ---
url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

# PEGA AQUÍ EL ENLACE QUE ACABAS DE COPIAR
url_form = "TU_LINK_COPIADO" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Leemos desde la fila 3 (donde están tus títulos reales)
    df = conn.read(spreadsheet=url_sheet, ttl=0, skiprows=2)
    df.columns = [str(c).strip().upper() for c in df.columns]

    st.subheader("🔍 Localizar Tela")
    bus = st.text_input("Ingresa Código o Descripción:").upper()

    if bus:
        mask = df['CODIGO'].astype(str).str.upper().str.contains(bus) | \
               df['DESCRIPCION'].astype(str).str.upper().str.contains(bus)
        res = df[mask]
        
        if not res.empty:
            st.success(f"✅ Se encontraron {len(res)} artículos")
            st.dataframe(res[['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19']])
            
            st.info("Para registrar el inventario, usa el botón de abajo:")
            # Este botón abre el formulario que acabas de publicar
            st.link_button("📝 REGISTRAR EN GOOGLE FORMS", url_form)
        else:
            st.warning("No se encontró ninguna tela con ese nombre o código.")

    st.divider()
    st.subheader("📋 Inventario Completo")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Error al conectar con la base de datos.")
    st.write(f"Detalle: {e}")
