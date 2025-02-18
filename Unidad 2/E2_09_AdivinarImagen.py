import sys, time as t
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox

qtCreatorFile = ("E2_09_AdivinarImagen.ui")  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Área de los Signals
        self.rbopc1.clicked.connect(self.opcion1)
        self.rbopc2.clicked.connect(self.opcion2)
        self.rbopc3.clicked.connect(self.opcion3)

        self.casos = {
            1: ("Quien es Walther White?", ":/ejercicios/WaltherWhite.png", ":/ejercicios/JessePinkman.png", ":/ejercicios/Imagen2.jpg", 0),
            2: ("Quien es John Cenna?", ":/ejercicios/tuvefe.jpg", ":/ejercicios/therockmeme.jpg", ":/ejercicios/john cena.png", 2),
            3: ("Quien es The Rock?", ":/ejercicios/john cena.png" , ":/ejercicios/therockmeme.jpg", ":/ejercicios/tuvefe.jpg", 1)
        }

        self.counter = 0
        self.index = 1
        self.respuestaindex = 0
        self.camposrespuesta = [self.res1, self.res2, self.res3]
        self.cargarcasos(self.index)

    # Área de los Slots
    def opcion1(self):
        v = self.rbopc1.isChecked()
        selected = 0
        print("Opción 1", v, selected)
        self.validarespuesta(selected)
    def opcion2(self):
        v = self.rbopc2.isChecked()
        selected = 1
        print("Opción 2", v, selected)
        self.validarespuesta(selected)
    def opcion3(self):
        v = self.rbopc3.isChecked()
        selected = 2
        print("Opción 3", v, selected)
        self.validarespuesta(selected)

    def cargarcasos(self, index):
        self.lbltitulo.setText(self.casos[index][0])
        self.imagen1.setPixmap(QtGui.QPixmap(self.casos[index][1]))
        self.imagen2.setPixmap(QtGui.QPixmap(self.casos[index][2]))
        self.imagen3.setPixmap(QtGui.QPixmap(self.casos[index][3]))

    def validarespuesta(self, selected):
        if selected == self.casos[self.index][4]:
            self.lblresultado.setText("Correcto")
            self.camposrespuesta[self.respuestaindex].setPixmap(QtGui.QPixmap(":/ejercicios/marcaverde.png"))
            self.imagen_resultado.setPixmap(QtGui.QPixmap(":/ejercicios/bolamarilla.jpg"))
            self.counter += 1
        else:
            self.lblresultado.setText("Incorrecto")
            self.camposrespuesta[self.respuestaindex].setPixmap(QtGui.QPixmap(":/ejercicios/incorrecto.png"))
            self.imagen_resultado.setPixmap(QtGui.QPixmap(":/ejercicios/gatoRiendose.png"))

        if self.index == len(self.casos) and self.counter >= 2:
            self.mostrarMensaje("Acertaste {} veces, Has ganado", self.counter)
        elif self.index == len(self.casos) and self.counter < 2:
            self.mostrarMensaje("Acertaste {} veces, Has perdido", self.counter)

        QtCore.QTimer.singleShot(2000, self.avanzarCaso)
        QtCore.QTimer.singleShot(2000, self.limpiarResultado)

    def avanzarCaso(self):
        if self.index < len(self.casos):
            self.index += 1
            self.respuestaindex += 1
            self.cargarcasos(self.index)

    def limpiarResultado(self):
        self.lblresultado.clear()
        self.imagen_resultado.clear()
        self.rbopc1.setChecked(False)
        self.rbopc2.setChecked(False)
        self.rbopc3.setChecked(False)

    def mostrarMensaje(self, mensaje, variable):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(mensaje.format(variable))
        msg.setWindowTitle("Resultado del Juego")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
