import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Control Telas", layout="wide")

st.title("📦 Inventario Almacenes 18 y 19")

archivo = st.file_uploader("Sube tu Excel de inventario", type=["xlsx"])

if archivo:
    # Leemos el excel saltando las primeras 2 filas para llegar a los encabezados
    df = pd.read_excel(archivo, skiprows=2)
    
    busqueda = st.text_input("Ingresa el inicio del código (ej: C0113):").upper()

    if busqueda:
        if 'CODIGO' in df.columns:
            # Filtro sensible: busca códigos que comiencen con el texto
            mascara = df['CODIGO'].astype(str).str.startswith(busqueda)
            seleccionados = df[mascara]
            
            st.write(f"Artículos encontrados: {len(seleccionados)}")
            st.dataframe(seleccionados)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Marcar Almacén 18"):
                    df.loc[mascara, 'Almacen 18'] = datetime.now().strftime("%d/%m/%Y")
                    st.success("✅ Actualizado Alm 18")
            with col2:
                if st.button("Marcar Almacén 19"):
                    df.loc[mascara, 'Almacen 19'] = datetime.now().strftime("%d/%m/%Y")
                    st.success("✅ Actualizado Alm 19")
        else:
            st.error("Error: No se encontró la columna 'CODIGO'. Verifica tu archivo.")

    # Preparar descarga
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Descargar Excel Actualizado",
        data=output.getvalue(),
        file_name="Inventario_Final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
