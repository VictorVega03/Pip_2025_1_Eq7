import sys
from PyQt5 import uic, QtWidgets, QtGui  # Importamos QtGui para QPixmap
import SetServiceTimeView  # Importamos la vista de configuración de tiempo

qtCreatorFile = "StartServiceView.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DispensadorAguaWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, tipo_servicio="Agua"):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.tipo_servicio = tipo_servicio

        # Cambiar título y texto según el tipo de servicio
        if tipo_servicio == "Alimento":
            self.setWindowTitle("Dispensador de Alimento")
            self.labelTitulo.setText("Dispensador de Alimento")

            # Cambiar la imagen para alimento (con QtGui.QPixmap)
            ruta_imagen_alimento = "C:/Users/victorvega/PycharmProjects/Pip_2025_1_Eq7/PIntegradorArchivos/food.png"
            self.labelImagenAgua.setPixmap(QtGui.QPixmap(ruta_imagen_alimento))

        # Área de los Signals
        self.btnVolver.clicked.connect(self.volver)
        self.btnIniciarManual.clicked.connect(self.iniciar_manual)
        self.btnIniciarTiempo.clicked.connect(self.iniciar_tiempo)
        self.btnConfigurarTiempo.clicked.connect(self.configurar_tiempo)

    # Área de los Slots
    def volver(self):
        self.close()

    def iniciar_manual(self):
        # Aquí iría la lógica para iniciar el servicio manual
        print(f"Iniciando servicio manual de {self.tipo_servicio}")

    def iniciar_tiempo(self):
        # Aquí iría la lógica para iniciar el servicio por tiempo
        print(f"Iniciando servicio por tiempo de {self.tipo_servicio}")

    def configurar_tiempo(self):
        self.ventana_configurar = SetServiceTimeView.ConfigurarTiempoWindow(self.tipo_servicio)
        self.ventana_configurar.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DispensadorAguaWindow()
    window.show()
    sys.exit(app.exec_())