import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
from pynput.keyboard import Controller
from pynput.keyboard import Key

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
        draw_button(img, button)
    return img

# Dibuja un botón individual en la imagen
def draw_button(img, button, color=(255, 0, 255)):
    x, y = button.pos
    w, h = button.size
    cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)
    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

# Verifica si un punto está dentro de un área rectangular
def is_point_in_rectangle(x, y, w, h, px, py):
    return x < px < x + w and y < py < y + h

# Maneja la detección de manos y la interacción con los botones
def handle_hand_detection(img, hands, button_list, final_text, keyboard, detector):
    if not hands:
        return final_text

    hand = hands[0]
    lm_list = hand["lmList"]
    point1 = lm_list[4][:2]  # Punta del Pulgar
    point2 = lm_list[8][:2]  # Punta del Indice

    for button in button_list:
        if is_point_in_rectangle(*button.pos, *button.size, *point1):
            draw_button(img, button, color=(175, 0, 175))
            l, _, _ = detector.findDistance(point1, point2)

            if l < 30:
                if button.text == "<-":
                    if final_text:
                        final_text = final_text[:-1]
                        keyboard.press(Key.backspace)
                else:
                    keyboard.press(button.text)
                    final_text += button.text
                draw_button(img, button, color=(0, 255, 0))
                sleep(0.15)

    return final_text

# Lógica principal del programa refactorizada para mejorar la velocidad
def main():
    cap = init_camera()
    detector = init_hand_detector()
    keys = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "<-"]
    ]
    button_list = create_buttons(keys)
    final_text = ""
    keyboard = Controller()

    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)
        img = draw_all_buttons(img, button_list)
        final_text = handle_hand_detection(img, hands, button_list, final_text, keyboard, detector)

        # Muestra el texto final en la imagen
        cv2.putText(img, final_text, (50, 600), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
