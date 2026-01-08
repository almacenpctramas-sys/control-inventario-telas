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
    # Solo se carga la primera vez o cuando subes uno nuevo
    st.session_state.df = pd.read_excel(archivo, skiprows=2)
    # Limpiar nombres de columnas
    st.session_state.df.columns = [str(c).strip() for c in st.session_state.df.columns]

if st.session_state.df is not None:
    df = st.session_state.df # Usamos el df de la memoria

    # --- 3. BUSCADOR Y MARCADO ---
    st.subheader("🔍 Buscador y Marcado Rápido")
    busqueda = st.text_input("Ingresa el inicio del código (ej: C0113):").upper()

    if busqueda and 'CODIGO' in df.columns:
        mascara = df['CODIGO'].astype(str).str.startswith(busqueda)
        seleccionados = df[mascara]
        
        if not seleccionados.empty:
            st.write(f"Artículos encontrados para marcar: {len(seleccionados)}")
            st.dataframe(seleccionados[['CODIGO', 'DESCRIPCION', 'Almacen 18', 'Almacen 19']])

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Marcar Almacén 18"):
                    st.session_state.df.loc[mascara, 'Almacen 18'] = datetime.now().strftime("%d/%m/%Y")
                    st.success("Actualizado Alm 18")
                    st.rerun() # Refresca para mostrar los cambios abajo
            with c2:
                if st.button("✅ Marcar Almacén 19"):
                    st.session_state.df.loc[mascara, 'Almacen 19'] = datetime.now().strftime("%d/%m/%Y")
                    st.success("Actualizado Alm 19")
                    st.rerun()
        else:
            st.warning("No se encontraron coincidencias.")

    st.divider()

    # --- 4. BOTONES DE FILTRO RÁPIDO ---
    st.subheader("📋 Control Visual de Pendientes")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    ver_todos = col_f1.button("👁️ Ver Todo el Inventario")
    ver_pendientes = col_f2.button("❌ Ver solo Pendientes (Alm 18)")
    ver_pendientes_19 = col_f3.button("❌ Ver solo Pendientes (Alm 19)")

    # Lógica de visualización
    df_visual = df.copy()
    
    # Definir qué mostrar basado en los botones
    if ver_pendientes:
        df_visual = df_visual[df_visual['Almacen 18'].isna() | (df_visual['Almacen 18'].astype(str) == "0")]
        st.write("Mostrando: **Pendientes Almacén 18**")
    elif ver_pendientes_19:
        df_visual = df_visual[df_visual['Almacen 19'].isna() | (df_visual['Almacen 19'].astype(str) == "0")]
        st.write("Mostrando: **Pendientes Almacén 19**")
    else:
        st.write("Mostrando: **Todos los artículos**")

    # Mostrar tabla principal
    st.dataframe(df_visual, use_container_width=True)

    # --- 5. DESCARGA ---
    st.divider()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Descargar Excel con todos los cambios",
        data=output.getvalue(),
        file_name="Inventario_Finalizado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Botón para limpiar memoria y cargar otro archivo
    if st.sidebar.button("🗑️ Borrar lista y cargar nuevo archivo"):
        st.session_state.df = None
        st.rerun()
