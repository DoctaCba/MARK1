import os
import pandas as pd
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Panteón Social - Fraternidad Laica Dominicana de Córdoba",
    page_icon="🏛️",
    layout="centered"
)

# 1. Cargar el archivo CSV de forma flexible
@st.cache_data
def cargar_datos():
    encodings = ['latin-1', 'cp1252', 'utf-8', 'iso-8859-1']
    delimitadores = [';', ',']
    
    for enc in encodings:
        for sep in delimitadores:
            try:
                df_temp = pd.read_csv("ReportGeneral.csv", sep=sep, encoding=enc, on_bad_lines="skip", low_memory=False)
                if df_temp.shape[1] > 1:
                    # Limpiar espacios en blanco alrededor de los nombres de las columnas
                    df_temp.columns = df_temp.columns.str.strip()
                    return df_temp
            except Exception:
                continue
    return pd.read_csv("ReportGeneral.csv", on_bad_lines="skip")

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")
    st.stop()

# Función para encontrar el nombre exacto de la columna ignorando mayúsculas/espacios
def obtener_columna(df_in, posible_nombre):
    posible_nombre_limpio = posible_nombre.strip().lower().replace(".", "").replace(" ", "")
    for col in df_in.columns:
        col_limpia = str(col).strip().lower().replace(".", "").replace(" ", "")
        if col_limpia == posible_nombre_limpio:
            return col
    return None

# Nombres reales de las columnas en el dataframe cargado
col_num_titular = obtener_columna(df, 'Nro. Titular') or 'Nro. Titular'
col_nicho = obtener_columna(df, 'Nicho') or 'Nicho'
col_titular = obtener_columna(df, 'Titular') or 'Titular'
col_tipo_arrendamiento = obtener_columna(df, 'Tipo Arrendamiento') or 'Tipo Arrendamiento'
col_deuda_arr = obtener_columna(df, 'Deuda Arr') or 'Deuda Arr'
col_deuda_mcl = obtener_columna(df, 'Deuda MCL') or 'Deuda MCL'
col_deuda_total = obtener_columna(df, 'Deuda Total') or 'Deuda Total'

# Limpieza de texto para la búsqueda
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
    
    if num_titular_user and col_num_titular in df_temp.columns:
        coincidencias &= (df_temp[col_num_titular].astype(str).str.strip() == str(num_titular_user).strip())
    
    if nicho_user and col_nicho in df_temp.columns:
        nicho_limpio = limpiar_texto(nicho_user)
        coincidencias &= df_temp[col_nicho].apply(limpiar_texto).str.contains(nicho_limpio, regex=False)
        
    if nombre_titular_user and col_titular in df_temp.columns:
        nombre_limpio = limpiar_texto(nombre_titular_user)
        coincidencias &= df_temp[col_titular].apply(limpiar_texto).str.contains(nombre_limpio, regex=False)
        
    resultado = df_temp[coincidencias]
    
    if resultado.empty:
        return "NO_ENCONTRADO", "No se encontraron registros que coincidan exactamente con los datos ingresados."
        
    return "EXITO", resultado.iloc[0]

# Regla de desvío a Legales/Administración
def procesar_resultado(fila):
    if col_tipo_arrendamiento in fila:
        estado = str(fila.get(col_tipo_arrendamiento, '')).upper()
        if "JURIDICO" in estado or "LEGAL" in estado or "ESTUDIO" in estado:
            return "DESVIAR_WHATSAPP"
    return "MOSTRAR_DEUDA"

# --- ENCABEZADO INSTITUCIONAL ---
col_logo, col_titulo = st.columns([1, 4])

posibles_logos = ["logo.png", "logo.jpg", "logo.jpeg", "LOGO.PNG", "LOGO.JPG"]
logo_encontrado = None
for l in posibles_logos:
    if os.path.exists(l):
        logo_encontrado = l
        break

with col_logo:
    if logo_encontrado:
        st.image(logo_encontrado, width=110)
    else:
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
                st.write(f"**Titular:** {res.get(col_titular, 'N/A')}")
                st.write(f"**N° de Titular:** {res.get(col_num_titular, 'N/A')}")
                st.write(f"**Nicho:** {res.get(col_nicho, 'N/A')}")
            with col_b:
                st.write(f"**Deuda Arrendamiento (ARR):** ${res.get(col_deuda_arr, 0)}")
                st.write(f"**Deuda Mantenimiento (MCL):** ${res.get(col_deuda_mcl, 0)}")
                st.markdown(f"#### **Total a Pagar:** ${res.get(col_deuda_total, 0)}")
            
            st.markdown("---")
            st.warning("⚠️ **Aviso importante:** Los montos mostrados son válidos hasta el **30 de octubre de 2026**.")
            st.info("💳 **Medios de pago habilitados:** Tarjeta de débito, efectivo, transferencia bancaria y pago con QR.\n\n"
                    "📌 *Consulte de lunes a viernes por descuentos especiales por pago contado/transferencia.*")

# AYUDA PARA ENCONTRAR DATOS EN EL RECIBO
with st.expander("❓ ¿Dónde encuentro estos datos en mi recibo físico?"):
    st.write("Consulte en la siguiente imagen de muestra la ubicación exacta de cada dato dentro del comprobante:")
    
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
