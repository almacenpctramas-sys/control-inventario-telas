import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración inicial de la página
st.set_page_config(page_title="Control Telas Pro", layout="wide")

st.title("📦 Sistema de Inventario Almacenes 18 y 19")

# --- 1. MEMORIA PERSISTENTE (Aquí es donde evitamos que se borre) ---
if 'df_master' not in st.session_state:
    st.session_state.df_master = None

# --- 2. CARGA DEL ARCHIVO (Solo aparece si la memoria está vacía) ---
if st.session_state.df_master is None:
    st.info("👋 Por favor, sube tu archivo Excel para empezar el inventario.")
    archivo_subido = st.file_uploader("Selecciona tu archivo .xlsx", type=["xlsx"])
    
    if archivo_subido is not None:
        # Cargamos los datos ignorando las primeras 2 filas de encabezado
        df_temp = pd.read_excel(archivo_subido, skiprows=2)
        # Limpiamos nombres de columnas
        df_temp.columns = [str(c).strip() for c in df_temp.columns]
        # Lo guardamos en la memoria 'maestra'
        st.session_state.df_master = df_temp
        st.rerun()

# --- 3. PANEL DE CONTROL (Solo se ve si ya hay un archivo cargado) ---
else:
    # Usamos una referencia corta para trabajar más cómodo
    df = st.session_state.df_master

    # Botón en la barra lateral para resetear todo si es necesario
    with st.sidebar:
        if st.button("🗑️ Cargar un archivo diferente"):
            st.session_state.df_master = None
            st.rerun()

    # Buscadores
    st.subheader("🔍 Localizar Artículos")
    col_b1, col_b2 = st.columns(2)
    bus_cod = col_b1.text_input("Buscar por CÓDIGO:").upper()
    bus_des = col_b2.text_input("Buscar por DESCRIPCIÓN (ej: Deco Style):").upper()

    # Aplicar filtros
    mask = pd.Series([False] * len(df))
    if bus_cod:
        mask = df['CODIGO'].astype(str).str.upper().str.startswith(bus_cod)
    elif bus_des:
        mask = df['DESCRIPCION'].astype(str).str.upper().str.contains(bus_des)

    # Lógica de Marcado (Botón de Guardado)
    if bus_cod or bus_des:
        resultados = df[mask]
        if not resultados.empty:
            st.write(f"📊 Encontrados: {len(resultados)} items")
            st.dataframe(resultados[['CODIGO', 'DESCRIPCION', 'Almacen 18', 'Almacen 19']])
            
            # Botones para "Guardar" la marca en la memoria
            c1, c2 = st.columns(2)
            if c1.button("📌 GUARDAR FECHA EN ALM 18"):
                st.session_state.df_master.loc[mask, 'Almacen 18'] = datetime.now().strftime("%d/%m/%Y")
                st.success("¡Guardado en memoria! Puedes seguir buscando.")
                # NO usamos rerun aquí para que no parpadee la pantalla
            
            if c2.button("📌 GUARDAR FECHA EN ALM 19"):
                st.session_state.df_master.loc[mask, 'Almacen 19'] = datetime.now().strftime("%d/%m/%Y")
                st.success("¡Guardado en memoria! Puedes seguir buscando.")
        else:
            st.warning("No hay resultados para esa búsqueda.")

    st.divider()

    # --- 4. VISUALIZACIÓN Y FILTROS DE ESTADO ---
    st.subheader("📋 Revisión de Inventario Completo")
    
    # Selector de filtros que NO borra los datos
    opcion_filtro = st.radio(
        "Ver lista de:",
        ["Todos los artículos", "Solo pendientes Almacén 18", "Solo pendientes Almacén 19"],
        horizontal=True
    )

    df_vista = df.copy()
    
    if "18" in opcion_filtro:
        df_vista = df_vista[df_vista['Almacen 18'].isna() | (df_vista['Almacen 18'].astype(str).isin(['0', 'nan', 'None']))]
    elif "19" in opcion_filtro:
        df_vista = df_vista[df_vista['Almacen 19'].isna() | (df_vista['Almacen 19'].astype(str).isin(['0', 'nan', 'None']))]

    st.dataframe(df_vista, use_container_width=True)

    # --- 5. BOTÓN DE DESCARGA FINAL ---
    st.write("---")
    st.write("Recuerda descargar tu archivo al finalizar para no perder los cambios.")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 DESCARGAR EXCEL CON TODAS LAS FECHAS",
        data=buffer.getvalue(),
        file_name=f"Inventario_Final_{datetime.now().strftime('%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
