import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Inventario PC7", layout="wide")

st.title("📊 Control de Inventario Permanente")

# URL de tu Google Sheet
url = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leemos saltando las primeras 2 filas vacías según tu imagen
    df = conn.read(spreadsheet=url, ttl=0, skiprows=2)
    
    # Limpiamos nombres de columnas
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Nombres de columnas según tu archivo
    c_cod = 'CODIGO'
    c_des = 'DESCRIPCION'
    c_a18 = 'ALMACEN 18'
    c_a19 = 'ALMACEN 19'

    st.subheader("🔍 Buscar Artículo")
    c1, c2 = st.columns(2)
    bus_cod = c1.text_input("Código:").upper()
    bus_des = c2.text_input("Descripción:").upper()

    mask = pd.Series([False] * len(df))
    if bus_cod:
        mask = df[c_cod].astype(str).str.upper().str.contains(bus_cod)
    elif bus_des:
        mask = df[c_des].astype(str).str.upper().str.contains(bus_des)

    if bus_cod or bus_des:
        res = df[mask]
        if not res.empty:
            st.write(f"✅ Encontrados: {len(res)}")
            st.dataframe(res[[c_cod, c_des, c_a18, c_a19]])
            
            b1, b2 = st.columns(2)
            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            
            if b1.button("📌 REGISTRAR EN ALM 18"):
                df.loc[mask, c_a18] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("✅ Guardado en Google Sheets")
                st.rerun()
                
            if b2.button("📌 REGISTRAR EN ALM 19"):
                df.loc[mask, c_a19] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("✅ Guardado en Google Sheets")
                st.rerun()
        else:
            st.error("No se encontró el artículo.")

    st.divider()
    st.subheader("📋 Estado General")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("⚠️ Error de permisos o estructura.")
    st.info("Asegúrate de cambiar el permiso en Google Sheets de 'Lector' a 'Editor'.")
    st.write(f"Detalle: {e}")
