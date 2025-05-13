import sys
from PyQt5 import uic, QtWidgets
import DetailsServiceView  # Importamos la vista de detalles

qtCreatorFile = "ServiceHistoryView.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class HistorialServiciosWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Área de los Signals
        self.btnVolver.clicked.connect(self.volver)
        self.btnVerRegistro.clicked.connect(self.ver_detalles)
        self.btnPrevious.clicked.connect(self.pagina_anterior)
        self.btnNext.clicked.connect(self.pagina_siguiente)

        # Inicializar variables
        self.pagina_actual = 1

    # Área de los Slots
    def volver(self):
        self.close()

    def ver_detalles(self):
        self.ventana_detalles = DetailsServiceView.DetallesOperacionWindow()
        self.ventana_detalles.show()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.lineEditPage.setText(str(self.pagina_actual))
            # Aquí actualizarías la información mostrada

    def pagina_siguiente(self):
        # Asumiendo que hay más páginas disponibles
        self.pagina_actual += 1
        self.lineEditPage.setText(str(self.pagina_actual))
        # Aquí actualizarías la información mostrada


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = HistorialServiciosWindow()
    window.show()
    sys.exit(app.exec_())