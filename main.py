import streamlit as st
import math
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="DIVACO - Plano de Plegado", page_icon="📏", layout="wide")

st.title("📏 Generador de Plano Acotado para Taller")
st.markdown("Calcula el desarrollo y genera un esquema con medidas exteriores para impresión.")

# --- BARRA LATERAL (CONFIGURACIÓN TÉCNICA) ---
st.sidebar.header("Datos Técnicos")
material = st.sidebar.selectbox("Material", ["Acero Carbono", "Inoxidable", "Aluminio"])
t = st.sidebar.number_input("Espesor (t) mm", min_value=0.1, value=1.0, step=0.1)

# Lógica de Factor K (Referencia 63277.jpg)
if "Carbono" in material: k_factor = 0.33 if t <= 3.0 else 0.45
elif "Inoxidable" in material: k_factor = 0.40
else: k_factor = 0.45

# --- ENTRADA DE MEDIDAS ---
st.header("1. Medidas de la Pieza (Caras Exteriores)")
num_pliegues = st.number_input("Número de dobleces", min_value=1, max_value=10, value=1)

medidas_input = []
total_rectos_reales = 0
total_ba = 0

col_ini = st.columns(2)
l_ini = col_ini[0].number_input("Longitud Cara 1 (Exterior) mm", min_value=1.0, value=50.0)
medidas_input.append(l_ini)

st.write("---")
for i in range(num_pliegues):
    c1, c2, c3, c4 = st.columns(4)
    dir_p = c1.selectbox(f"Sentido {i+1}", ["Arriba", "Abajo"], key=f"d_{i}")
    ang = c2.number_input(f"Ángulo {i+1} (°)", min_value=1, max_value=170, value=90, key=f"a_{i}")
    rad = c3.number_input(f"Radio {i+1} (R)", min_value=0.1, value=t, key=f"r_{i}")
    l_sig = c4.number_input(f"Cara {i+2} (Ext) mm", min_value=1.0, value=50.0, key=f"l_{i}")
    
    medidas_input.append(l_sig)
    
    # Cálculo de BA y tramos rectos reales
    ba = (ang / 180) * math.pi * (rad + (k_factor * t))
    total_ba += ba
    
    # Ajuste de tramos para el cálculo de corte
    total_rectos_reales += (l_sig - (rad + t))
    if i == 0: total_rectos_reales += (l_ini - (rad + t))

# --- GENERACIÓN DEL DIBUJO ACOTADO ---
st.header("2. Esquema de Plegado (Para Imprimir)")

fig, ax = plt.subplots(figsize=(10, 6))
px, py = [0], [0]
ang_acumulado = 0

for i, l_cara in enumerate(medidas_input):
    # Dibujo del tramo
    rad_ang = math.radians(ang_acumulado)
    dx = l_cara * math.cos(rad_ang)
    dy = l_cara * math.sin(rad_ang)
    
    # Dibujar línea de la pieza
    ax.plot([px[-1], px[-1] + dx], [py[-1], py[-1] + dy], color="black", linewidth=3)
    
    # Añadir ACOTACIÓN (Texto con la medida exterior)
    mx, my = px[-1] + dx/2, py[-1] + dy/2
    ax.text(mx, my + 2, f"{l_cara} mm", color="blue", fontsize=10, fontweight='bold', ha='center')
    
    px.append(px[-1] + dx)
    py.append(py[-1] + dy)
    
    if i < num_pliegues:
        # Actualizar ángulo para el siguiente tramo
        sentido = st.session_state[f"d_{i}"]
        ang_giro = st.session_state[f"a_{i}"]
        ang_acumulado += ang_giro if sentido == "Arriba" else -ang_giro

ax.set_aspect('equal')
ax.axis('off') # Quitamos los ejes para que parezca un plano limpio
st.pyplot(fig)

# --- RESULTADO FINAL ---
desarrollo = total_rectos_reales + total_ba
st.success(f"### LONGITUD DE CORTE: {desarrollo:.2f} mm")
st.info("💡 **Consejo de impresión:** Pulsa `Ctrl + P` en tu teclado y selecciona 'Guardar como PDF' o imprime directamente.")
