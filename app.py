import cv2
import numpy as np
import math

# Cargar la captura de pantalla del mapa
img = cv2.imread('mapa_pubg.png')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Ejemplo: Definir rango HSV para detectar la marca amarilla (Punto B)
yellow_lower = np.array([20, 100, 100])
yellow_upper = np.array([30, 255, 255])

mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)
contours, _ = cv2.findContours(mask_yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

if contours:
    # Obtener el centroide del contorno más grande encontrado
    c = max(contours, key=cv2.contourArea)
    M = cv2.moments(c)
    if M["m00"] != 0:
        bx = int(M["m10"] / M["m00"])
        by = int(M["m01"] / M["m00"])
        print(f"Punto B (Marca amarilla): ({bx}, {by})")

# Supongamos que la posición del jugador A ya fue detectada en (ax, ay)
ax, ay = 500, 400 
bx, by = 650, 520

# Relación de píxeles a metros en el mapa actual
m_per_pixel = 1.5 

# Cálculo de la distancia
dist_px = math.sqrt((bx - ax)**2 + (by - ay)**2)
dist_metros = dist_px * m_per_pixel

print(f"Distancia para mortero: {round(dist_metros)} metros")
