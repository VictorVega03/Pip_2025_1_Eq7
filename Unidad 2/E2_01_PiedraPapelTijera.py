import sys, time as t
from random import randint
from PyQt5 import uic, QtWidgets, QtGui, QtCore

qtCreatorFile = "E2_01_PiedraPapelTijera.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Área de los Signals
        self.rbpiedra.clicked.connect(self.piedra)
        self.rbpapel.clicked.connect(self.papel)
        self.rbtijera.clicked.connect(self.tijera)
        self.rblimpiar.clicked.connect(self.limpiarResultado)

        self.imagenes = {
            1: (":/ejercicios/piedra.png", 0),
            2: (":/ejercicios/papel.png", 1),
            3: (":/ejercicios/tijera.png", 2)
        }
        self.casos = {
            (0, 0): ("Empate", ":/ejercicios/WaltherWhite.png"),
            (0, 1): ("Perdiste", ":/ejercicios/gatoRiendose.png"),
            (0, 2): ("Ganaste", ":/ejercicios/bolamarilla.jpg"),
            (1, 0): ("Ganaste", ":/ejercicios/bolamarilla.jpg"),
            (1, 1): ("Empate", ":/ejercicios/WaltherWhite.png"),
            (1, 2): ("Perdiste", ":/ejercicios/gatoRiendose.png"),
            (2, 0): ("Perdiste", ":/ejercicios/gatoRiendose.png"),
            (2, 1): ("Ganaste", ":/ejercicios/bolamarilla.jpg"),
            (2, 2): ("Empate", ":/ejercicios/WaltherWhite.png")
        }

    # Área de los Slots
    def piedra(self):
        v = self.rbpiedra.isChecked()
        selected = 0
        print("piedra", v, selected)
        self.cambiarImagen(selected)
    def papel(self):
        v = self.rbpapel.isChecked()
        selected = 1
        print("papel", v, selected)
        self.cambiarImagen(selected)

    def tijera(self):
        v = self.rbtijera.isChecked()
        selected = 2
        print("tijera", v, selected)
        self.cambiarImagen(selected)

    def cambiarImagen(self, selected):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.actualizarImagen)
        self.timer.start(100)

        QtCore.QTimer.singleShot(4000, lambda: self.timer.stop())  # Detener después de 4 segundos
        QtCore.QTimer.singleShot(4000, lambda: self.resultado(selected))

    def actualizarImagen(self):
        value = randint(1, 3)
        self.imagen_random.setPixmap(QtGui.QPixmap(self.imagenes[value][0]))
        self.valorComputadora = self.imagenes[value][1]

    def resultado(self, selected):
        print("Resultado", selected, self.valorComputadora),
        texto = self.casos[(selected, self.valorComputadora)][0]
        imagen = self.casos[(selected, self.valorComputadora)][1]

        self.txt_resultado.setText(str(texto))
        self.imagen_resultado.setPixmap(QtGui.QPixmap(imagen))

    def limpiarResultado(self):
        self.txt_resultado.clear()
        self.imagen_resultado.clear()
        self.imagen_random.setPixmap(QtGui.QPixmap(":/ejercicios/signointerroacion.png"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
