import streamlit as st
import cv2
import numpy as np
import math
from PIL import Image
import easyocr

MAPAS_PUBG = {
    "Erangel / Miramar / Taego / Rondo (8x8 km)": 8000,
    "Vikar (6x6 km)": 6000,
    "Sanhok (4x4 km)": 4000,
    "Paramo (3x3 km)": 3000,
    "Karakin (2x2 km)": 2000
}

# Rangos de color HSV para los 4 colores de jugador en PUBG
RANGOS_HSV = {
    "Amarillo / Jugador 1": ([20, 100, 100], [35, 255, 255]),
    "Azul / Jugador 2": ([95, 100, 100], [125, 255, 255]),
    "Verde / Jugador 3": ([40, 100, 100], [80, 255, 255]),
    "Naranja / Jugador 4": ([5, 150, 150], [18, 255, 255])
}

st.set_page_config(page_title="PUBG Mortar - Gamertag Detector", layout="centered")
st.title("🎯 PUBG Mortar Auto-Detector")

# Inicializar lector OCR en caché para rapidez
@st.cache_resource
def cargar_ocr():
    return easyocr.Reader(['en'])

reader = cargar_ocr()

gamertag = st.text_input("Ingresa tu Gamertag exacto:", value="Llatz")
mapa_sel = st.selectbox("Selecciona el mapa:", list(MAPAS_PUBG.keys()))
tamano_m = MAPAS_PUBG[mapa_sel]

archivo = st.file_uploader("Sube una captura de mapa completo (M):", type=["jpg", "png", "jpeg"])

if archivo and gamertag:
    image = Image.open(archivo)
    img_np = np.array(image.convert("RGB"))
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    
    st.image(image, use_container_width=True, caption="Imagen cargada")
    
    with st.spinner(f"Buscando a '{gamertag}' en el mapa..."):
        # 1. OCR: Buscar texto en la imagen
        resultados = reader.readtext(img_np)
        
        pos_jugador = None
        color_detectado = None
        
        for (bbox, texto, prob) in resultados:
            # Coincidencia flexible de texto para Gamertags
            if gamertag.lower() in texto.lower() or "llatz" in texto.lower():
                # Centro del texto encontrado
                (top_left, top_right, bottom_right, bottom_left) = bbox
                cx = int((top_left[0] + bottom_right[0]) / 2)
                cy = int((top_left[1] + bottom_right[1]) / 2)
                pos_jugador = (cx, cy)
                
                # Muestra de color alrededor del texto
                pixel_hsv = hsv[max(0, cy-5):min(hsv.shape[0], cy+5), max(0, cx-5):min(hsv.shape[1], cx+5)]
                if pixel_hsv.size > 0:
                    h_mean = np.mean(pixel_hsv[:, :, 0])
                    s_mean = np.mean(pixel_hsv[:, :, 1])
                    
                    # Identificar a cuál de los 4 colores pertenece
                    if 20 <= h_mean <= 35:
                        color_detectado = "Amarillo / Jugador 1"
                    elif 95 <= h_mean <= 125:
                        color_detectado = "Azul / Jugador 2"
                    elif 40 <= h_mean <= 80:
                        color_detectado = "Verde / Jugador 3"
                    elif 5 <= h_mean <= 18:
                        color_detectado = "Naranja / Jugador 4"
                break

    if pos_jugador:
        st.success(f"✅ Gamertag **{gamertag}** localizado en píxeles: {pos_jugador}")
        
        # Selección manual de respaldo si el color no fue preciso por compresión
        if not color_detectado:
            color_detectado = st.selectbox("Selecciona tu color de jugador en la partida:", list(RANGOS_HSV.keys()))
        else:
            st.info(f"Color identificado automáticamente: **{color_detectado}**")
            
        # 2. Buscar el ping/marcador correspondiente a ese color
        lower_b, upper_b = RANGOS_HSV[color_detectado]
        mask = cv2.inRange(hsv, np.array(lower_b), np.array(upper_b))
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrar contornos lejanos al nombre para hallar la marca de objetivo
        pos_objetivo = None
        min_dist = float("inf")
        
        for c in contours:
            if cv2.contourArea(c) > 10:  # Filtrar ruido de píxeles aislados
                M = cv2.moments(c)
                if M["m00"] != 0:
                    ox = int(M["m10"] / M["m00"])
                    oy = int(M["m01"] / M["m00"])
                    
                    # Evitar seleccionar la propia etiqueta del nombre
                    d = math.sqrt((ox - pos_jugador[0])**2 + (oy - pos_jugador[1])**2)
                    if d > 30 and d < min_dist:
                        min_dist = d
                        pos_objetivo = (ox, oy)
        
        if pos_objetivo:
            st.success(f"🎯 Marca de objetivo hallada en píxeles: {pos_objetivo}")
            
            # 3. Calcular distancia final
            dist_px = math.sqrt((pos_objetivo[0] - pos_jugador[0])**2 + (pos_objetivo[1] - pos_jugador[1])**2)
            dist_m = dist_px * (tamano_m / img_np.shape[1])
            
            st.markdown("---")
            st.metric("Distancia para Mortero", f"{round(dist_m, 1)} m")
            
            if 121 <= dist_m <= 700:
                st.success("✅ EN RANGO OPERATIVO DE MORTERO (121m - 700m)")
            elif dist_m < 121:
                st.warning("⚠️ Demasiado cerca (Alcance mínimo: 121m)")
            else:
                st.error("❌ Fuera de alcance (Alcance máximo: 700m)")
        else:
            st.warning("⚠️ No se encontró la marca de objetivo del mismo color en el mapa.")
    else:
        st.error(f"❌ No se encontró el texto '{gamertag}' en la captura. Asegúrate de que el mapa abierto (M) sea legible y sin distorsión.")
