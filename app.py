import streamlit as st
import cv2
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

RANGOS_HSV = {
    "Amarillo / Jugador 1": ([20, 100, 100], [35, 255, 255]),
    "Azul / Jugador 2": ([95, 100, 100], [125, 255, 255]),
    "Verde / Jugador 3": ([40, 100, 100], [80, 255, 255]),
    "Naranja / Jugador 4": ([5, 150, 150], [18, 255, 255])
}

st.set_page_config(page_title="PUBG Mortar - Llatz", layout="centered")
st.title("🎯 PUBG Mortar Calculator")

mapa_sel = st.selectbox("Selecciona el mapa:", list(MAPAS_PUBG.keys()))
tamano_m = MAPAS_PUBG[mapa_sel]

color_sel = st.selectbox("Selecciona tu color de jugador en la partida:", list(RANGOS_HSV.keys()))

archivo = st.file_uploader("Sube una captura de mapa completo (M):", type=["jpg", "png", "jpeg"])

if archivo:
    image = Image.open(archivo)
    img_np = np.array(image.convert("RGB"))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    st.image(image, use_container_width=True, caption="Mapa cargado")
    
    # Detección por color seleccionado
    lower_b, upper_b = RANGOS_HSV[color_sel]
    mask = cv2.inRange(hsv, np.array(lower_b), np.array(upper_b))
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    puntos = []
    for c in contours:
        if cv2.contourArea(c) > 15:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                puntos.append((cx, cy))
                
    if len(puntos) >= 2:
        p1, p2 = puntos[0], puntos[1]
        dist_px = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        dist_m = dist_px * (tamano_m / img_np.shape[1])
        
        st.markdown("---")
        st.metric("Distancia calculada", f"{round(dist_m, 1)} m")
        
        if 121 <= dist_m <= 700:
            st.success("✅ EN RANGO DE MORTERO (121m - 700m)")
        elif dist_m < 121:
            st.warning("⚠️ Demasiado cerca (Mínimo 121m)")
        else:
            st.error("❌ Fuera de alcance (Máximo 700m)")
    else:
        st.info("💡 Introducción manual de posiciones (si falla la lectura automática de color):")
        col1, col2 = st.columns(2)
        with col1:
            x1 = st.number_input("Jugador X", value=int(img_np.shape[1]/2))
            y1 = st.number_input("Jugador Y", value=int(img_np.shape[0]/2))
        with col2:
            x2 = st.number_input("Objetivo X", value=int(img_np.shape[1]/2) + 50)
            y2 = st.number_input("Objetivo Y", value=int(img_np.shape[0]/2) + 50)
            
        dist_px = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        dist_m = dist_px * (tamano_m / img_np.shape[1])
        st.metric("Distancia manual", f"{round(dist_m, 1)} m")
