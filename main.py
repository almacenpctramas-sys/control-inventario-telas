import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Control Telas", layout="wide")

st.title("📦 Inventario Almacenes 18 y 19")

archivo = st.file_uploader("Sube tu Excel de inventario", type=["xlsx"])

if archivo:
    # Leemos el excel saltando las primeras 2 filas según tu formato
    df = pd.read_excel(archivo, skiprows=2)
    
    # Limpiamos nombres de columnas por si acaso hay espacios
    df.columns = [str(c).strip() for c in df.columns]

    # --- LÓGICA DE BÚSQUEDA Y MARCADO ---
    busqueda = st.text_input("Ingresa el inicio del código (ej: C0113):").upper()

    if busqueda and 'CODIGO' in df.columns:
        mascara = df['CODIGO'].astype(str).str.startswith(busqueda)
        seleccionados = df[mascara]
        
        st.write(f"🔍 Artículos seleccionados para marcar: {len(seleccionados)}")
        st.dataframe(seleccionados)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Marcar Almacén 18"):
                df.loc[mascara, 'Almacen 18'] = datetime.now().strftime("%d/%m/%Y")
                st.success("✅ Marcado en Alm 18")
        with col2:
            if st.button("Marcar Almacén 19"):
                df.loc[mascara, 'Almacen 19'] = datetime.now().strftime("%d/%m/%Y")
                st.success("✅ Marcado en Alm 19")

    st.divider()

    # --- LÓGICA DE CONTROL VISUAL (LO QUE SOLICITASTE) ---
    st.subheader("📋 Estado General del Inventario")

    # Creamos la columna de estado para cada almacén
    def verificar_estado(fila, col):
        if pd.isna(fila[col]) or str(fila[col]).strip() == "" or str(fila[col]) == "0":
            return "❌ Pendiente"
        return f"✅ {fila[col]}"

    if 'Almacen 18' in df.columns and 'Almacen 19' in df.columns:
        # Crear vista resumida
        df_visual = df.copy()
        df_visual['Estado Alm 18'] = df_visual.apply(lambda x: verificar_estado(x, 'Almacen 18'), axis=1)
        df_visual['Estado Alm 19'] = df_visual.apply(lambda x: verificar_estado(x, 'Almacen 19'), axis=1)

        # Mostrar tabla completa con los estados
        st.dataframe(df_visual[['CODIGO', 'DESCRIPCION', 'Estado Alm 18', 'Estado Alm 19']], use_container_width=True)
        
        # Resumen numérico
        pendientes_18 = (df_visual['Estado Alm 18'] == "❌ Pendiente").sum()
        pendientes_19 = (df_visual['Estado Alm 19'] == "❌ Pendiente").sum()
        
        st.info(f"Faltan por inventariar: **{pendientes_18}** artículos en Alm 18 y **{pendientes_19}** en Alm 19.")

    # Preparar descarga
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Descargar Excel Final",
        data=output.getvalue(),
        file_name="Inventario_Actualizado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
