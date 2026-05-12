import streamlit as st
import math
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="DIVACO 3D - Plegado Profesional", layout="wide")

st.title("📏 Calculadora de Plegado con Visualización 3D")
st.markdown("Genera el desarrollo de corte y verifica la pieza en un entorno tridimensional.")

# --- DATOS TÉCNICOS ---
st.sidebar.header("Configuración Técnica")
material = st.sidebar.selectbox("Material", ["Acero Carbono", "Inoxidable", "Aluminio"])
t = st.sidebar.number_input("Espesor (t) mm", min_value=0.1, value=1.0)
ancho_pieza = st.sidebar.number_input("Ancho de la pieza (Z) mm", min_value=1.0, value=100.0)

# Factor K (Referencia 63277.jpg)
if "Carbono" in material: k_factor = 0.33 if t <= 3.0 else 0.45
elif "Inoxidable" in material: k_factor = 0.40
else: k_factor = 0.45

# --- ENTRADA DE MEDIDAS ---
st.header("1. Dimensiones Exteriores")
num_pliegues = st.number_input("Número de dobleces", min_value=1, max_value=10, value=1)

medidas_input = []
total_rectos_reales = 0
total_ba = 0

# Primera Cara
l_ini = st.number_input("Longitud Cara 1 (Ext) mm", min_value=1.0, value=50.0)
medidas_input.append(l_ini)

# Definición de pliegues
config_pliegues = []
for i in range(num_pliegues):
    st.write(f"--- Doblez {i+1} ---")
    c1, c2, c3, c4 = st.columns(4)
    dir_p = c1.selectbox("Sentido", ["Arriba", "Abajo"], key=f"d_{i}")
    ang = c2.number_input("Ángulo (°)", min_value=1, max_value=170, value=90, key=f"a_{i}")
    rad = c3.number_input("Radio (R)", min_value=0.1, value=t, key=f"r_{i}")
    l_sig = c4.number_input("Siguiente Cara (Ext) mm", min_value=1.0, value=50.0, key=f"l_{i}")
    
    medidas_input.append(l_sig)
    config_pliegues.append({'dir': dir_p, 'ang': ang, 'rad': rad})
    
    # Cálculo técnico para longitud de corte (Referencia 63277.jpg)
    ba = (ang / 180) * math.pi * (rad + (k_factor * t))
    total_ba += ba
    total_rectos_reales += (l_sig - (rad + t))
    if i == 0: total_rectos_reales += (l_ini - (rad + t))

# --- GENERACIÓN DE COORDENADAS 3D ---
x, y = [0, medidas_input[0]], [0, 0]
ang_acumulado = 0

for i in range(num_pliegues):
    giro = config_pliegues[i]['ang'] if config_pliegues[i]['dir'] == "Arriba" else -config_pliegues[i]['ang']
    ang_acumulado += giro
    rad_ang = math.radians(ang_acumulado)
    
    x.append(x[-1] + medidas_input[i+1] * math.cos(rad_ang))
    y.append(y[-1] + medidas_input[i+1] * math.sin(rad_ang))

# --- VISUALIZACIÓN 3D (PLOTLY) ---
st.header("2. Modelo 3D Interactivo")
fig_3d = go.Figure()

# Creamos las dos caras del ancho de la pieza para dar volumen
for z_pos in [0, ancho_pieza]:
    fig_3d.add_trace(go.Scatter3d(x=x, y=y, z=[z_pos]*len(x), mode='lines', line=dict(color='silver', width=5)))

# Unimos las caras para crear el sólido
for i in range(len(x)):
    fig_3d.add_trace(go.Scatter3d(x=[x[i], x[i]], y=[y[i], y[i]], z=[0, ancho_pieza], mode='lines', line=dict(color='gray', width=2)))

fig_3d.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0))
st.plotly_chart(fig_3d, use_container_width=True)

# --- RESULTADO FINAL ---
desarrollo = total_rectos_reales + total_ba
st.success(f"### LONGITUD DE CORTE NECESARIA: {desarrollo:.2f} mm")
