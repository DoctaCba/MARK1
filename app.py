import os
import pandas as pd
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Panteón Social - Fraternidad Laica Dominicana de Córdoba",
    page_icon="🏛️",
    layout="centered"
)

# 1. Cargar el archivo CSV
try:
    df = pd.read_csv("ReportGeneral.csv", sep=";")
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
        return "ERROR_CAMPOS", "Por favor, ingrese al menos 2 de los 3 datos requeridos para realizar la consulta."
    
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
        return "NO_ENCONTRADO", "No se encontraron registros que coincidan exactamente con los datos ingresados."
        
    return "EXITO", resultado.iloc[0]

# Regla de desvío a Legales/Administración
def procesar_resultado(fila):
    estado = str(fila.get('Tipo Arrendamiento', '')).upper()
    if "JURIDICO" in estado or "LEGAL" in estado or "ESTUDIO" in estado:
        return "DESVIAR_WHATSAPP"
    return "MOSTRAR_DEUDA"

# --- ENCABEZADO INSTITUCIONAL ---
col_logo, col_titulo = st.columns([1, 4])

# Búsqueda inteligente de imagen de logo local
posibles_logos = ["Logo.png", "logo.jpg", "logo.jpeg", "LOGO.PNG", "LOGO.JPG"]
logo_encontrado = None

for l in posibles_logos:
    if os.path.exists(l):
        logo_encontrado = l
        break

with col_logo:
    if logo_encontrado:
        st.image(logo_encontrado, width=110)
    else:
        # Respaldo web si no subiste aún el logo.png
        url_escudo = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Dominican_Order_coat_of_arms.svg/300px-Dominican_Order_coat_of_arms.svg.png"
        st.image(url_escudo, width=110)

with col_titulo:
    st.markdown("## **Fraternidad Laica Dominicana de Córdoba**")
    st.markdown("### 🏛️ *Panteón Social - Consulta de Estado de Cuenta*")

st.success("🏛️ **Portal Web Oficial de Consultas** — Panteón Social Fraternidad Laica Dominicana de Córdoba")
st.markdown("---")

# --- GUÍA PASO A PASO PARA EL USUARIO ---
st.subheader("📋 Complete los datos para consultar su cuenta")
st.caption("Para proteger sus datos y validar su identidad, **ingrese al menos 2 de los 3 datos** requeridos:")

col1, col2, col3 = st.columns(3)
with col1:
    titular_num_in = st.text_input("1. N° de Titular", help="Ejemplo: 1234")
with col2:
    nicho_in = st.text_input("2. Ubicación de Nicho", help="Ejemplo: 01 B 016 8")
with col3:
    titular_nom_in = st.text_input("3. Nombre / Apellido", help="Apellido o nombre del titular")

# Botón de consulta
if st.button("🔍 CONSULTAR MI CUENTA", use_container_width=True, type="primary"):
    estado, res = consultar_deuda(titular_num_in, nicho_in, titular_nom_in)
    
    if estado in ["ERROR_CAMPOS", "NO_ENCONTRADO"]:
        st.error(res)
        st.info("💡 **¿Necesita ayuda?** Si los datos no coinciden o tiene dudas, puede comunicarse directamente con la Administración.")
    elif estado == "EXITO":
        accion = procesar_resultado(res)
        
        if accion == "DESVIAR_WHATSAPP":
            st.warning("⚠️ **Atención:** La cuenta seleccionada posee una condición especial de gestión.")
            st.info("Para consultar el saldo y regularizar la situación, por favor comuníquese directamente con la Administración.")
            st.markdown("[📲 Contactar a la Administración por WhatsApp](https://wa.me/5493518739308?text=Hola,%20quisiera%20consultar%20por%20mi%20cuenta)")
        else:
            st.success("✅ **Cuenta verificada con éxito**")
            
            st.markdown("### 📄 Detalle de la Cuenta")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Titular:** {res['Titular']}")
                st.write(f"**N° de Titular:** {res['Nro. Titular']}")
                st.write(f"**Nicho:** {res['Nicho']}")
            with col_b:
                st.write(f"**Deuda Arrendamiento (ARR):** ${res.get('Deuda Arr', 0)}")
                st.write(f"**Deuda Mantenimiento (MCL):** ${res.get('Deuda MCL', 0)}")
                st.markdown(f"#### **Total a Pagar:** ${res.get('Deuda Total', 0)}")
            
            st.markdown("---")
            st.warning("⚠️ **Aviso importante:** Los montos mostrados son válidos hasta el **30 de octubre de 2026**.")
            st.info("💳 **Medios de pago habilitados:** Tarjeta de débito, efectivo, transferencia bancaria y pago con QR.\n\n"
                    "📌 *Consulte de lunes a viernes por descuentos especiales por pago contado/transferencia.*")

# AYUDA PARA ENCONTRAR DATOS EN EL RECIBO
with st.expander("❓ ¿Dónde encuentro estos datos en mi recibo físico?"):
    st.write("Consulte en la siguiente imagen de muestra la ubicación exacta de cada dato dentro del comprobante:")
    
    # Búsqueda flexible de la imagen del recibo
    posibles_recibos = [
        "MUESTRA-RECIBO.JPG", "muestra-recibo.jpg", "MUESTRA-RECIBO.jpg", 
        "muestra-recibo.png", "MUESTRA-RECIBO.PNG", "muestra_recibo.png"
    ]
    
    recibo_encontrado = None
    for r in posibles_recibos:
        if os.path.exists(r):
            recibo_encontrado = r
            break

    if recibo_encontrado:
        st.image(recibo_encontrado, caption="Ubicación de datos en el recibo de muestra", use_container_width=True)
    else:
        st.warning("⚠️ No se encontró la imagen del recibo. Asegúrese de que el archivo esté subido en GitHub.")

# PIE DE PÁGINA INSTITUCIONAL
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #555555; font-size: 0.9em;'>
        <p><b>Administración Panteón Social Fraternidad Laica Dominicana de Córdoba</b><br>
        Córdoba, Argentina | Atención presencial y telefónica de lunes a viernes.<br>
        <i>Portal Web de Consulta Segura</i></p>
    </div>
    """, 
    unsafe_allow_html=True
)
