import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Inventario PC7", layout="wide")
st.title("📊 Control de Inventario Almacenes 18 y 19")

# URL de tu archivo (la misma de siempre)
url_sheet = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

# --- PEGA AQUÍ TU ENLACE DEL FORMULARIO ---
url_form = "TU_LINK_AQUI" 

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leemos específicamente la 'Hoja 1' saltando las filas vacías iniciales
    # según tu imagen, los títulos están en la fila 3
    df = conn.read(spreadsheet=url_sheet, worksheet="Hoja 1", ttl=0, skiprows=2)
    
    # Limpiamos nombres de columnas (quitar espacios y poner mayúsculas)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Verificamos que existan datos
    if df.empty:
        st.warning("No se encontraron datos en la 'Hoja 1'. Revisa el nombre de la pestaña.")
    else:
        st.subheader("🔍 Localizar Tela")
        bus = st.text_input("Ingresa Código o Descripción:").upper()

        if bus:
            # Filtramos por Código o Descripción
            mask = df['CODIGO'].astype(str).str.upper().str.contains(bus) | \
                   df['DESCRIPCION'].astype(str).str.upper().str.contains(bus)
            res = df[mask]
            
            if not res.empty:
                st.success(f"✅ Artículos encontrados: {len(res)}")
                # Mostramos las columnas importantes
                cols_ok = [c for c in ['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19'] if c in df.columns]
                st.dataframe(res[cols_ok], use_container_width=True)
                
                st.info("Para registrar un ingreso, haz clic abajo:")
                st.link_button("📝 REGISTRAR EN GOOGLE FORMS", url_form)
            else:
                st.warning("No se encontró el artículo.")

        st.divider()
        st.subheader("📋 Inventario Completo")
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Error de conexión.")
    st.write("Asegúrate de que la pestaña se llame exactamente 'Hoja 1' y no esté vacía.")
    st.write(f"Detalle: {e}")
