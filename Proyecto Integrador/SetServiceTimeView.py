import sys
from PyQt5 import uic, QtWidgets
from PetFeederController import PetFeederController  # Importamos el controlador

qtCreatorFile = "SetServiceTImeVIew.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class ConfigurarTiempoWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, tipo_servicio="Agua"):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Inicializar el controlador del alimentador
        self.pet_feeder = PetFeederController()

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
    def iniciar_detener(self):
        """Inicia o detiene el servicio"""
        if not self.pet_feeder.is_esp32_connected():
            self.mostrar_mensaje_error("No hay conexión con el ESP32")
            return

        if not self.servicio_iniciado:
            # Iniciar servicio
            success = False
            if self.tipo_servicio == "Agua":
                success = self.pet_feeder.serve_water()
            else:  # Alimento
                success = self.pet_feeder.serve_food()

            if success:
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
                self.mostrar_mensaje_error(f"Error al iniciar el servicio de {self.tipo_servicio}")
        else:
            # Detener servicio
            # Nota: En el código ESP32 no hay un comando específico para detener,
            # pero podríamos implementarlo si es necesario.
            # Por ahora, simplemente cambiamos el estado en la interfaz.
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
            self.mostrar_mensaje_info(f"Servicio de {self.tipo_servicio} detenido")

    def guardar(self):
        """Guarda la configuración de tiempo"""
        # Obtener el tiempo configurado
        # Aquí asumimos que hay un campo de texto o un spinbox para configurar el tiempo
        # Debes ajustar esto según tu interfaz UI
        try:
            if hasattr(self, 'spinBoxTiempo'):
                tiempo_ms = self.spinBoxTiempo.value() * 1000  # Convertir a milisegundos
            elif hasattr(self, 'lineEditTiempo'):
                tiempo_ms = int(self.lineEditTiempo.text()) * 1000
            else:
                # Si no encontramos el control, usamos un valor predeterminado
                tiempo_ms = 3000  # 3 segundos por defecto

            # Crear configuración para enviar al ESP32
            config = {}
            if self.tipo_servicio == "Agua":
                config['dur_serv_agua'] = tiempo_ms
            else:  # Alimento
                config['dur_serv_alim'] = tiempo_ms

            # Enviar configuración al ESP32
            if self.pet_feeder.is_esp32_connected():
                success = self.pet_feeder.update_esp32_config(config)
                if success:
                    self.mostrar_mensaje_info(f"Configuración de tiempo guardada: {tiempo_ms / 1000} segundos")
                    self.close()
                else:
                    self.mostrar_mensaje_error("Error al comunicarse con el ESP32")
            else:
                self.mostrar_mensaje_error("No hay conexión con el ESP32")

        except ValueError as e:
            self.mostrar_mensaje_error(f"Error al guardar configuración: {str(e)}")

    def volver(self):
        self.close()

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
    window = ConfigurarTiempoWindow()
    window.show()
    sys.exit(app.exec_())