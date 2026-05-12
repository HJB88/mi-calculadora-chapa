import streamlit as st
import math
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Calculadora de Plegado DIVACO", page_icon="🛠️")

st.title("🛠️ Calculadora con Previsualización de Perfil")
st.markdown("Basada en los parámetros de **DIVACO Tooling**.")

# --- BARRA LATERAL ---
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
else:
    k_factor = 0.45
    r_min = 1.0 * t

st.sidebar.info(f"**Factor K:** {k_factor} | **R mín:** {r_min} mm")

# --- ENTRADA DE DATOS ---
st.header("Definición de la Pieza")
num_pliegues = st.number_input("¿Cuántos dobleces tiene?", min_value=1, max_value=10, value=1)

total_rectos = 0
total_ba = 0
puntos_x = [0]
puntos_y = [0]
angulo_actual = 0  # En grados, acumulado para el dibujo

# Primer tramo
l_inicial = st.number_input("Longitud Tramo Inicial (mm)", min_value=1.0, value=50.0)
total_rectos += l_inicial
puntos_x.append(l_inicial)
puntos_y.append(0)

st.divider()

for i in range(num_pliegues):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        dir_p = st.selectbox(f"Doblado {i+1}", ["Arriba/Der", "Abajo/Izq"], key=f"dir_{i}")
    with col2:
        ang = st.number_input("Ángulo (°)", min_value=1, max_value=170, value=90, key=f"ang_{i}")
    with col3:
        rad = st.number_input("Radio (R)", min_value=0.1, value=t, key=f"rad_{i}")
    with col4:
        l_sig = st.number_input("Sig. Tramo (mm)", min_value=1.0, value=50.0, key=f"l_{i}")

    # Cálculos técnicos (63277.jpg)
    ba = (ang / 180) * math.pi * (rad + (k_factor * t))
    total_ba += ba
    total_rectos += l_sig

    # Lógica para el dibujo (Geometría básica)
    cambio_ang = ang if "Arriba" in dir_p else -ang
    angulo_actual += cambio_ang
    
    rad_ang = math.radians(angulo_actual)
    nuevo_x = puntos_x[-1] + l_sig * math.cos(rad_ang)
    nuevo_y = puntos_y[-1] + l_sig * math.sin(rad_ang)
    
    puntos_x.append(nuevo_x)
    puntos_y.append(nuevo_y)

# --- VISUALIZACIÓN ---
st.subheader("Previsualización del Perfil (Corte Lateral)")
fig, ax = plt.subplots()
ax.plot(puntos_x, puntos_y, marker='o', color='#FF4B4B', linewidth=t+1 if t < 5 else 6)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_xlabel("mm")
ax.set_ylabel("mm")
st.pyplot(fig)

# --- RESULTADOS ---
st.divider()
longitud_final = total_rectos + total_ba
st.metric("LONGITUD TOTAL DE CORTE (L)", f"{longitud_final:.2f} mm")
st.info(f"Suma de tramos rectos: {total_rectos:.2f} mm | Total Bend Allowance: {total_ba:.2f} mm")
