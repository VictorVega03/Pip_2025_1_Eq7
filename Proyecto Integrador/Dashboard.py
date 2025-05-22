import sys
from PyQt5 import uic, QtWidgets, QtGui, QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FiguraCanvas
import ServiceHistoryView
import SelectServiceView
from PetFeederController import PetFeederController

qtCreatorFile = "Dashboard.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.pet_feeder = PetFeederController()
        self.estado_grafica = 0  # 0 = nivel, 1 = historial

        # Conectar señales
        self.btnHistorial.clicked.connect(self.mostrar_historial)
        self.btnDispensador.clicked.connect(self.mostrar_dispensador)
        self.btnCambiarGrafica.clicked.connect(self.alternar_grafica)

        if hasattr(self, 'btnActualizarEstado'):
            self.btnActualizarEstado.clicked.connect(self.actualizar_estado)

        # Agregar botones de configuración
        if not hasattr(self, 'btnConfigWiFi'):
            self.btnConfigWiFi = QtWidgets.QPushButton("Config. WiFi", self)
            if hasattr(self, 'horizontalLayout'):
                self.horizontalLayout.addWidget(self.btnConfigWiFi)
            self.btnConfigWiFi.clicked.connect(self.mostrar_config_wifi)

        if not hasattr(self, 'btnConfigESP32'):
            self.btnConfigESP32 = QtWidgets.QPushButton("Config. ESP32", self)
            if hasattr(self, 'horizontalLayout'):
                self.horizontalLayout.addWidget(self.btnConfigESP32)
            self.btnConfigESP32.clicked.connect(self.mostrar_config_esp32)

        self.inicializar_graficas()
        self.actualizar_estado()
        self.mostrar_graficas_nivel()

        # Timer para actualización automática
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.actualizar_estado)
        self.timer.start(30000)

        # Mostrar IP en barra de estado
        if hasattr(self, 'statusbar') and self.pet_feeder.is_esp32_connected():
            self.statusbar.showMessage(f"Conectado a ESP32: {self.pet_feeder.config['esp32_ip']}")

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

    def mostrar_historial(self):
        self.ventana_historial = ServiceHistoryView.HistorialServiciosWindow()
        self.ventana_historial.show()

    def mostrar_dispensador(self):
        self.ventana_dispensador = SelectServiceView.DispensadorWindow()
        self.ventana_dispensador.show()

    def mostrar_config_wifi(self):
        QtWidgets.QMessageBox.information(
            self,
            "Información",
            "La configuración WiFi se realiza directamente en el código del ESP32.\n"
            "Por favor consulte la documentación para más detalles."
        )

    def mostrar_config_esp32(self):
        from ESP32ConfigDialog import show_esp32_config_dialog

        if not self.pet_feeder.is_esp32_connected():
            QtWidgets.QMessageBox.warning(
                self,
                "Error de conexión",
                "No hay conexión con el ESP32. No se puede configurar."
            )
            return

        if show_esp32_config_dialog(self, self.pet_feeder):
            self.actualizar_estado()

    def alternar_grafica(self):
        if self.estado_grafica == 0:
            self.mostrar_graficas_historial()
            self.estado_grafica = 1
            self.btnCambiarGrafica.setText("Ver Niveles")
        else:
            self.mostrar_graficas_nivel()
            self.estado_grafica = 0
            self.btnCambiarGrafica.setText("Ver Consumo")

    def actualizar_estado(self):
        if self.pet_feeder.is_esp32_connected():
            self.pet_feeder.update_status()

            nivel_agua = self.pet_feeder.get_water_level()
            nivel_comida = self.pet_feeder.get_food_level()

            self.lineEditCantidadRestanteAgua.setText(f"{nivel_agua}%")
            self.lineEditCantidadRestanteAlimento.setText(f"{nivel_comida}%")

            consumo_agua, consumo_comida = self.pet_feeder.get_daily_consumption()
            self.lineEditConsumoEstimadoAgua.setText(f"{consumo_agua} ml/día")
            self.lineEditConsumoEstimadoAlimento.setText(f"{consumo_comida} g/día")

            if self.estado_grafica == 0:
                self.mostrar_graficas_nivel()

            if hasattr(self, 'statusbar'):
                self.statusbar.showMessage(f"Conectado a ESP32: {self.pet_feeder.config['esp32_ip']}")
        else:
            self.pet_feeder.connect_to_esp32()

            if not self.pet_feeder.is_esp32_connected():
                if hasattr(self, 'statusbar'):
                    self.statusbar.showMessage("Sin conexión con ESP32")

    def inicializar_graficas(self):
        # Configurar canvas para agua
        self.figure_agua = plt.figure(figsize=(4, 3))
        self.canvas_agua = FiguraCanvas(self.figure_agua)
        layout_agua = QtWidgets.QVBoxLayout(self.frameGraficaComida_2)
        layout_agua.addWidget(self.canvas_agua)
        self.ax_agua = self.figure_agua.add_subplot(111)

        # Configurar canvas para comida
        self.figure_comida = plt.figure(figsize=(4, 3))
        self.canvas_comida = FiguraCanvas(self.figure_comida)
        layout_comida = QtWidgets.QVBoxLayout(self.frameGraficaComida)
        layout_comida.addWidget(self.canvas_comida)
        self.ax_comida = self.figure_comida.add_subplot(111)

    def mostrar_graficas_nivel(self):
        try:
            nivel_agua = int(self.lineEditCantidadRestanteAgua.text().replace('%', '').strip())
            nivel_comida = int(self.lineEditCantidadRestanteAlimento.text().replace('%', '').strip())

            # Gráfica agua
            self.ax_agua.clear()
            self.ax_agua.bar(['Nivel actual'], [nivel_agua], color='blue', width=0.4)
            self.ax_agua.set_ylim(0, 100)
            self.ax_agua.set_title('Nivel de Agua')
            self.ax_agua.axhline(y=20, color='red', linestyle='--')
            self.ax_agua.text(0, nivel_agua + 5, f"{nivel_agua}%", ha='center')
            self.figure_agua.tight_layout()
            self.canvas_agua.draw()

            # Gráfica comida
            self.ax_comida.clear()
            self.ax_comida.bar(['Nivel actual'], [nivel_comida], color='orange', width=0.4)
            self.ax_comida.set_ylim(0, 100)
            self.ax_comida.set_title('Nivel de Alimento')
            self.ax_comida.axhline(y=20, color='red', linestyle='--')
            self.ax_comida.text(0, nivel_comida + 5, f"{nivel_comida}%", ha='center')
            self.figure_comida.tight_layout()
            self.canvas_comida.draw()

            self.labelGraficaAgua.setText("Gráfica de Nivel de Agua")
            self.labelGraficaComida.setText("Gráfica de Nivel de Alimento")
        except (ValueError, AttributeError) as e:
            print(f"Error al mostrar gráficas de nivel: {e}")
            nivel_agua = self.pet_feeder.get_water_level()
            nivel_comida = self.pet_feeder.get_food_level()

    def mostrar_graficas_historial(self):
        dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

        # Verificar datos del ESP32
        datos_reales = False
        if self.pet_feeder.is_esp32_connected():
            status = self.pet_feeder.esp32.get_status()
            if status and 'estadisticas' in status:
                pass

        # Usar estimaciones si no hay datos reales
        if not datos_reales:
            try:
                consumo_agua_txt = self.lineEditConsumoEstimadoAgua.text().split()[0]
                consumo_comida_txt = self.lineEditConsumoEstimadoAlimento.text().split()[0]

                consumo_agua_base = int(consumo_agua_txt)
                consumo_comida_base = int(consumo_comida_txt)
            except (ValueError, AttributeError, IndexError):
                consumo_agua_base = 600
                consumo_comida_base = 750

            # Generar variaciones para la semana
            import random
            random.seed(42)

            consumo_agua = [max(0, consumo_agua_base + random.randint(-50, 50)) for _ in range(7)]
            consumo_comida = [max(0, consumo_comida_base + random.randint(-50, 50)) for _ in range(7)]

        # Gráfica historial agua
        self.ax_agua.clear()
        barras_agua = self.ax_agua.bar(dias, consumo_agua, color='blue', width=0.6)
        self.ax_agua.set_title('Consumo de Agua (ml/día)')
        for barra in barras_agua:
            altura = barra.get_height()
            self.ax_agua.text(barra.get_x() + barra.get_width() / 2., altura + 5,
                              f'{int(altura)}', ha='center', va='bottom')
        self.figure_agua.tight_layout()
        self.canvas_agua.draw()

        # Gráfica historial comida
        self.ax_comida.clear()
        barras_comida = self.ax_comida.bar(dias, consumo_comida, color='orange', width=0.6)
        self.ax_comida.set_title('Consumo de Alimento (g/día)')
        for barra in barras_comida:
            altura = barra.get_height()
            self.ax_comida.text(barra.get_x() + barra.get_width() / 2., altura + 5,
                                f'{int(altura)}', ha='center', va='bottom')
        self.figure_comida.tight_layout()
        self.canvas_comida.draw()

        self.labelGraficaAgua.setText("Historial de Consumo de Agua")
        self.labelGraficaComida.setText("Historial de Consumo de Alimento")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())