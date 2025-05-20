import sys
from PyQt5 import uic, QtWidgets
from PetFeederController import PetFeederController  # Importamos el controlador

qtCreatorFile = "DetailsServiceView.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DetallesOperacionWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Inicializar el controlador del alimentador
        self.pet_feeder = PetFeederController()

        # Área de los Signals
        self.btnVolver.clicked.connect(self.volver)

        # Si hay botón para repetir operación, conectarlo
        if hasattr(self, 'btnRepetirOperacion'):
            self.btnRepetirOperacion.clicked.connect(self.repetir_operacion)

    # Área de los Slots
    def volver(self):
        self.close()

    def repetir_operacion(self):
        """Repite la operación mostrada en los detalles"""
        if not self.pet_feeder.is_esp32_connected():
            self.mostrar_mensaje_error("No hay conexión con el ESP32")
            return

        # Determinar qué tipo de operación se va a repetir
        tipo_servicio = "desconocido"
        if hasattr(self, 'labelTipoServicio'):
            tipo_servicio = self.labelTipoServicio.text().lower()

        # Mostrar diálogo de confirmación
        confirmar = QtWidgets.QMessageBox()
        confirmar.setIcon(QtWidgets.QMessageBox.Question)
        confirmar.setWindowTitle("Confirmar")
        confirmar.setText(f"¿Desea repetir esta operación de {tipo_servicio}?")
        confirmar.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmar.setDefaultButton(QtWidgets.QMessageBox.No)

        if confirmar.exec_() == QtWidgets.QMessageBox.Yes:
            success = False
            if "agua" in tipo_servicio:
                success = self.pet_feeder.serve_water()
            elif "alimento" in tipo_servicio or "comida" in tipo_servicio:
                success = self.pet_feeder.serve_food()
            else:
                self.mostrar_mensaje_error("Tipo de servicio no reconocido")
                return

            # Mostrar mensaje de resultado
            if success:
                self.mostrar_mensaje_info(f"La operación de {tipo_servicio} se ha repetido correctamente")
            else:
                self.mostrar_mensaje_error(f"Error al repetir la operación de {tipo_servicio}")

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
    window = DetallesOperacionWindow()
    window.show()
    sys.exit(app.exec_())