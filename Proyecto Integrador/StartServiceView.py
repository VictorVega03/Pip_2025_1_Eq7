import sys
from PyQt5 import uic, QtWidgets, QtGui  # Importamos QtGui para QPixmap
import SetServiceTimeView  # Importamos la vista de configuración de tiempo
from PetFeederController import PetFeederController  # Importamos el controlador

qtCreatorFile = "StartServiceView.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DispensadorAguaWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, tipo_servicio="Agua"):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Inicializar el controlador del alimentador
        self.pet_feeder = PetFeederController()

        self.tipo_servicio = tipo_servicio
        self.servicio_activo = False

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

        # Verificar conexión con ESP32
        if not self.pet_feeder.is_esp32_connected():
            mensaje = QtWidgets.QMessageBox()
            mensaje.setIcon(QtWidgets.QMessageBox.Warning)
            mensaje.setWindowTitle("Advertencia")
            mensaje.setText("No hay conexión con el ESP32.")
            mensaje.setInformativeText("Algunas funciones podrían no estar disponibles.")
            mensaje.setStandardButtons(QtWidgets.QMessageBox.Ok)
            mensaje.exec_()

    # Área de los Slots
    def volver(self):
        self.close()

    def iniciar_manual(self):
        """Inicia el servicio manualmente (activa el dispensador)"""
        if not self.pet_feeder.is_esp32_connected():
            self.mostrar_mensaje_error("No hay conexión con el ESP32")
            return

        # Mostrar diálogo de confirmación
        confirmar = QtWidgets.QMessageBox()
        confirmar.setIcon(QtWidgets.QMessageBox.Question)
        confirmar.setWindowTitle("Confirmar")
        confirmar.setText(f"¿Desea iniciar el dispensador de {self.tipo_servicio}?")
        confirmar.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmar.setDefaultButton(QtWidgets.QMessageBox.No)

        if confirmar.exec_() == QtWidgets.QMessageBox.Yes:
            # Llamar al método correspondiente según el tipo de servicio
            success = False
            if self.tipo_servicio == "Agua":
                success = self.pet_feeder.serve_water()
            else:  # Alimento
                success = self.pet_feeder.serve_food()

            # Mostrar mensaje de resultado
            if success:
                self.mostrar_mensaje_info(f"El servicio de {self.tipo_servicio} se ha iniciado correctamente")
            else:
                self.mostrar_mensaje_error(f"Error al iniciar el servicio de {self.tipo_servicio}")

    def iniciar_tiempo(self):
        """Inicia el servicio por tiempo (según configuración)"""
        if not self.pet_feeder.is_esp32_connected():
            self.mostrar_mensaje_error("No hay conexión con el ESP32")
            return

        # Mostrar diálogo de confirmación
        confirmar = QtWidgets.QMessageBox()
        confirmar.setIcon(QtWidgets.QMessageBox.Question)
        confirmar.setWindowTitle("Confirmar")
        confirmar.setText(f"¿Desea iniciar el dispensador de {self.tipo_servicio} por tiempo?")
        confirmar.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmar.setDefaultButton(QtWidgets.QMessageBox.No)

        if confirmar.exec_() == QtWidgets.QMessageBox.Yes:
            # Aquí podríamos añadir lógica adicional para el servicio por tiempo
            # Por ahora, simplemente llamamos al mismo método que el manual
            success = False
            if self.tipo_servicio == "Agua":
                success = self.pet_feeder.serve_water()
            else:  # Alimento
                success = self.pet_feeder.serve_food()

            # Mostrar mensaje de resultado
            if success:
                self.mostrar_mensaje_info(
                    f"El servicio de {self.tipo_servicio} por tiempo se ha iniciado correctamente")
            else:
                self.mostrar_mensaje_error(f"Error al iniciar el servicio de {self.tipo_servicio} por tiempo")

    def configurar_tiempo(self):
        """Abre la ventana de configuración de tiempo"""
        self.ventana_configurar = SetServiceTimeView.ConfigurarTiempoWindow(self.tipo_servicio)
        self.ventana_configurar.show()

    def mostrar_mensaje_info(self, mensaje):
        """Muestra un mensaje de información"""
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Información")
        msg.setText(mensaje)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def mostrar_mensaje_error(self, mensaje):
        """Muestra un mensaje de error"""
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