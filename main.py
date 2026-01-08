import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Control Telas Pro", layout="wide")

st.title("📦 Sistema de Inventario Almacenes 18 y 19")

# --- 1. GESTIÓN DE MEMORIA ROBUSTA ---
# Usamos session_state para que los datos sobrevivan a las acciones dentro de la app
if 'df' not in st.session_state:
    st.session_state.df = None

# --- 2. CARGA DE ARCHIVO ---
# Si no hay datos en memoria, mostramos el cargador
if st.session_state.df is None:
    archivo = st.file_uploader("Sube tu Excel de inventario para comenzar", type=["xlsx"])
    if archivo:
        # Leemos el excel (skiprows=2 porque tus datos reales empiezan en la fila 3)
        df_lectura = pd.read_excel(archivo, skiprows=2)
        # Limpiar nombres de columnas para evitar errores de espacios
        df_lectura.columns = [str(c).strip() for c in df_lectura.columns]
        st.session_state.df = df_lectura
        st.rerun()
else:
    # --- 3. INTERFAZ DE TRABAJO (Cuando el archivo ya está cargado) ---
    df = st.session_state.df

    st.sidebar.header("Opciones")
    if st.sidebar.button("🗑️ Cambiar/Borrar Archivo Actual"):
        st.session_state.df = None
        st.rerun()

    # Buscadores
    st.subheader("🔍 Buscador Inteligente")
    col_bus1, col_bus2 = st.columns(2)
    bus_cod = col_bus1.text_input("Código (Ej: V1624):").upper()
    bus_des = col_bus2.text_input("Descripción (Ej: DECO STYLE):").upper()

    # Lógica de filtrado para marcado
    mask = pd.Series([False] * len(df))
    if bus_cod:
        mask = df['CODIGO'].astype(str).str.upper().str.startswith(bus_cod)
    elif bus_des:
        mask = df['DESCRIPCION'].astype(str).str.upper().str.contains(bus_des)

    if (bus_cod or bus_des):
        seleccionados = df[mask]
        if not seleccionados.empty:
            st.write(f"📊 Artículos encontrados: {len(seleccionados)}")
            st.dataframe(seleccionados[['CODIGO', 'DESCRIPCION', 'Almacen 18', 'Almacen 19']])

            c1, c2 = st.columns(2)
            if c1.button("✅ Marcar todo lo filtrado en Alm 18"):
                st.session_state.df.loc[mask, 'Almacen 18'] = datetime.now().strftime("%d/%m/%Y")
                st.success("Marcado exitoso")
                st.rerun()
            if c2.button("✅ Marcar todo lo filtrado en Alm 19"):
                st.session_state.df.loc[mask, 'Almacen 19'] = datetime.now().strftime("%d/%m/%Y")
                st.success("Marcado exitoso")
                st.rerun()
        else:
            st.warning("No se encontraron coincidencias.")

    st.divider()

    # --- 4. CONTROL DE PENDIENTES ---
    st.subheader("📋 Estado General")
    f1, f2, f3 = st.columns(3)
    
    # Filtros de visualización
    ver = "Todos"
    if f2.button("❌ Ver solo Pendientes 18"): ver = "P18"
    if f3.button("❌ Ver solo Pendientes 19"): ver = "P19"
    if f1.button("👁️ Ver Todos"): ver = "Todos"

    df_mostrar = df.copy()
    if ver == "P18":
        df_mostrar = df_mostrar[df_mostrar['Almacen 18'].isna() | (df_mostrar['Almacen 18'].astype(str) == "0")]
    elif ver == "P19":
        df_mostrar = df_mostrar[df_mostrar['Almacen 19'].isna() | (df_mostrar['Almacen 19'].astype(str) == "0")]

    st.dataframe(df_mostrar, use_container_width=True)

    # --- 5. DESCARGA SEGURA ---
    st.divider()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 DESCARGAR EXCEL CON CAMBIOS",
        data=output.getvalue(),
        file_name=f"Inventario_Telas_{datetime.now().strftime('%d_%m')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
