import sys
from PyQt5 import uic, QtWidgets, QtGui
import SetServiceTimeView
from PetFeederController import PetFeederController

qtCreatorFile = "StartServiceView.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DispensadorAguaWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, tipo_servicio="Agua"):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.pet_feeder = PetFeederController()
        self.tipo_servicio = tipo_servicio
        self.servicio_activo = False

        # Cambiar título y contenido según el tipo de servicio
        if tipo_servicio == "Alimento":
            self.setWindowTitle("Dispensador de Alimento")
            self.labelTitulo.setText("Dispensador de Alimento")

            # Cambiar imagen para alimento
            ruta_imagen_alimento = "C:/Users/victorvega/PycharmProjects/Pip_2025_1_Eq7/PIntegradorArchivos/food.png"
            self.labelImagenAgua.setPixmap(QtGui.QPixmap(ruta_imagen_alimento))

        self.btnVolver.clicked.connect(self.volver)
        self.btnIniciarManual.clicked.connect(self.iniciar_manual)
        self.btnIniciarTiempo.clicked.connect(self.iniciar_tiempo)
        self.btnConfigurarTiempo.clicked.connect(self.configurar_tiempo)

        # Verificar conexión con ESP32
        if not self.pet_feeder.is_esp32_connected():
            mensaje = QtWidgets.QMessageBox()
            mensaje.setIcon(QtWidgets.QMessageBox.Warning)
            mensaje.setWindowTitle("Advertencia")
            mensaje.setText("No hay conexión con el ESP32.")
            mensaje.setInformativeText("Algunas funciones podrían no estar disponibles.")
            mensaje.setStandardButtons(QtWidgets.QMessageBox.Ok)
            mensaje.exec_()

    def volver(self):
        self.close()

    def iniciar_manual(self):
        if not self.pet_feeder.is_esp32_connected():
            self.mostrar_mensaje_error("No hay conexión con el ESP32")
            return

        confirmar = QtWidgets.QMessageBox()
        confirmar.setIcon(QtWidgets.QMessageBox.Question)
        confirmar.setWindowTitle("Confirmar")
        confirmar.setText(f"¿Desea iniciar el dispensador de {self.tipo_servicio}?")
        confirmar.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmar.setDefaultButton(QtWidgets.QMessageBox.No)

        if confirmar.exec_() == QtWidgets.QMessageBox.Yes:
            success = False
            if self.tipo_servicio == "Agua":
                success = self.pet_feeder.serve_water()
            else:
                success = self.pet_feeder.serve_food()

            if success:
                self.mostrar_mensaje_info(f"El servicio de {self.tipo_servicio} se ha iniciado correctamente")
            else:
                self.mostrar_mensaje_error(f"Error al iniciar el servicio de {self.tipo_servicio}")

    def iniciar_tiempo(self):
        if not self.pet_feeder.is_esp32_connected():
            self.mostrar_mensaje_error("No hay conexión con el ESP32")
            return

        confirmar = QtWidgets.QMessageBox()
        confirmar.setIcon(QtWidgets.QMessageBox.Question)
        confirmar.setWindowTitle("Confirmar")
        confirmar.setText(f"¿Desea iniciar el dispensador de {self.tipo_servicio} por tiempo?")
        confirmar.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmar.setDefaultButton(QtWidgets.QMessageBox.No)

        if confirmar.exec_() == QtWidgets.QMessageBox.Yes:
            success = False
            if self.tipo_servicio == "Agua":
                success = self.pet_feeder.serve_water()
            else:
                success = self.pet_feeder.serve_food()

            if success:
                self.mostrar_mensaje_info(f"El servicio de {self.tipo_servicio} por tiempo se ha iniciado correctamente")
            else:
                self.mostrar_mensaje_error(f"Error al iniciar el servicio de {self.tipo_servicio} por tiempo")

    def configurar_tiempo(self):
        self.ventana_configurar = SetServiceTimeView.ConfigurarTiempoWindow(self.tipo_servicio)
        self.ventana_configurar.show()

    def mostrar_mensaje_info(self, mensaje):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Información")
        msg.setText(mensaje)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def mostrar_mensaje_error(self, mensaje):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DispensadorAguaWindow()
    window.show()
    sys.exit(app.exec_())