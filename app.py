import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Controller

# Inicialización de la cámara y configuración de la resolución
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Inicialización del detector de manos
detector = HandDetector(detectionCon=0.8)

# Definición de las teclas en el teclado virtual
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]

finalText = ""  # Texto final ingresado por el usuario

keyboard = Controller()  # Inicialización del controlador del teclado físico


# Función para dibujar todos los botones en la imagen
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                          20, rt=0)  # Dibuja un rectángulo redondeado en la esquina del botón
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)  # Dibuja el botón
        cv2.putText(img, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)  # Coloca el texto en el botón
    return img


# Clase que representa un botón
class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


# Creación de la lista de botones basados en las teclas definidas
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

while True:
    success, img = cap.read()  # Captura una imagen de la cámara
    img = detector.findHands(img)  # Detecta las manos en la imagen
    lmList, bboxInfo = detector.findPosition(img)  # Obtiene la posición de los landmarks de las manos
    img = drawAll(img, buttonList)  # Dibuja todos los botones en la imagen

    if lmList:
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            # Verifica si la punta del dedo índice está sobre un botón
            if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65),
                            cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                # Calcula la distancia entre la punta del índice y la del pulgar
                l, _, _ = detector.findDistance(8, 12, img, draw=False)
                print(l)

                # Cuando se hace clic (distancia pequeña), simula la pulsación de la tecla
                if l < 30:
                    keyboard.press(button.text)
                    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65),
                                cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    finalText += button.text  # Añade la tecla al texto final
                    sleep(0.15)  # Espera un momento para evitar múltiples detecciones

    # Dibuja un rectángulo para mostrar el texto final ingresado
    cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, finalText, (60, 430),
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Image", img)  # Muestra la imagen en una ventana
    cv2.waitKey(1)  # Espera por una tecla para cerrar la ventana

