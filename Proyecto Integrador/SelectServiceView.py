import sys
from PyQt5 import uic, QtWidgets
import StartServiceView  # Importamos la vista de inicio de servicio

qtCreatorFile = "SelectServiceView.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DispensadorWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Área de los Signals
        # Conectamos los frames como botones
        self.frameAgua.mousePressEvent = self.seleccionar_agua
        self.frameAlimento.mousePressEvent = self.seleccionar_alimento

    # Área de los Slots
    def seleccionar_agua(self, event):
        self.ventana_servicio_agua = StartServiceView.DispensadorAguaWindow("Agua")
        self.ventana_servicio_agua.show()

    def seleccionar_alimento(self, event):
        # Crear vista para el dispensador de alimento
        self.ventana_servicio_alimento = StartServiceView.DispensadorAguaWindow("Alimento")
        self.ventana_servicio_alimento.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DispensadorWindow()
    window.show()
    sys.exit(app.exec_())