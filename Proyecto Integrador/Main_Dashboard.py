import sys
from PyQt5 import uic, QtWidgets
import ServiceHistoryView  # Importamos la vista de historial
import SelectServiceView  # Importamos la vista de selección de servicio

qtCreatorFile = "Dashboard.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Área de los Signals
        self.btnHistorial.clicked.connect(self.mostrar_historial)
        self.btnDispensador.clicked.connect(self.mostrar_dispensador)

    # Área de los Slots
    def mostrar_historial(self):
        self.ventana_historial = ServiceHistoryView.HistorialServiciosWindow()
        self.ventana_historial.show()

    def mostrar_dispensador(self):
        self.ventana_dispensador = SelectServiceView.DispensadorWindow()
        self.ventana_dispensador.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())