import streamlit as st
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Plano de Trazado Completo", layout="wide")

st.title("📏 Plano de Desarrollo Perimetral con Trazado")
st.markdown("Genera el rectángulo de corte y todas las líneas de marcado para piezas asimétricas.")

# --- PARÁMETROS TÉCNICOS (DIVACO) ---
st.sidebar.header("Material y Espesor")
t = st.sidebar.number_input("Espesor (t) mm", min_value=0.1, value=1.5, step=0.1)
material = st.sidebar.selectbox("Material", ["Acero Carbono", "Inoxidable", "Aluminio"])

if "Carbono" in material: k_factor = 0.33 if t <= 3.0 else 0.45
elif "Inoxidable" in material: k_factor = 0.40
else: k_factor = 0.45

def calcular_detalles_lado(nombre_lado, key_suffix):
    st.subheader(f"Lado {nombre_lado}")
    n = st.number_input(f"Nº pliegues {nombre_lado}", 0, 5, 1, key=f"n_{key_suffix}")
    desarrollos = []
    for i in range(n):
        c1, c2 = st.columns(2)
        alt = c1.number_input(f"Altura {i+1}", value=20.0, key=f"l_{key_suffix}_{i}")
        rad = c2.number_input(f"Radio {i+1}", value=t, key=f"r_{key_suffix}_{i}")
        ba = (90 / 180) * math.pi * (rad + (k_factor * t))
        # Guardamos el tramo recto y el BA para posicionar las líneas
        desarrollos.append({'recto': alt - (rad + t), 'ba': ba})
    return desarrollos

# --- ENTRADA DE DATOS ---
col1, col2 = st.columns(2)
with col1:
    base_x = st.number_input("Base central (Largo) mm", value=200.0)
    data_izq = calcular_detalles_lado("Izquierdo (Oeste)", "izq")
    data_der = calcular_detalles_lado("Derecho (Este)", "der")

with col2:
    base_z = st.number_input("Base central (Ancho) mm", value=100.0)
    data_sup = calcular_detalles_lado("Superior (Norte)", "sup")
    data_inf = calcular_detalles_lado("Inferior (Sur)", "inf")

# --- CÁLCULO DE POSICIONES ---
des_izq_total = sum(d['recto'] + d['ba'] for d in data_izq)
des_der_total = sum(d['recto'] + d['ba'] for d in data_der)
des_inf_total = sum(d['recto'] + d['ba'] for d in data_inf)
des_sup_total = sum(d['recto'] + d['ba'] for d in data_sup)

largo_total = des_izq_total + base_x + des_der_total
ancho_total = des_inf_total + base_z + des_sup_total

# --- DIBUJO ---
st.divider()
fig, ax = plt.subplots(figsize=(12, 8))

# Chapa base
ax.add_patch(plt.Rectangle((0, 0), largo_total, ancho_total, facecolor='#f8f9fa', edgecolor='black', lw=2))

# Líneas Verticales (Plegados Izquierda y Derecha)
acum = 0
for i, d in enumerate(data_izq):
    acum += d['recto'] + d['ba']/2
    ax.axvline(x=acum, color='red', linestyle='--', lw=1)
    ax.text(acum, -5, f"V{i+1}", color='red', ha='center', fontsize=8)
    acum += d['ba']/2

# Desde el otro lado (Derecha)
acum = largo_total
for i, d in enumerate(data_der):
    acum -= (d['recto'] + d['ba']/2)
    ax.axvline(x=acum, color='red', linestyle='--', lw=1)
    ax.text(acum, -5, f"V_der{i+1}", color='red', ha='center', fontsize=8)
    acum -= d['ba']/2

# Líneas Horizontales (Plegados Inferior y Superior)
acum = 0
for i, d in enumerate(data_inf):
    acum += d['recto'] + d['ba']/2
    ax.axhline(y=acum, color='blue', linestyle='--', lw=1)
    ax.text(-10, acum, f"H{i+1}", color='blue', va='center', fontsize=8)
    acum += d['ba']/2

acum = ancho_total
for i, d in enumerate(data_sup):
    acum -= (d['recto'] + d['ba']/2)
    ax.axhline(y=acum, color='blue', linestyle='--', lw=1)
    ax.text(-10, acum, f"H_sup{i+1}", color='blue', va='center', fontsize=8)
    acum -= d['ba']/2

# Etiquetas de dimensiones finales
ax.text(largo_total/2, ancho_total + 10, f"CORTE: {largo_total:.2f} mm", ha='center', fontweight='bold', size=14)
ax.text(largo_total + 10, ancho_total/2, f"{ancho_total:.2f} mm", va='center', rotation=270, fontweight='bold', size=14)

ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)

st.success(f"### Medida de Chapa: {largo_total:.2f} x {ancho_total:.2f} mm")
