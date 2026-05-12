import streamlit as st
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Plano de Desarrollo 2D", layout="wide")

st.title("📏 Plano de Desarrollo (Chapa Plana)")
st.markdown("Genera las medidas de corte y las líneas de marcado para el taller.")

# --- BARRA LATERAL ---
st.sidebar.header("Parámetros Técnicos")
t = st.sidebar.number_input("Espesor (t) mm", min_value=0.1, value=1.5)
material = st.sidebar.selectbox("Material", ["Acero Carbono", "Inoxidable", "Aluminio"])

# Lógica Factor K (Referencia 63277.jpg)
if "Carbono" in material: k_factor = 0.33 if t <= 3.0 else 0.45
elif "Inoxidable" in material: k_factor = 0.40
else: k_factor = 0.45

# --- CÁLCULO EJE X (Perfil) ---
st.header("1. Desarrollo Longitudinal (Eje X)")
c1, c2 = st.columns(2)
l1_ext = c1.number_input("Ala inicial exterior (mm)", value=30.0)
l2_ext = c2.number_input("Ala final exterior (mm)", value=30.0)
base_x_ext = st.number_input("Base central exterior (mm)", value=100.0)
r_x = st.number_input("Radio de doblado en X", value=t)

# Cálculo de BA y tramos reales
ba_x = (90 / 180) * math.pi * (r_x + (k_factor * t))
recto_ala1 = l1_ext - (r_x + t)
recto_base_x = base_x_ext - 2*(r_x + t)
recto_ala2 = l2_ext - (r_x + t)

desarrollo_x = recto_ala1 + recto_base_x + recto_ala2 + 2*ba_x

# --- CÁLCULO EJE Z (Ancho) ---
st.header("2. Desarrollo Transversal (Eje Z)")
ancho_base_ext = st.number_input("Ancho base exterior (mm)", value=80.0)
ala_z_ext = st.number_input("Altura pestañas laterales (mm)", value=20.0)
r_z = st.number_input("Radio de doblado en Z", value=t)

ba_z = (90 / 180) * math.pi * (r_z + (k_factor * t))
recto_base_z = ancho_base_ext - 2*(r_z + t)
recto_ala_z = ala_z_ext - (r_z + t)

desarrollo_z = recto_ala_z + recto_base_z + recto_ala_z + 2*ba_z

# --- DIBUJO DEL PLANO DE DESARROLLO ---
st.header("3. Plano de Corte y Marcado")

fig, ax = plt.subplots(figsize=(10, 6))

# Dibujo del contorno de la chapa plana
rect = plt.Rectangle((0, 0), desarrollo_x, desarrollo_z, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(rect)

# Líneas de plegado en X (verticales)
pos_p1_x = recto_ala1 + ba_x/2
pos_p2_x = desarrollo_x - (recto_ala2 + ba_x/2)
ax.axvline(x=pos_p1_x, color='red', linestyle='--', label='Líneas de pliegue')
ax.axvline(x=pos_p2_x, color='red', linestyle='--')

# Líneas de plegado en Z (horizontales)
pos_p1_z = recto_ala_z + ba_z/2
pos_p2_z = desarrollo_z - (recto_ala_z + ba_z/2)
ax.axhline(y=pos_p1_z, color='red', linestyle='--')
ax.axhline(y=pos_p2_z, color='red', linestyle='--')

# Acotación del total
ax.text(desarrollo_x/2, desarrollo_z + 5, f"LARGO TOTAL: {desarrollo_x:.2f} mm", ha='center', fontsize=12, color='blue', fontweight='bold')
ax.text(-10, desarrollo_z/2, f"ANCHO TOTAL: {desarrollo_z:.2f} mm", va='center', rotation=90, fontsize=12, color='blue', fontweight='bold')

ax.set_xlim(-20, desarrollo_x + 20)
ax.set_ylim(-20, desarrollo_z + 20)
ax.set_aspect('equal')
ax.axis('off')

st.pyplot(fig)

st.success(f"### MEDIDA DE CORTE: {desarrollo_x:.2f} x {desarrollo_z:.2f} mm")
st.info("Las líneas rojas punteadas indican el centro de la zona de doblado (donde baja el punzón).")
