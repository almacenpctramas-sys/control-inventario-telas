import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Inventario PC7", layout="wide")

st.title("📊 Control de Inventario en Tiempo Real")
st.write("Los cambios se guardan automáticamente en Google Sheets.")

# --- CONEXIÓN CON TU GOOGLE SHEET ---
url = "https://docs.google.com/spreadsheets/d/1pCki91RhG37d6x9mw0bZ3XnVMWAFkQe3NxIq4a9rrvM/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Leemos los datos (asumiendo que los datos reales están en la hoja principal)
    df = conn.read(spreadsheet=url, ttl=0) # ttl=0 para que siempre lea lo más nuevo
    
    # Limpieza de columnas para evitar errores
    df.columns = [str(c).strip().upper() for c in df.columns]

    # --- BUSCADORES ---
    st.subheader("🔍 Localizar Artículos")
    c1, c2 = st.columns(2)
    bus_cod = c1.text_input("Código (Ej: C0108):").upper()
    bus_des = c2.text_input("Descripción (Ej: DECO STYLE):").upper()

    # Lógica de búsqueda
    mask = pd.Series([False] * len(df))
    if bus_cod:
        mask = df['CODIGO'].astype(str).str.upper().str.contains(bus_cod)
    elif bus_des:
        mask = df['DESCRIPCION'].astype(str).str.upper().str.contains(bus_des)

    if bus_cod or bus_des:
        res = df[mask]
        if not res.empty:
            st.write(f"✅ Encontrados: {len(res)} items")
            st.dataframe(res[['CODIGO', 'DESCRIPCION', 'ALMACEN 18', 'ALMACEN 19']])
            
            b1, b2 = st.columns(2)
            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            
            if b1.button("📌 REGISTRAR EN ALM 18"):
                df.loc[mask, 'ALMACEN 18'] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("Guardado en Google Sheets")
                st.rerun()
                
            if b2.button("📌 REGISTRAR EN ALM 19"):
                df.loc[mask, 'ALMACEN 19'] = fecha_hoy
                conn.update(spreadsheet=url, data=df)
                st.success("Guardado en Google Sheets")
                st.rerun()
        else:
            st.warning("No se encontraron coincidencias.")

    st.divider()

    # --- VISTA DE PENDIENTES ---
    st.subheader("📋 Estado Actual")
    filtro = st.radio("Ver lista:", ["Todos", "Pendientes Alm 18", "Pendientes Alm 19"], horizontal=True)

    df_v = df.copy()
    if "18" in filtro:
        # Filtra si está vacío, es 0 o es None
        df_v = df_v[df_v['ALMACEN 18'].isna() | (df_v['ALMACEN 18'].astype(str).isin(['0', 'nan', 'None', '']))]
    elif "19" in filtro:
        df_v = df_v[df_v['ALMACEN 19'].isna() | (df_v['ALMACEN 19'].astype(str).isin(['0', 'nan', 'None', '']))]

    st.dataframe(df_v, use_container_width=True)

except Exception as e:
    st.error("Error de conexión.")
    st.info("Asegúrate de que el Google Sheet esté compartido como 'Editor' para 'Cualquier persona con el enlace'.")
    st.write(e)
