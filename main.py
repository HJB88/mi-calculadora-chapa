import streamlit as st
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Desarrollo Bandeja 4 Lados", layout="wide")

st.title("📏 Desarrollo de Chapa: Bandeja 4 Lados")
st.markdown("Calcula el corte de chapa para piezas con plegados en todo el perímetro.")

# --- PARÁMETROS TÉCNICOS (Basados en DIVACO Tooling) ---
st.sidebar.header("Parámetros del Material")
t = st.sidebar.number_input("Espesor (t) mm", min_value=0.1, value=1.5, step=0.1)
material = st.sidebar.selectbox("Material", ["Acero Carbono", "Inoxidable", "Aluminio"])

# Lógica de Factor K (Referencia 63277.jpg)
if "Carbono" in material: k_factor = 0.33 if t <= 3.0 else 0.45
elif "Inoxidable" in material: k_factor = 0.40
else: k_factor = 0.45

# --- EJE X (LARGO) ---
st.header("1. Desarrollo Longitudinal (Largo)")
num_x = st.number_input("Nº de pliegues por cada lado del largo", min_value=1, max_value=5, value=1)
base_x = st.number_input("Base central (Largo exterior) mm", value=200.0)

ba_total_x = 0
rectos_x = base_x - 2*(t + t) # Ajuste base inicial aproximado

for i in range(int(num_x)):
    col1, col2 = st.columns(2)
    alt = col1.number_input(f"Altura Pestaña X{i+1} (mm)", value=20.0, key=f"lx_{i}")
    rad = col2.number_input(f"Radio R{i+1} (mm)", value=t, key=f"rx_{i}")
    
    ba = (90 / 180) * math.pi * (rad + (k_factor * t))
    ba_total_x += ba * 2 # Dos lados
    rectos_x += (alt - (rad + t)) * 2

# --- EJE Z (ANCHO) ---
st.header("2. Desarrollo Transversal (Ancho)")
num_z = st.number_input("Nº de pliegues por cada lado del ancho", min_value=1, max_value=5, value=1)
base_z = st.number_input("Base central (Ancho exterior) mm", value=100.0)

ba_total_z = 0
rectos_z = base_z - 2*(t + t)

for i in range(int(num_z)):
    col1, col2 = st.columns(2)
    alt_z = col1.number_input(f"Altura Pestaña Z{i+1} (mm)", value=20.0, key=f"lz_{i}")
    rad_z = col2.number_input(f"Radio Rz{i+1} (mm)", value=t, key=f"rz_{i}")
    
    ba_z = (90 / 180) * math.pi * (rad_z + (k_factor * t))
    ba_total_z += ba_z * 2
    rectos_z += (alt_z - (rad_z + t)) * 2

# --- RESULTADOS ---
st.divider()
total_x = rectos_x + ba_total_x
total_z = rectos_z + ba_total_z

# --- DIBUJO DEL DESARROLLO (PLANO DE CORTE) ---
st.header("3. Plano de Desarrollo (Corte Laser/Cizalla)")

fig, ax = plt.subplots(figsize=(8, 6))
# Dibujo de la chapa plana total
rect = plt.Rectangle((0, 0), total_x, total_z, linewidth=2, edgecolor='black', facecolor='#e3f2fd')
ax.add_patch(rect)

# Líneas de plegado (Esquema simplificado)
ax.axvline(x=total_x*0.15, color='red', linestyle='--')
ax.axvline(x=total_x*0.85, color='red', linestyle='--')
ax.axhline(y=total_z*0.15, color='red', linestyle='--')
ax.axhline(y=total_z*0.85, color='red', linestyle='--')

ax.text(total_x/2, total_z + 5, f"LARGO TOTAL: {total_x:.2f} mm", ha='center', fontweight='bold', color='blue')
ax.text(-15, total_z/2, f"ANCHO TOTAL: {total_z:.2f} mm", va='center', rotation=90, fontweight='bold', color='blue')

ax.set_xlim(-30, total_x + 30)
ax.set_ylim(-30, total_z + 30)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)

st.success(f"### Medida final de la chapa: {total_x:.2f} x {total_z:.2f} mm")
st.info("Este cálculo descuenta automáticamente el espesor y radio en los 4 costados.")
