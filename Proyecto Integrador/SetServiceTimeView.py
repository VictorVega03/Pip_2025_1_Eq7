import sys
from PyQt5 import uic, QtWidgets

qtCreatorFile = "SetServiceTImeVIew.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class ConfigurarTiempoWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, tipo_servicio="Agua"):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.tipo_servicio = tipo_servicio
        self.servicio_iniciado = False

        # Actualizar el título según el tipo de servicio
        if tipo_servicio == "Alimento":
            self.setWindowTitle("Configurar Tiempo de Servicio - Alimento")
            # Si la ventana tiene un label de título, también lo actualizaríamos aquí
            if hasattr(self, 'labelTitulo'):
                self.labelTitulo.setText("Configurar Tiempo de Servicio - Alimento")

        # Área de los Signals
        self.btnIniciar.clicked.connect(self.iniciar_detener)
        self.btnGuardar.clicked.connect(self.guardar)
        self.btnVolver.clicked.connect(self.volver)

    # Área de los Slots
    def iniciar_detener(self):
        if not self.servicio_iniciado:
            # Iniciar servicio
            self.servicio_iniciado = True
            self.btnIniciar.setText("Detener")
            self.btnIniciar.setStyleSheet("""
            QPushButton {
                background-color: #FF6347;
                border-radius: 18px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF4500;
            }
            QPushButton:pressed {
                background-color: #DC143C;
            }
            """)
            print(f"Iniciando dispensador de {self.tipo_servicio}")
        else:
            # Detener servicio
            self.servicio_iniciado = False
            self.btnIniciar.setText("Iniciar")
            self.btnIniciar.setStyleSheet("""
            QPushButton {
                background-color: #90EE90;
                border-radius: 18px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #9ACD32;
            }
            QPushButton:pressed {
                background-color: #7CFC00;
            }
            """)
            print(f"Deteniendo dispensador de {self.tipo_servicio}")

    def guardar(self):
        # Aquí iría la lógica para guardar la configuración de tiempo
        print(f"Guardando configuración de tiempo para {self.tipo_servicio}")
        self.close()

    def volver(self):
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ConfigurarTiempoWindow()
    window.show()
    sys.exit(app.exec_())