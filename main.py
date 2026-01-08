import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Inventario PC7 Real-Time", layout="wide")

st.title("📊 Control de Inventario Permanente")
st.info("Los cambios se guardan directamente en tu Google Sheet.")

# --- CONEXIÓN CON TU GOOGLE SHEET ---
url = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

try:
    # Creamos la conexión
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Leer datos (ttl=0 para que no use memoria vieja y lea siempre lo último)
    df = conn.read(spreadsheet=url, ttl=0)
    
    # Limpiar nombres de columnas (pasar a mayúsculas y quitar espacios)
    df.columns = [str(c).strip().upper() for c in df.columns]

    # --- BUSCADORES ---
    st.subheader("🔍 Localizar Artículos")
    c1, c2 = st.columns(2)
    bus_cod = c1.text_input("Código (Ej: C0108):").upper()
    bus_des = c2.text_input("Descripción (Ej: DECO STYLE):").upper()

    mask = pd.Series([False] * len(df))
    if bus_cod:
        mask = df['CODIGO'].astype(str).str.upper().str.contains(bus_cod)
    elif bus_des:
        mask = df['DESCRIPCION'].astype(str).str.upper().str.contains(bus_des)

    if bus_cod or bus_des:
        res = df[mask]
        if not res.empty:
            st.write(f"✅ Encontrados: {len(res)} artículos")
            st.dataframe(res[['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19']])
            
            b1, b2 = st.columns(2)
            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            
            if b1.button("📌 GUARDAR EN ALM 18"):
                df.loc[mask, 'ALMACEN 18'] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("✅ ¡Actualizado en Google Sheets!")
                st.rerun()
                
            if b2.button("📌 GUARDAR EN ALM 19"):
                df.loc[mask, 'ALMACEN 19'] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("✅ ¡Actualizado en Google Sheets!")
                st.rerun()
        else:
            st.warning("No se encontró ese código o descripción.")

    st.divider()

    # --- VISTA DE ESTADO ---
    st.subheader("📋 Lista Completa / Pendientes")
    filtro = st.radio("Mostrar:", ["Todos", "Pendientes Alm 18", "Pendientes Alm 19"], horizontal=True)

    df_v = df.copy()
    if "18" in filtro:
        df_v = df_v[df_v['ALMACEN 18'].isna() | (df_v['ALMACEN 18'].astype(str).isin(['0', 'nan', 'None', '']))]
    elif "19" in filtro:
        df_v = df_v[df_v['ALMACEN 19'].isna() | (df_v['ALMACEN 19'].astype(str).isin(['0', 'nan', 'None', '']))]

    st.dataframe(df_v, use_container_width=True)

except Exception as e:
    st.error("Error de conexión o de librerías.")
    st.write(f"Detalle técnico: {e}")
