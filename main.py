import streamlit as st
import math

# Configuración de la página
st.set_page_config(page_title="Calculadora de Plegado DIVACO", page_icon="🛠️")

st.title("🛠️ Calculadora de Desplegado de Chapa")
st.markdown("Basada en los parámetros esenciales de **DIVACO Tooling**.")

# --- BARRA LATERAL: CONFIGURACIÓN BASE ---
st.sidebar.header("Configuración del Material")
material = st.sidebar.selectbox(
    "Selecciona el Material",
    ["Acero al Carbono / Galvanizado", "Acero Inoxidable (304)", "Aluminio (1060)"]
)

t = st.sidebar.number_input("Espesor (t) en mm", min_value=0.1, max_value=20.0, value=1.0, step=0.1)

# Lógica de Factor K y Radio Mínimo (Referencia 63277.jpg y 63275.jpg)
if "Acero al Carbono" in material:
    k_factor = 0.33 if t <= 3.0 else 0.45
    r_min = 0.5 * t if t <= 1.0 else 1.0 * t
elif "Inoxidable" in material:
    k_factor = 0.40
    r_min = 1.0 * t
else: # Aluminio
    k_factor = 0.45
    r_min = 1.0 * t

st.sidebar.info(f"**Factor K asignado:** {k_factor}\n\n**Radio mín. sugerido:** {r_min} mm")

# --- CUERPO PRINCIPAL: ENTRADA DE PLIEGUES ---
st.header("Definición de la Pieza")
num_pliegues = st.number_input("¿Cuántos dobleces tiene la pieza?", min_value=1, max_value=10, value=1)

total_rectos = 0
total_ba = 0

st.subheader("Dimensiones de los tramos y pliegues")

# Primer tramo recto
l_inicial = st.number_input("Longitud Tramo Inicial (mm)", min_value=0.0, value=50.0)
total_rectos += l_inicial

# Generar entradas dinámicas para cada pliegue
for i in range(num_pliegues):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.write(f"**Doblez {i+1}**")
        dir_p = st.selectbox("Dirección", ["Derecha/Arriba", "Izquierda/Abajo"], key=f"dir_{i}")
    
    with col2:
        ang = st.number_input("Ángulo (°)", min_value=1, max_value=179, value=90, key=f"ang_{i}")
        
    with col3:
        rad = st.number_input("Radio (R) mm", min_value=0.1, value=t, key=f"rad_{i}")
        if rad < r_min:
            st.warning("R muy bajo")
            
    with col4:
        l_sig = st.number_input("Siguiente Tramo (mm)", min_value=0.0, value=50.0, key=f"l_{i}")
        total_rectos += l_sig

    # Cálculo de BA (Fórmula 63277.jpg)
    ba = (ang / 180) * math.pi * (rad + (k_factor * t))
    total_ba += ba

# --- RESULTADO FINAL ---
st.divider()
longitud_final = total_rectos + total_ba

c1, c2 = st.columns(2)
c1.metric("Longitud de Corte Total", f"{longitud_final:.2f} mm")
c2.metric("Suma de Tolerancias (BA)", f"{total_ba:.2f} mm")

if st.button("Generar Hoja de Ruta"):
    st.success(f"Corta una chapa de {longitud_final:.2f} mm de largo para empezar.")
    st.write("Sigue la secuencia de plegado según las direcciones indicadas arriba.")