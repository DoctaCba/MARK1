import os
import pandas as pd
import streamlit as st

# 1. Cargar el archivo CSV (se lee directamente de la carpeta de GitHub)
try:
    df = pd.read_csv("ReportGeneral.csv", sep=":")
except Exception:
    df = pd.read_csv("ReportGeneral.csv")

# Limpieza de texto
def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    return str(texto).strip().upper().replace(",", "").replace(".", "")

# Lógica de búsqueda "2 de 3"
def consultar_deuda(num_titular_user, nicho_user, nombre_titular_user):
    campos_ingresados = sum([bool(num_titular_user), bool(nicho_user), bool(nombre_titular_user)])
    
    if campos_ingresados < 2:
        return "ERROR_CAMPOS", "Por favor, ingrese al menos 2 de los 3 datos requeridos para consultar."
    
    df_temp = df.copy()
    coincidencias = pd.Series([True] * len(df_temp))
    
    if num_titular_user:
        coincidencias &= (df_temp['Nro. Titular'].astype(str).str.strip() == str(num_titular_user).strip())
    
    if nicho_user:
        nicho_limpio = limpiar_texto(nicho_user)
        coincidencias &= df_temp['Nicho'].apply(limpiar_texto).str.contains(nicho_limpio, regex=False)
        
    if nombre_titular_user:
        nombre_limpio = limpiar_texto(nombre_titular_user)
        coincidencias &= df_temp['Titular'].apply(limpiar_texto).str.contains(nombre_limpio, regex=False)
        
    resultado = df_temp[coincidencias]
    
    if resultado.empty:
        return "NO_ENCONTRADO", "No se encontraron registros que coincidan con los datos ingresados."
        
    return "EXITO", resultado.iloc[0]

# Regla de desvío a Legales/Administración
def procesar_resultado(fila):
    estado = str(fila.get('Tipo Arrendamiento', '')).upper()
    if "JURIDICO" in estado or "LEGAL" in estado or "ESTUDIO" in estado:
        return "DESVIAR_WHATSAPP"
    return "MOSTRAR_DEUDA"

# Interfaz en Streamlit
st.set_page_config(page_title="MARK 1 - Consulta de Deuda", page_icon="📄")
st.title("🏛️ Consulta de Estado de Cuenta y Deuda")
st.write("Ingrese al menos 2 de los 3 datos requeridos para validar su cuenta.")

with st.expander("❓ ¿Dónde encuentro estos datos en mi recibo?"):
    st.info("Consulte la ubicación de los datos en su comprobante o factura:")
    ruta_imagen = "muestra_recibo.png"
    if os.path.exists(ruta_imagen):
        st.image(ruta_imagen, caption="Ubicación de datos en el recibo de muestra")

col1, col2, col3 = st.columns(3)
with col1:
    titular_num_in = st.text_input("N° de Titular")
with col2:
    nicho_in = st.text_input("Nicho (Ej: 01 B 016 8)")
with col3:
    titular_nom_in = st.text_input("Nombre / Apellido Titular")

if st.button("Consultar Deuda"):
    estado, res = consultar_deuda(titular_num_in, nicho_in, titular_nom_in)
    
    if estado in ["ERROR_CAMPOS", "NO_ENCONTRADO"]:
        st.error(res)
        st.warning("Si no encuentra sus datos o tiene dudas, comuníquese con la Administración.")
    elif estado == "EXITO":
        accion = procesar_resultado(res)
        
        if accion == "DESVIAR_WHATSAPP":
            st.warning("⚠️ La cuenta seleccionada posee una condición especial.")
            st.info("Para consultar el estado de esta cuenta, por favor comuníquese directamente con la Administración.")
            st.markdown("[📲 Contactar por WhatsApp](https://wa.me/5493518739308?text=Hola,%20quisiera%20consultar%20por%20mi%20cuenta)")
        else:
            st.success("✅ Cuenta verificada con éxito")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Titular:** {res['Titular']}")
                st.write(f"**N° de Titular:** {res['Nro. Titular']}")
                st.write(f"**Nicho:** {res['Nicho']}")
            with col_b:
                st.write(f"**Deuda Arrendamiento (ARR):** ${res.get('Deuda Arr', 0)}")
                st.write(f"**Deuda Mantenimiento (MCL):** ${res.get('Deuda MCL', 0)}")
                st.markdown(f"### **Total a Pagar:** ${res.get('Deuda Total', 0)}")
            
            st.markdown("---")
            st.warning("⚠️ **Aviso importante:** Los montos mostrados son válidos hasta el **30 de octubre de 2026**.")
            st.info("💳 **Medios de pago habilitados:** Tarjeta de débito, efectivo, transferencia bancaria y pago con QR.\n\n"
                    "📌 *Consulte de lunes a viernes por descuentos especiales por pago contado/transferencia.*")
