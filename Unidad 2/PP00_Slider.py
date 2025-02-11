import sys, time as t
from PyQt5 import uic, QtWidgets, QtGui, QtCore
qtCreatorFile = "PP00_Slider.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # Área de los Signals
        self.selectorImagen.setMinimum(1)
        self.selectorImagen.setMaximum(10)
        self.selectorImagen.setSingleStep(1)
        self.selectorImagen.setValue(1) # valor inicial
        self.selectorImagen.valueChanged.connect(self.cambiaValor)

        self.diccionarioDatos = {
            1: (":/ejercicios/john cena.png", ["john cenna", "Actor"]),
            2: (":/ejercicios/DuckMusic.jpg", ["patto cuack", "Animal"]),
            3: (":/ejercicios/gatoese.jpg", ["gato", "Animal"]),
            4: (":/ejercicios/Guitars.jpg", ["Guitarra", "Instrumento"]),
            5: (":/ejercicios/Imagen1.jpg", ["Malenia", "Personaje"]),
            6: (":/ejercicios/Imagen2.jpg", ["Saul Goodman", "Persona"]),
            7: (":/ejercicios/Imagen3.jpg", ["Aurora Boreal", "Evento Natural"]),
            8: (":/ejercicios/Imagen4.jpg", ["Lampara", "Objeto"]),
            9: (":/ejercicios/JessePinkman.png", ["Jesse Pinkman", "Persona"]),
            10: (":/ejercicios/WaltherWhite.png", ["Walther White", "Persona"])
        }
        self.indice = 1
        self.obtenerDatos()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.incrementarSlider)
        self.timer.start(1000)

    def obtenerDatos(self):
        nombre = self.diccionarioDatos[self.indice][1][0]
        tipo = self.diccionarioDatos[self.indice][1][1]
        self.txt_nombre.setText(nombre)
        self.txt_tipo.setText(tipo)
        self.imagen_descripcion.setPixmap(QtGui.QPixmap(self.diccionarioDatos[self.indice][0]))

    # Área de los Slots
    def cambiaValor(self):
        self.indice = self.selectorImagen.value()
        self.obtenerDatos()

    def incrementarSlider(self):
        valorActual = self.selectorImagen.value()
        if valorActual < self.selectorImagen.maximum():
            self.selectorImagen.setValue(valorActual + 1)
        else:
            self.selectorImagen.setValue(self.selectorImagen.minimum())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())