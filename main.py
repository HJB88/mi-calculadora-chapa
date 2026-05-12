import streamlit as st
import math
import plotly.graph_objects as go

st.set_page_config(page_title="DIVACO 3D Multi-Eje", layout="wide")

st.title("🛠️ Calculadora 3D: Pliegues en X y Z")
st.markdown("Calcula el desarrollo total para piezas con pestañas en ambos ejes.")

# --- CONFIGURACIÓN TÉCNICA ---
st.sidebar.header("Material y Espesor")
material = st.sidebar.selectbox("Material", ["Acero Carbono", "Inoxidable", "Aluminio"])
t = st.sidebar.number_input("Espesor (t) mm", min_value=0.1, value=1.0)

# Factor K (Referencia 63277.jpg)
if "Carbono" in material: k_factor = 0.33 if t <= 3.0 else 0.45
elif "Inoxidable" in material: k_factor = 0.40
else: k_factor = 0.45

# --- EJE X (Perfil Principal) ---
st.header("1. Pliegues Perfil Principal (Eje X)")
num_x = st.number_input("Número de dobleces en X", min_value=1, max_value=10, value=1)
l_ini_x = st.number_input("Largo Cara Inicial (mm)", value=50.0)

rectos_x = l_ini_x
ba_total_x = 0
coords_x, coords_y = [0, l_ini_x], [0, 0]
ang_acum_x = 0

for i in range(int(num_x)):
    c1, c2, c3 = st.columns(3)
    ang = c1.number_input(f"Ángulo X{i+1}", value=90.0, key=f"ax_{i}")
    rad = c2.number_input(f"Radio X{i+1}", value=t, key=f"rx_{i}")
    l_sig = c3.number_input(f"Cara X{i+2} (mm)", value=50.0, key=f"lx_{i}")
    
    # Cálculos X (Referencia 63277.jpg)
    ba = (ang / 180) * math.pi * (rad + (k_factor * t))
    ba_total_x += ba
    rectos_x += (l_sig - (rad + t))
    
    ang_acum_x += ang
    rad_ang = math.radians(ang_acum_x)
    coords_x.append(coords_x[-1] + l_sig * math.cos(rad_ang))
    coords_y.append(coords_y[-1] + l_sig * math.sin(rad_ang))

# --- EJE Z (Pestañas Laterales) ---
st.header("2. Pliegues Laterales (Eje Z)")
ancho_base = st.number_input("Ancho Base (Z) mm", value=100.0)
num_z = st.number_input("¿Pestañas laterales?", min_value=0, max_value=2, step=1)

rectos_z = ancho_base
ba_total_z = 0

if num_z > 0:
    c_z1, c_z2 = st.columns(2)
    l_pestaña = c_z1.number_input("Largo de Pestaña (mm)", value=20.0)
    rad_z = c_z2.number_input("Radio Pestaña (mm)", value=t)
    
    # Calculamos para las pestañas (se multiplica por el número de pestañas)
    ba_z = (90 / 180) * math.pi * (rad_z + (k_factor * t))
    ba_total_z = ba_z * num_z
    rectos_z += (l_pestaña - (rad_z + t)) * num_z

# --- RESULTADOS Y 3D ---
st.divider()
des_x = rectos_x + ba_total_x
des_z = rectos_z + ba_total_z

st.success(f"### DIMENSIONES DE CORTE: {des_x:.2f} mm x {des_z:.2f} mm")

# Visualización 3D básica
fig = go.Figure()
for z_p in [0, ancho_base]:
    fig.add_trace(go.Scatter3d(x=coords_x, y=coords_y, z=[z_p]*len(coords_x), mode='lines', line=dict(color='blue', width=4)))
fig.update_layout(scene=dict(aspectmode='data'))
st.plotly_chart(fig, use_container_width=True)
