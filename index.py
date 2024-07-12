import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
from pynput.keyboard import Controller

# Inicialización de la cámara y configuración de la resolución
def init_camera(width=1280, height=720):
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)
    return cap

# Inicialización del detector de manos
def init_hand_detector(detection_confidence=0.8):
    return HandDetector(detectionCon=detection_confidence)

# Clase que representa un botón
class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

# Creación de botones basados en las teclas definidas
def create_buttons(keys):
    button_list = []
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            button_list.append(Button([100 * j + 50, 100 * i + 50], key))
    return button_list

# Dibuja todos los botones en la imagen
def draw_all_buttons(img, button_list):
    for button in button_list:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img

# Verifica si un punto está dentro de un área rectangular
def is_point_in_rectangle(x, y, w, h, px, py):
    return x < px < x + w and y < py < y + h

# Lógica principal del programa refactorizada para mejorar la velocidad
def main():
    cap = init_camera()
    detector = init_hand_detector()
    
    # Definición de las teclas en el teclado virtual
    keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
            ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
    
    button_list = create_buttons(keys)
    final_text = ""
    keyboard = Controller()

    while True:
        success, img = cap.read()

        # Copia de la imagen original para mantener las detecciones de manos
        img_copy = img.copy()

        # Detección de manos en la imagen copiada
        hands, img_copy = detector.findHands(img_copy)

        # Dibuja los botones en la imagen original
        img = draw_all_buttons(img, button_list)

        if hands:
            hand = hands[0]
            lm_list = hand["lmList"]
            point1 = lm_list[8][:2]  # Punta del índice
            point2 = lm_list[4][:2]  # Punta del pulgar

            for button in button_list:
                x, y = button.pos
                w, h = button.size

                # Verifica si el dedo índice está sobre un botón
                if is_point_in_rectangle(x, y, w, h, point1[0], point1[1]):
                    cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                    # Calcula la distancia entre el índice y el pulgar
                    l, _, _ = detector.findDistance(point1, point2)

                    # Si la distancia es pequeña, simula la pulsación de la tecla
                    if l < 30:
                        keyboard.press(button.text)
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                        final_text += button.text  # Añade la tecla al texto final
                        sleep(0.15)  # Espera un momento para evitar múltiples detecciones

        # Muestra el texto final en la imagen
        cv2.putText(img, final_text, (50, 600), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

        cv2.imshow("Image", img)  # Muestra la imagen
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
