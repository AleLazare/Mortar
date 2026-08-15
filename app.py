import streamlit as st
import numpy as np
import math
from PIL import Image

MAPAS_PUBG = {
    "Erangel / Miramar / Taego / Rondo (8x8 km)": 8000,
    "Vikar (6x6 km)": 6000,
    "Sanhok (4x4 km)": 4000,
    "Paramo (3x3 km)": 3000,
    "Karakin (2x2 km)": 2000
}

st.set_page_config(page_title="PUBG Mortero", layout="centered")
st.title("🎯 PUBG Mortar Calculator")

mapa_sel = st.selectbox("Selecciona el mapa:", list(MAPAS_PUBG.keys()))
tamano_m = MAPAS_PUBG[mapa_sel]

archivo = st.file_uploader("Toma una foto o sube captura del mapa:", type=["jpg", "png", "jpeg"])

if archivo:
    image = Image.open(archivo)
    st.image(image, use_container_width=True)
    
    ancho, alto = image.size
    
    st.markdown("### 📍 Posiciones (Coordenadas en px)")
    col1, col2 = st.columns(2)
    with col1:
        x1 = st.number_input("Jugador X", value=int(ancho/2), step=10)
        y1 = st.number_input("Jugador Y", value=int(alto/2), step=10)
    with col2:
        x2 = st.number_input("Objetivo X", value=int(ancho/2) + 50, step=10)
        y2 = st.number_input("Objetivo Y", value=int(alto/2) + 50, step=10)
        
    dist_px = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    dist_m = dist_px * (tamano_m / ancho)
    
    st.markdown("---")
    st.metric("Distancia calculada", f"{round(dist_m, 1)} m")
    
    if 121 <= dist_m <= 700:
        st.success("✅ EN RANGO DE MORTERO (121m - 700m)")
    elif dist_m < 121:
        st.warning("⚠️ Demasiado cerca (Mínimo 121m)")
    else:
        st.error("❌ Fuera de alcance (Máximo 700m)")
