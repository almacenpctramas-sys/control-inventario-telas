import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración de página
st.set_page_config(page_title="Control Telas Pro", layout="wide")

st.title("📦 Sistema de Inventario Almacenes 18 y 19")

# --- 1. INICIALIZACIÓN DE MEMORIA (Caja de Seguridad) ---
if 'df_inventario' not in st.session_state:
    st.session_state.df_inventario = None

# --- 2. CARGA DE ARCHIVO (Solo se muestra si no hay datos en memoria) ---
if st.session_state.df_inventario is None:
    st.info("👋 Para comenzar, sube tu archivo de Excel.")
    archivo = st.file_uploader("Subir archivo de inventario", type=["xlsx"])
    
    if archivo:
        # Cargamos el archivo una sola vez
        df_original = pd.read_excel(archivo, skiprows=2)
        # Limpieza de nombres de columnas
        df_original.columns = [str(c).strip() for c in df_original.columns]
        # Guardamos en la memoria permanente de la sesión
        st.session_state.df_inventario = df_original
        st.rerun()

# --- 3. PANEL DE TRABAJO (Si el archivo ya está en memoria) ---
else:
    df = st.session_state.df_inventario

    # Barra lateral para gestión de archivos
    with st.sidebar:
        st.header("⚙️ Gestión")
        if st.button("🗑️ Cargar un Nuevo Archivo"):
            st.session_state.df_inventario = None
            st.rerun()
        st.write("---")
        st.success("Archivo cargado y protegido en memoria.")

    # Buscadores
    st.subheader("🔍 Buscador de Artículos")
    col_b1, col_b2 = st.columns(2)
    bus_cod = col_b1.text_input("Buscar por CÓDIGO (Ej: V1624):").upper()
    bus_des = col_b2.text_input("Buscar por DESCRIPCIÓN (Ej: DECO STYLE):").upper()

    # Lógica de filtrado
    mask = pd.Series([False] * len(df))
    if bus_cod:
        mask = df['CODIGO'].astype(str).str.upper().str.startswith(bus_cod)
    elif bus_des:
        mask = df['DESCRIPCION'].astype(str).str.upper().str.contains(bus_des)

    # Sección de Marcado
    if (bus_cod or bus_des):
        encontrados = df[mask]
        if not encontrados.empty:
            st.write(f"✅ Se encontraron **{len(encontrados)}** artículos.")
            st.dataframe(encontrados[['CODIGO', 'DESCRIPCION', 'Almacen 18', 'Almacen 19']])
            
            m1, m2 = st.columns(2)
            if m1.button("📌 Marcar Todo en Almacén 18"):
                st.session_state.df_inventario.loc[mask, 'Almacen 18'] = datetime.now().strftime("%d/%m/%Y")
                st.toast("Actualizado en Almacén 18")
                st.rerun()
            if m2.button("📌 Marcar Todo en Almacén 19"):
                st.session_state.df_inventario.loc[mask, 'Almacen 19'] = datetime.now().strftime("%d/%m/%Y")
                st.toast("Actualizado en Almacén 19")
                st.rerun()
        else:
            st.warning("No se encontraron coincidencias.")

    st.divider()

    # --- 4. VISTA GENERAL Y FILTROS ---
    st.subheader("📋 Estado del Inventario Completo")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    # Usamos un 'radio button' para que el filtro se mantenga fijo
    filtro = col_f1.radio("Ver:", ["Todos", "Pendientes Alm 18", "Pendientes Alm 19"], horizontal=True)

    df_view = df.copy()
    if filtro == "Pendientes Alm 18":
        df_view = df_view[df_view['Almacen 18'].isna() | (df_view['Almacen 18'].astype(str).isin(['0', 'nan', 'None']))]
    elif filtro == "Pendientes Alm 19":
        df_view = df_view[df_view['Almacen 19'].isna() | (df_view['Almacen 19'].astype(str).isin(['0', 'nan', 'None']))]

    st.dataframe(df_view, use_container_width=True)

    # --- 5. DESCARGA DE SEGURIDAD ---
    st.write("---")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 DESCARGAR EXCEL ACTUALIZADO",
        data=output.getvalue(),
        file_name=f"Inventario_Telas_{datetime.now().strftime('%d-%m-%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
