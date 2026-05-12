import streamlit as st
import math
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Calculadora DIVACO - Medidas Exteriores", page_icon="🛠️")

st.title("🛠️ Calculadora de Plegado (Medidas Exteriores)")
st.markdown("Cálculo preciso de la longitud de corte basado en cotas externas.")

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
tipo_medida = st.radio("Las medidas introducidas son:", ["Exteriores (Cota total)", "Interiores (Tramo recto)"])

num_pliegues = st.number_input("¿Cuántos dobleces tiene?", min_value=1, max_value=10, value=1)

total_rectos_calculados = 0
total_ba = 0
puntos_x = [0]
puntos_y = [0]
angulo_actual = 0 

st.divider()

# Función para ajustar tramos si son medidas exteriores
def ajustar_tramo(valor, radio, espesor, es_punta=False):
    if tipo_medida == "Interiores (Tramo recto)":
        return valor
    # Si es exterior, restamos el Radio y el Espesor para obtener el tramo recto real
    # En las puntas solo se resta una vez, en tramos intermedios se restaría por ambos lados
    return valor - (radio + espesor)

# Primer tramo
l_input_inicial = st.number_input("Longitud Cara Inicial (mm)", min_value=1.0, value=50.0)

# Para el primer dibujo necesitamos el radio del primer pliegue
r_primero = st.session_state.get("rad_0", t)
l_recto_inicial = ajustar_tramo(l_input_inicial, r_primero, t) if tipo_medida == "Exteriores (Cota total)" else l_input_inicial

total_rectos_calculados += l_recto_inicial
puntos_x.append(l_recto_inicial)
puntos_y.append(0)

for i in range(num_pliegues):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        dir_p = st.selectbox(f"Doblado {i+1}", ["Arriba/Der", "Abajo/Izq"], key=f"dir_{i}")
    with col2:
        ang = st.number_input("Ángulo (°)", min_value=1, max_value=170, value=90, key=f"ang_{i}")
    with col3:
        rad = st.number_input("Radio (R)", min_value=0.1, value=t, key=f"rad_{i}")
    with col4:
        l_input_sig = st.number_input("Siguiente Cara (mm)", min_value=1.0, value=50.0, key=f"l_{i}")

    # Cálculo de BA (Fórmula técnica 63277.jpg)
    ba = (ang / 180) * math.pi * (rad + (k_factor * t))
    total_ba += ba
    
    # Ajuste de medida exterior a tramo recto real
    l_recto_sig = ajustar_tramo(l_input_sig, rad, t) if tipo_medida == "Exteriores (Cota total)" else l_input_sig
    total_rectos_calculados += l_recto_sig

    # Geometría para el dibujo
    cambio_ang = ang if "Arriba" in dir_p else -ang
    angulo_actual += cambio_ang
    rad_ang = math.radians(angulo_actual)
    
    nuevo_x = puntos_x[-1] + l_recto_sig * math.cos(rad_ang)
    nuevo_y = puntos_y[-1] + l_recto_sig * math.sin(rad_ang)
    puntos_x.append(nuevo_x)
    puntos_y.append(nuevo_y)

# --- VISUALIZACIÓN ---
st.subheader("Esquema del Perfil")
fig, ax = plt.subplots()
ax.plot(puntos_x, puntos_y, marker='o', color='#1E88E5', linewidth=t+1 if t < 5 else 6)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig)

# --- RESULTADOS ---
st.divider()
longitud_final = total_rectos_calculados + total_ba
st.metric("LONGITUD DE DESARROLLO (CORTE)", f"{longitud_final:.2f} mm")

with st.expander("Ver detalles del cálculo"):
    st.write(f"**Suma de tramos rectos reales:** {total_rectos_calculados:.2f} mm")
    st.write(f"**Tolerancia de doblado total (BA):** {total_ba:.2f} mm")
    st.caption("Nota: El cálculo convierte tus medidas exteriores a la línea neutra para asegurar la precisión.")
