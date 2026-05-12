import streamlit as st
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Desarrollo Asimétrico 4 Lados", layout="wide")

st.title("📏 Desarrollo de Chapa: Perímetro Asimétrico")
st.markdown("Calcula el corte de chapa para piezas donde cada lado tiene pliegues distintos.")

# --- PARÁMETROS TÉCNICOS ---
st.sidebar.header("Parámetros del Material")
t = st.sidebar.number_input("Espesor (t) mm", min_value=0.1, value=1.5, step=0.1)
material = st.sidebar.selectbox("Material", ["Acero Carbono", "Inoxidable", "Aluminio"])

# Lógica de Factor K (Referencia 63277.jpg)
if "Carbono" in material: k_factor = 0.33 if t <= 3.0 else 0.45
elif "Inoxidable" in material: k_factor = 0.40
else: k_factor = 0.45

def calcular_desarrollo_lado(nombre_lado):
    st.subheader(f"Configuración Lado {nombre_lado}")
    n_pliegues = st.number_input(f"Nº pliegues {nombre_lado}", min_value=0, max_value=5, value=1, key=f"n_{nombre_lado}")
    
    desarrollo_lado = 0
    for i in range(int(n_pliegues)):
        c1, c2 = st.columns(2)
        alt = c1.number_input(f"Altura Pestaña {i+1} (mm)", value=20.0, key=f"l_{nombre_lado}_{i}")
        rad = c2.number_input(f"Radio R{i+1} (mm)", value=t, key=f"r_{nombre_lado}_{i}")
        
        # Fórmula BA (Referencia 63277.jpg)
        ba = (90 / 180) * math.pi * (rad + (k_factor * t))
        # Sumamos el tramo recto real + el estiramiento
        desarrollo_lado += (alt - (rad + t)) + ba
    return desarrollo_lado

# --- ENTRADA DE DIMENSIONES ---
col_izq, col_der = st.columns(2)

with col_izq:
    base_x = st.number_input("Base central (Largo) mm", value=200.0)
    des_izquierdo = calcular_desarrollo_lado("Izquierdo (Oeste)")
    des_derecho = calcular_desarrollo_lado("Derecho (Este)")

with col_der:
    base_z = st.number_input("Base central (Ancho) mm", value=100.0)
    des_superior = calcular_desarrollo_lado("Superior (Norte)")
    des_inferior = calcular_desarrollo_lado("Inferior (Sur)")

# --- CÁLCULO FINAL ---
# El largo total es: Desarrollo Izq + Base X + Desarrollo Der
# El ancho total es: Desarrollo Sup + Base Z + Desarrollo Inf

largo_total = des_izquierdo + base_x + des_derecho
ancho_total = des_superior + base_z + des_inferior

# --- DIBUJO DEL PLANO ---
st.divider()
st.header("3. Plano de Desarrollo de Corte")

fig, ax = plt.subplots(figsize=(10, 6))

# Chapa total
rect_chapa = plt.Rectangle((0, 0), largo_total, ancho_total, linewidth=2, edgecolor='black', facecolor='#fffde7')
ax.add_patch(rect_chapa)

# Dibujo de la base central (líneas de pliegue principales)
base_rect = plt.Rectangle((des_izquierdo, des_inferior), base_x, base_z, 
                           linewidth=1, edgecolor='red', linestyle='--', facecolor='none', label='Líneas de pliegue')
ax.add_patch(base_rect)

# Etiquetas de dimensiones
ax.text(largo_total/2, ancho_total + 5, f"LARGO DE CORTE: {largo_total:.2f} mm", ha='center', fontweight='bold', color='blue')
ax.text(-15, ancho_total/2, f"ANCHO DE CORTE: {ancho_total:.2f} mm", va='center', rotation=90, fontweight='bold', color='blue')

ax.set_xlim(-40, largo_total + 40)
ax.set_ylim(-40, ancho_total + 40)
ax.set_aspect('equal')
ax.axis('off')
st.pyplot(fig)

# --- RESULTADOS ---
c_res1, c_res2 = st.columns(2)
c_res1.metric("Chapa Largo (X)", f"{largo_total:.2f} mm")
c_res2.metric("Chapa Ancho (Z)", f"{ancho_total:.2f} mm")

st.success(f"### Medida de Guillotina/Láser: {largo_total:.2f} x {ancho_total:.2f} mm")
