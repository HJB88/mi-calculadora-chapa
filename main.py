import streamlit as st
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Desarrollo Multi-Plegado", layout="wide")

st.title("📏 Plano de Desarrollo: Multi-Plegado")
st.markdown("Calcula la chapa plana para piezas con múltiples dobleces consecutivos.")

# --- BARRA LATERAL ---
st.sidebar.header("Parámetros del Material")
t = st.sidebar.number_input("Espesor (t) mm", min_value=0.1, value=1.5, step=0.1)
material = st.sidebar.selectbox("Material", ["Acero Carbono", "Inoxidable", "Aluminio"])
ancho_z = st.sidebar.number_input("Ancho de la pieza (mm)", min_value=1.0, value=100.0)

# Factor K según tus tablas (63277.jpg)
if "Carbono" in material: k_factor = 0.33 if t <= 3.0 else 0.45
elif "Inoxidable" in material: k_factor = 0.40
else: k_factor = 0.45

# --- ENTRADA DE DATOS ---
st.header("1. Definición de la Pieza (Cotas Exteriores)")
num_pliegues = st.number_input("¿Cuántos dobleces tiene?", min_value=1, max_value=15, value=2)

caras_exteriores = []
pliegues_data = []

# Cara inicial
l1_ext = st.number_input("Longitud Cara 1 (Ext) mm", value=40.0)
caras_exteriores.append(l1_ext)

st.write("---")
for i in range(int(num_pliegues)):
    c1, c2, c3 = st.columns(3)
    ang = c1.number_input(f"Ángulo {i+1} (°)", value=90, key=f"ang_{i}")
    rad = c2.number_input(f"Radio R{i+1} (mm)", value=t, key=f"rad_{i}")
    l_sig = c3.number_input(f"Siguiente Cara {i+2} (Ext) mm", value=40.0, key=f"l_{i}")
    
    caras_exteriores.append(l_sig)
    pliegues_data.append({'ang': ang, 'rad': rad})

# --- CÁLCULO TÉCNICO ---
tramos_reales = []
ba_valores = []
posiciones_pliegue = [] # Para el dibujo
desarrollo_total = 0

# Procesamos cada pliegue y cara
for i in range(int(num_pliegues)):
    ang = pliegues_data[i]['ang']
    rad = pliegues_data[i]['rad']
    
    # Tolerancia de doblado (Fórmula 63277.jpg)
    ba = (ang / 180) * math.pi * (rad + (k_factor * t))
    ba_valores.append(ba)
    
    # Tramo recto real (descontando R y t de las caras exteriores)
    if i == 0:
        # Primer tramo recto
        recto = caras_exteriores[i] - (rad + t)
        tramos_reales.append(recto)
        posiciones_pliegue.append(recto + ba/2)
        desarrollo_total += recto + ba
    else:
        # Tramos intermedios (descuentan por ambos lados)
        recto = caras_exteriores[i] - 2*(rad + t)
        tramos_reales.append(recto)
        # La posición es el acumulado anterior + el tramo + mitad del BA actual
        posiciones_pliegue.append(desarrollo_total + recto + ba/2)
        desarrollo_total += recto + ba

# Último tramo recto
ultimo_recto = caras_exteriores[-1] - (pliegues_data[-1]['rad'] + t)
tramos_reales.append(ultimo_recto)
desarrollo_total += ultimo_recto

# --- DIBUJO DEL PLANO ---
st.header("2. Plano de Trazado para Corte y Marcado")

fig, ax = plt.subplots(figsize=(12, 5))

# Dibujo de la chapa plana
rect = plt.Rectangle((0, 0), desarrollo_total, ancho_z, linewidth=2, edgecolor='black', facecolor='#f0f0f0')
ax.add_patch(rect)

# Dibujar cada línea de plegado
for pos in posiciones_pliegue:
    ax.axvline(x=pos, color='red', linestyle='--', alpha=0.7)
    ax.text(pos, ancho_z + 2, f"{pos:.1f}", color='red', fontsize=8, ha='center', rotation=45)

# Acotación total
ax.text(desarrollo_total/2, -15, f"LARGO DE DESARROLLO: {desarrollo_total:.2f} mm", 
        ha='center', fontsize=12, color='blue', fontweight='bold')
ax.text(-10, ancho_z/2, f"{ancho_z} mm", va='center', rotation=90, fontweight='bold')

ax.set_xlim(-20, desarrollo_total + 20)
ax.set_ylim(-30, ancho_z + 30)
ax.set_aspect('equal')
ax.axis('off')

st.pyplot(fig)

# --- RESUMEN ---
st.success(f"### Longitud de Corte: {desarrollo_total:.2f} mm")
st.info("💡 **Las líneas rojas punteadas** indican la posición de marcado desde el borde izquierdo (0).")
