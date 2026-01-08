import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Control Telas Pro", layout="wide")

st.title("📦 Sistema de Inventario Almacenes 18 y 19")

# --- 1. MEMORIA DE LA APLICACIÓN (Session State) ---
if 'df' not in st.session_state:
    st.session_state.df = None

# --- 2. CARGA DE ARCHIVO ---
archivo = st.file_uploader("Sube tu Excel de inventario", type=["xlsx"])

if archivo and st.session_state.df is None:
    st.session_state.df = pd.read_excel(archivo, skiprows=2)
    st.session_state.df.columns = [str(c).strip() for c in st.session_state.df.columns]

if st.session_state.df is not None:
    df = st.session_state.df

    # --- 3. BUSCADOR DUAL (CÓDIGO O DESCRIPCIÓN) ---
    st.subheader("🔍 Buscador y Marcado Rápido")
    col_bus1, col_bus2 = st.columns(2)
    
    bus_cod = col_bus1.text_input("Buscar por CÓDIGO (Ej: V1624):").upper()
    bus_des = col_bus2.text_input("Buscar por DESCRIPCIÓN (Ej: DECO STYLE):").upper()

    # Lógica de búsqueda combinada
    mask = pd.Series([False] * len(df))
    
    if bus_cod:
        mask = df['CODIGO'].astype(str).str.upper().str.startswith(bus_cod)
    elif bus_des:
        # El buscador de descripción es "sensible": busca la frase en cualquier parte del texto
        mask = df['DESCRIPCION'].astype(str).str.upper().str.contains(bus_des)

    if (bus_cod or bus_des) and not df[mask].empty:
        seleccionados = df[mask]
        st.write(f"📊 Artículos encontrados: {len(seleccionados)}")
        st.dataframe(seleccionados[['CODIGO', 'DESCRIPCION', 'Almacen 18', 'Almacen 19']])

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Marcar Almacén 18"):
                st.session_state.df.loc[mask, 'Almacen 18'] = datetime.now().strftime("%d/%m/%Y")
                st.rerun()
        with c2:
            if st.button("✅ Marcar Almacén 19"):
                st.session_state.df.loc[mask, 'Almacen 19'] = datetime.now().strftime("%d/%m/%Y")
                st.rerun()
    elif (bus_cod or bus_des):
        st.warning("⚠️ No se encontraron artículos con esa búsqueda.")

    st.divider()

    # --- 4. FILTROS Y VISTA GENERAL ---
    st.subheader("📋 Estado General del Inventario")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    ver_todos = col_f1.button("👁️ Ver Todo")
    ver_p18 = col_f2.button("❌ Pendientes Alm 18")
    ver_p19 = col_f3.button("❌ Pendientes Alm 19")

    df_visual = df.copy()
    if ver_p18:
        df_visual = df_visual[df_visual['Almacen 18'].isna() | (df_visual['Almacen 18'].astype(str) == "0")]
        st.write("Mostrando: **Pendientes Almacén 18**")
    elif ver_p19:
        df_visual = df_visual[df_visual['Almacen 19'].isna() | (df_visual['Almacen 19'].astype(str) == "0")]
        st.write("Mostrando: **Pendientes Almacén 19**")

    st.dataframe(df_visual, use_container_width=True)

    # --- 5. DESCARGA Y LIMPIEZA ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button("📥 Descargar Excel Final", output.getvalue(), "Inventario_Actualizado.xlsx")

    if st.sidebar.button("🗑️ Cargar otro archivo"):
        st.session_state.df = None
        st.rerun()
