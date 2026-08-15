import streamlit as st
import cv2
import numpy as np
import math
from PIL import Image

# Configuración de tamaños de mapa en metros
MAPAS_PUBG = {
    "Erangel (8x8 km)": 8000,
    "Miramar (8x8 km)": 8000,
    "Taego (8x8 km)": 8000,
    "Rondo (8x8 km)": 8000,
    "Sanhok (4x4 km)": 4000,
    "Vikar (6x6 km)": 6000,
    "Karakin (2x2 km)": 2000,
    "Paramo (3x3 km)": 3000
}

st.title("🎯 Calculadora de Mortero PUBG")

mapa_seleccionado = st.selectbox("Selecciona el mapa:", list(MAPAS_PUBG.keys()))
tamano_mapa_m = MAPAS_PUBG[mapa_seleccionado]

archivo = st.file_uploader("Sube una captura del mapa completo (M):", type=["png", "jpg", "jpeg"])

if archivo is not None:
    # Cargar imagen
    image = Image.open(archivo)
    img_array = np.array(image)
    
    st.image(image, caption="Mapa cargado", use_container_width=True)
    
    st.info("Ingresa la posición en píxeles o detecta mediante colores:")
    
    # Simulación de cálculo por coordenadas seleccionadas
    col1, col2 = st.columns(2)
    with col1:
        x1 = st.number_input("Jugador X (px)", value=int(img_array.shape[1] / 2))
        y1 = st.number_input("Jugador Y (px)", value=int(img_array.shape[0] / 2))
    with col2:
        x2 = st.number_input("Objetivo X (px)", value=int(img_array.shape[1] / 2) + 100)
        y2 = st.number_input("Objetivo Y (px)", value=int(img_array.shape[0] / 2) + 100)
        
    dist_px = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    metros_por_px = tamano_mapa_m / img_array.shape[1]
    dist_m = dist_px * metros_por_px
    
    st.subheader(f"Distancia estimada: **{round(dist_m, 1)} metros**")
    
    if 121 <= dist_m <= 700:
        st.success("✅ EN RANGO DE MORTERO (121m - 700m)")
    elif dist_m < 121:
        st.warning("⚠️ Demasiado cerca (Mínimo 121m)")
    else:
        st.error("❌ Fuera de alcance (Máximo 700m)")
