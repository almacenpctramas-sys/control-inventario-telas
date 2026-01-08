import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Inventario Permanente", layout="wide")
st.title("📊 Control de Inventario PC7")

url = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Saltamos las 2 filas vacías iniciales
    df = conn.read(spreadsheet=url, ttl=0, skiprows=2)
    
    # Limpiamos nombres de columnas para que coincidan siempre
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Identificamos las columnas clave
    col_cod = 'CODIGO'
    col_des = 'DESCRIPCION'
    col_a18 = 'ALMACEN 18'
    col_a19 = 'ALMACEN 19'

    st.subheader("🔍 Buscar y Registrar")
    c1, c2 = st.columns(2)
    bus_cod = c1.text_input("Código:").upper()
    bus_des = c2.text_input("Descripción:").upper()

    mask = pd.Series([False] * len(df))
    if bus_cod:
        mask = df[col_cod].astype(str).str.upper().str.contains(bus_cod)
    elif bus_des:
        mask = df[col_des].astype(str).str.upper().str.contains(bus_des)

    if bus_cod or bus_des:
        res = df[mask]
        if not res.empty:
            st.dataframe(res[[col_cod, col_des, col_a18, col_a19]])
            
            b1, b2 = st.columns(2)
            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            
            if b1.button("✅ MARCAR EN ALMACÉN 18"):
                df.loc[mask, col_a18] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("¡Registrado en Google Sheets!")
                st.rerun()
                
            if b2.button("✅ MARCAR EN ALMACÉN 19"):
                df.loc[mask, col_a19] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("¡Registrado en Google Sheets!")
                st.rerun()

    st.divider()
    st.subheader("📋 Vista de Inventario")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error("Error de conexión.")
    st.write(f"Detalle: {e}")
