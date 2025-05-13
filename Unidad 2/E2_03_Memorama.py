import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi

class Memorama(QMainWindow):
    def __init__(self):
        super(Memorama, self).__init__()
        loadUi('E2_03_Memorama.ui', self)  # Asegúrate de que el nombre del archivo sea correcto

        # Diccionario de imágenes
        self.imagenes = {
            "img_0_0": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/ejercicios/ContornoTD.jpg"
            },
            "img_0_1": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/logos/FIT_logo_vertical.png"
            },
            "img_0_2": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/logos/log_uat_nuevo.png"
            },
            "img_0_3": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/ejercicios/ContornoTD.jpg"
            },
            "img_1_0": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/logos/FIT_logo_vertical.png"
            },
            "img_1_1": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/logos/log_uat_nuevo.png"
            },
            "img_1_2": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/ejercicios/ContornoTD.jpg"
            },
            "img_1_3": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/logos/FIT_logo_vertical.png"
            },
            "img_2_0": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/logos/log_uat_nuevo.png"
            },
            "img_2_1": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/ejercicios/ContornoTD.jpg"
            },
            "img_2_2": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/logos/FIT_logo_vertical.png"
            },
            "img_2_3": {
                "interrogacion": ":/ejercicios/signointerroacion.png",
                "real": ":/logos/log_uat_nuevo.png"
            }
        }

        # Lista de botones (QLabel)
        self.botones = [
            self.img_0_0, self.img_0_1, self.img_0_2, self.img_0_3,
            self.img_1_0, self.img_1_1, self.img_1_2, self.img_1_3,
            self.img_2_0, self.img_2_1, self.img_2_2, self.img_2_3
        ]

        # Estado de las imágenes (mostradas o no)
        self.imagenes_mostradas = [False] * len(self.botones)

        # Variables para rastrear los clics
        self.primer_click = None
        self.segundo_click = None

        # Inicializar el juego
        self.inicializar_juego()

    def inicializar_juego(self):
        # Configurar las imágenes iniciales (signo de interrogación)
        for i, boton in enumerate(self.botones):
            boton.mousePressEvent = lambda event, idx=i: self.mostrar_imagen(idx)
            boton.setPixmap(QPixmap(self.imagenes[f"img_{i//4}_{i%4}"]["interrogacion"])) # Ajusta el índice según tu grid

        # Ocultar las imágenes después de 2 segundos
        QTimer.singleShot(2000, self.ocultar_imagenes)

    def mostrar_imagen(self, idx):
        if self.imagenes_mostradas[idx]:
            return

        # Mostrar la imagen real
        boton = self.botones[idx]
        boton.setPixmap(QPixmap(self.imagenes[f"img_{idx//4}_{idx%4}"]["real"]))  # Ajusta el índice según tu grid
        self.imagenes_mostradas[idx] = True

        # Verificar si es el primer o segundo clic
        if self.primer_click is None:
            self.primer_click = idx
        else:
            self.segundo_click = idx
            self.verificar_coincidencia()

    def ocultar_imagenes(self):
        # Ocultar todas las imágenes que no han sido mostradas
        for i, boton in enumerate(self.botones):
            if not self.imagenes_mostradas[i]:
                boton.setPixmap(QPixmap(self.imagenes[f"img_{i//4}_{i%4}"]["interrogacion"]))  # Ajusta el índice según tu grid

    def verificar_coincidencia(self):
        # Verificar si las dos imágenes seleccionadas coinciden
        if self.imagenes[f"img_{self.primer_click//4}_{self.primer_click%4}"]["real"] == self.imagenes[f"img_{self.segundo_click//4}_{self.segundo_click%4}"]["real"]:
            self.primer_click = None
            self.segundo_click = None
        else:
            # Si no coinciden, ocultarlas después de 1 segundo
            QTimer.singleShot(1000, self.reiniciar_clicks)

    def reiniciar_clicks(self):
        # Ocultar las imágenes que no coincidieron
        self.botones[self.primer_click].setPixmap(QPixmap(self.imagenes[f"img_{self.primer_click//4}_{self.primer_click%4}"]["interrogacion"]))
        self.botones[self.segundo_click].setPixmap(QPixmap(self.imagenes[f"img_{self.segundo_click//4}_{self.segundo_click%4}"]["interrogacion"]))
        self.imagenes_mostradas[self.primer_click] = False
        self.imagenes_mostradas[self.segundo_click] = False
        self.primer_click = None
        self.segundo_click = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Memorama()
    window.show()
    sys.exit(app.exec_())