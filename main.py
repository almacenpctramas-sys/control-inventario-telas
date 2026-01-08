import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Control Telas Pro", layout="wide")

st.title("📦 Sistema de Inventario Almacenes 18 y 19")

# --- 1. MEMORIA DE SESIÓN ---
if 'df_master' not in st.session_state:
    st.session_state.df_master = None

# --- 2. CARGA DE ARCHIVO ---
if st.session_state.df_master is None:
    st.info("👋 Sube el último Excel que descargaste para continuar.")
    archivo_subido = st.file_uploader("Selecciona tu archivo Excel", type=["xlsx"])
    
    if archivo_subido is not None:
        df_temp = pd.read_excel(archivo_subido)
        # Ajuste para archivos nuevos vs archivos ya procesados
        if "CODIGO" not in df_temp.columns:
            df_temp = pd.read_excel(archivo_subido, skiprows=2)
        
        df_temp.columns = [str(c).strip() for c in df_temp.columns]
        st.session_state.df_master = df_temp
        st.rerun()

# --- 3. PANEL DE TRABAJO ---
else:
    df = st.session_state.df_master

    # Buscadores
    st.subheader("🔍 Localizar y Registrar")
    c1, c2 = st.columns(2)
    bus_cod = c1.text_input("Código:").upper()
    bus_des = c2.text_input("Descripción (ej: DECO STYLE):").upper()

    mask = pd.Series([False] * len(df))
    if bus_cod:
        mask = df['CODIGO'].astype(str).str.upper().str.startswith(bus_cod)
    elif bus_des:
        mask = df['DESCRIPCION'].astype(str).str.upper().str.contains(bus_des)

    if bus_cod or bus_des:
        res = df[mask]
        if not res.empty:
            st.write(f"📊 Items encontrados: {len(res)}")
            st.dataframe(res[['CODIGO', 'DESCRIPCION', 'Almacen 18', 'Almacen 19']])
            
            b1, b2 = st.columns(2)
            if b1.button("📌 REGISTRAR EN ALM 18"):
                st.session_state.df_master.loc[mask, 'Almacen 18'] = datetime.now().strftime("%d/%m/%Y")
                st.success("✅ Guardado en sesión.")
            
            if b2.button("📌 REGISTRAR EN ALM 19"):
                st.session_state.df_master.loc[mask, 'Almacen 19'] = datetime.now().strftime("%d/%m/%Y")
                st.success("✅ Guardado en sesión.")
        else:
            st.error("No se encontró nada.")

    # --- BOTÓN DE DESCARGA SIEMPRE VISIBLE ---
    st.write("---")
    st.subheader("💾 Guardar Cambios en tu PC")
    st.write("Haz clic aquí cada vez que marques algo para no perder el progreso:")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 DESCARGAR EXCEL DE RESPALDO",
        data=buffer.getvalue(),
        file_name=f"Inventario_Respaldo_{datetime.now().strftime('%H_%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.write("---")

    # --- 4. VISTA GENERAL ---
    st.subheader("📋 Revisión de Inventario")
    filtro = st.radio("Mostrar:", ["Todos", "Pendientes 18", "Pendientes 19"], horizontal=True)
    
    df_v = df.copy()
    if "18" in filtro:
        df_v = df_v[df_v['Almacen 18'].isna() | (df_v['Almacen 18'].astype(str).isin(['0', 'nan', 'None', ''] archeological))]
    elif "19" in filtro:
        df_v = df_v[df_v['Almacen 19'].isna() | (df_v['Almacen 19'].astype(str).isin(['0', 'nan', 'None', '']))]

    st.dataframe(df_v, use_container_width=True)

    if st.button("🗑️ Salir y cargar otro archivo"):
        st.session_state.df_master = None
        st.rerun()
