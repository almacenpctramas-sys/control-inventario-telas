import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Inventario PC7", layout="wide")

st.title("📊 Control de Inventario Permanente")
st.info("Conectado a Google Sheets. Los cambios son permanentes.")

url = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url, ttl=0)
    
    # --- LIMPIEZA AUTOMÁTICA DE COLUMNAS ---
    # Esto quita tildes y espacios para que no de error
    df.columns = df.columns.str.strip().str.upper().str.replace('Ó', 'O').str.replace('Í', 'I')
    
    # Buscamos los nombres reales que quedaron tras la limpieza
    col_cod = 'CODIGO'
    col_des = 'DESCRIPCION'
    col_a18 = 'ALMACEN 18'
    col_a19 = 'ALMACEN 19'

    # --- BUSCADORES ---
    st.subheader("🔍 Localizar Artículos")
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
            st.write(f"✅ Items encontrados: {len(res)}")
            st.dataframe(res[[col_cod, col_des, col_a18, col_a19]])
            
            b1, b2 = st.columns(2)
            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            
            if b1.button("📌 REGISTRAR EN ALM 18"):
                df.loc[mask, col_a18] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("Guardado en Google Sheets")
                st.rerun()
                
            if b2.button("📌 REGISTRAR EN ALM 19"):
                df.loc[mask, col_a19] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("Guardado en Google Sheets")
                st.rerun()
        else:
            st.warning("No se encontró ese artículo.")

    st.divider()

    # --- LISTADO Y FILTROS ---
    st.subheader("📋 Estado General")
    filtro = st.radio("Mostrar:", ["Todos", "Pendientes 18", "Pendientes 19"], horizontal=True)

    df_v = df.copy()
    if "18" in filtro:
        df_v = df_v[df_v[col_a18].isna() | (df_v[col_a18].astype(str).isin(['0', 'nan', 'None', '', '0.0']))]
    elif "19" in filtro:
        df_v = df_v[df_v[col_a19].isna() | (df_v[col_a19].astype(str).isin(['0', 'nan', 'None', '', '0.0']))]

    st.dataframe(df_v, use_container_width=True)

except Exception as e:
    st.error("Error de nombres de columna.")
    st.write(f"Asegúrate de que en tu Excel los títulos sean: CODIGO, DESCRIPCION, ALMACEN 18, ALMACEN 19")
    st.write(f"Error detectado: {e}")
