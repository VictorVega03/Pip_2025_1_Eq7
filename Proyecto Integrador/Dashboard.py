import sys
from PyQt5 import uic, QtWidgets, QtGui, QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FiguraCanvas
import ServiceHistoryView  # Importamos la vista de historial
import SelectServiceView  # Importamos la vista de selección de servicio
from PetFeederController import PetFeederController  # Importamos el controlador

qtCreatorFile = "Dashboard.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Inicializar el controlador del alimentador
        self.pet_feeder = PetFeederController()

        # Variable para controlar el estado de la gráfica (0 = nivel, 1 = historial)
        self.estado_grafica = 0

        # Área de los Signals
        self.btnHistorial.clicked.connect(self.mostrar_historial)
        self.btnDispensador.clicked.connect(self.mostrar_dispensador)
        self.btnCambiarGrafica.clicked.connect(self.alternar_grafica)

        # Botón de actualizar estados (opcional)
        if hasattr(self, 'btnActualizarEstado'):
            self.btnActualizarEstado.clicked.connect(self.actualizar_estado)

        # Agregar botones de configuración si no existen
        if not hasattr(self, 'btnConfigWiFi'):
            self.btnConfigWiFi = QtWidgets.QPushButton("Config. WiFi", self)
            if hasattr(self, 'horizontalLayout'):  # Asumiendo que hay un layout horizontal
                self.horizontalLayout.addWidget(self.btnConfigWiFi)
            self.btnConfigWiFi.clicked.connect(self.mostrar_config_wifi)

        if not hasattr(self, 'btnConfigESP32'):
            self.btnConfigESP32 = QtWidgets.QPushButton("Config. ESP32", self)
            if hasattr(self, 'horizontalLayout'):  # Asumiendo que hay un layout horizontal
                self.horizontalLayout.addWidget(self.btnConfigESP32)
            self.btnConfigESP32.clicked.connect(self.mostrar_config_esp32)

        # Inicializar las gráficas
        self.inicializar_graficas()

        # Actualizar niveles desde ESP32 si está conectado
        self.actualizar_estado()

        # Mostrar las gráficas iniciales (de nivel)
        self.mostrar_graficas_nivel()

        # Timer para actualizar periódicamente - CORREGIDO: QTimer pertenece a QtCore, no a QtWidgets
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.actualizar_estado)
        self.timer.start(30000)  # Actualizar cada 30 segundos

        # Mostrar dirección IP del ESP32 en la barra de estado
        if hasattr(self, 'statusbar') and self.pet_feeder.is_esp32_connected():
            self.statusbar.showMessage(f"Conectado a ESP32: {self.pet_feeder.config['esp32_ip']}")

    def closeEvent(self, event):
        """Se ejecuta al cerrar la ventana"""
        # Detener el timer
        self.timer.stop()

        # Desconectar del ESP32 si es necesario
        # Comentar si queremos mantener la conexión entre ejecuciones
        # self.pet_feeder.disconnect_from_esp32()

        event.accept()

    # Área de los Slots
    def mostrar_historial(self):
        # Solo abre la ventana de historial, sin cambiar las gráficas
        self.ventana_historial = ServiceHistoryView.HistorialServiciosWindow()
        self.ventana_historial.show()

    def mostrar_dispensador(self):
        self.ventana_dispensador = SelectServiceView.DispensadorWindow()
        self.ventana_dispensador.show()

    def mostrar_config_wifi(self):
        """Muestra diálogo para configurar parámetros WiFi (pendiente de implementar)"""
        QtWidgets.QMessageBox.information(
            self,
            "Información",
            "La configuración WiFi se realiza directamente en el código del ESP32.\n"
            "Por favor consulte la documentación para más detalles."
        )

    def mostrar_config_esp32(self):
        """Muestra diálogo para configurar parámetros del ESP32"""
        from ESP32ConfigDialog import show_esp32_config_dialog

        if not self.pet_feeder.is_esp32_connected():
            QtWidgets.QMessageBox.warning(
                self,
                "Error de conexión",
                "No hay conexión con el ESP32. No se puede configurar."
            )
            return

        # Mostrar diálogo de configuración
        if show_esp32_config_dialog(self, self.pet_feeder):
            # Si se guardó la configuración, actualizar la UI
            self.actualizar_estado()

    def alternar_grafica(self):
        """Alterna entre mostrar gráficas de nivel y gráficas de historial"""
        if self.estado_grafica == 0:
            # Cambiar a gráficas de historial
            self.mostrar_graficas_historial()
            self.estado_grafica = 1
            self.btnCambiarGrafica.setText("Ver Niveles")
        else:
            # Cambiar a gráficas de nivel
            self.mostrar_graficas_nivel()
            self.estado_grafica = 0
            self.btnCambiarGrafica.setText("Ver Consumo")

    def actualizar_estado(self):
        """Actualiza los estados desde el ESP32"""
        if self.pet_feeder.is_esp32_connected():
            self.pet_feeder.update_status()

            # Actualizar niveles en la UI
            nivel_agua = self.pet_feeder.get_water_level()
            nivel_comida = self.pet_feeder.get_food_level()

            # Actualizar campos de texto
            self.lineEditCantidadRestanteAgua.setText(f"{nivel_agua}%")
            self.lineEditCantidadRestanteAlimento.setText(f"{nivel_comida}%")

            # Obtener consumo estimado diario
            consumo_agua, consumo_comida = self.pet_feeder.get_daily_consumption()
            self.lineEditConsumoEstimadoAgua.setText(f"{consumo_agua} ml/día")
            self.lineEditConsumoEstimadoAlimento.setText(f"{consumo_comida} g/día")

            # Si estamos mostrando gráficas de nivel, actualizarlas
            if self.estado_grafica == 0:
                self.mostrar_graficas_nivel()

            # Actualizar barra de estado
            if hasattr(self, 'statusbar'):
                self.statusbar.showMessage(f"Conectado a ESP32: {self.pet_feeder.config['esp32_ip']}")
        else:
            # Intentar conectar
            self.pet_feeder.connect_to_esp32()

            if not self.pet_feeder.is_esp32_connected():
                # Actualizar barra de estado
                if hasattr(self, 'statusbar'):
                    self.statusbar.showMessage("Sin conexión con ESP32")

                # QtWidgets.QMessageBox.warning(self, "Advertencia", "No se pudo conectar con el ESP32")

    def inicializar_graficas(self):
        """Inicializa las figuras y canvas para las gráficas"""
        # Gráfica para agua
        self.figure_agua = plt.figure(figsize=(4, 3))
        self.canvas_agua = FiguraCanvas(self.figure_agua)
        layout_agua = QtWidgets.QVBoxLayout(self.frameGraficaComida_2)
        layout_agua.addWidget(self.canvas_agua)
        self.ax_agua = self.figure_agua.add_subplot(111)

        # Gráfica para comida
        self.figure_comida = plt.figure(figsize=(4, 3))
        self.canvas_comida = FiguraCanvas(self.figure_comida)
        layout_comida = QtWidgets.QVBoxLayout(self.frameGraficaComida)
        layout_comida.addWidget(self.canvas_comida)
        self.ax_comida = self.figure_comida.add_subplot(111)

    def mostrar_graficas_nivel(self):
        """Muestra gráficas de nivel actual para agua y comida"""
        try:
            # Obtener los niveles actuales
            nivel_agua = int(self.lineEditCantidadRestanteAgua.text().replace('%', '').strip())
            nivel_comida = int(self.lineEditCantidadRestanteAlimento.text().replace('%', '').strip())

            # Gráfica de nivel de agua
            self.ax_agua.clear()
            self.ax_agua.bar(['Nivel actual'], [nivel_agua], color='blue', width=0.4)
            self.ax_agua.set_ylim(0, 100)  # Escala de 0 a 100%
            self.ax_agua.set_title('Nivel de Agua')
            self.ax_agua.axhline(y=20, color='red', linestyle='--')  # Línea de nivel bajo
            self.ax_agua.text(0, nivel_agua + 5, f"{nivel_agua}%", ha='center')
            self.figure_agua.tight_layout()
            self.canvas_agua.draw()

            # Gráfica de nivel de comida
            self.ax_comida.clear()
            self.ax_comida.bar(['Nivel actual'], [nivel_comida], color='orange', width=0.4)
            self.ax_comida.set_ylim(0, 100)  # Escala de 0 a 100%
            self.ax_comida.set_title('Nivel de Alimento')
            self.ax_comida.axhline(y=20, color='red', linestyle='--')  # Línea de nivel bajo
            self.ax_comida.text(0, nivel_comida + 5, f"{nivel_comida}%", ha='center')
            self.figure_comida.tight_layout()
            self.canvas_comida.draw()

            # Actualizar etiquetas
            self.labelGraficaAgua.setText("Gráfica de Nivel de Agua")
            self.labelGraficaComida.setText("Gráfica de Nivel de Alimento")
        except (ValueError, AttributeError) as e:
            print(f"Error al mostrar gráficas de nivel: {e}")
            # En caso de error, intentar con valores predeterminados
            nivel_agua = self.pet_feeder.get_water_level()
            nivel_comida = self.pet_feeder.get_food_level()

            # Continuar con las gráficas...
            # (código similar al anterior)

    def mostrar_graficas_historial(self):
        """Muestra gráficas de historial de consumo para agua y comida"""
        # Datos de ejemplo para el historial
        dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

        # Intentar obtener datos reales desde el ESP32
        datos_reales = False
        if self.pet_feeder.is_esp32_connected():
            status = self.pet_feeder.esp32.get_status()

            # Verificar si hay datos de historial en el status
            if status and 'estadisticas' in status:
                # Implementar procesamiento de datos reales si están disponibles
                pass

        # Si no hay datos reales, usar estimaciones
        if not datos_reales:
            # Obtener valores de consumo de los campos de texto
            try:
                consumo_agua_txt = self.lineEditConsumoEstimadoAgua.text().split()[0]  # Extraer el número
                consumo_comida_txt = self.lineEditConsumoEstimadoAlimento.text().split()[0]  # Extraer el número

                consumo_agua_base = int(consumo_agua_txt)
                consumo_comida_base = int(consumo_comida_txt)
            except (ValueError, AttributeError, IndexError):
                # Si hay error de conversión, usar valores predeterminados
                consumo_agua_base = 600
                consumo_comida_base = 750

            # Generar variaciones aleatorias para los días
            import random
            random.seed(42)  # Para reproducibilidad

            consumo_agua = [max(0, consumo_agua_base + random.randint(-50, 50)) for _ in range(7)]
            consumo_comida = [max(0, consumo_comida_base + random.randint(-50, 50)) for _ in range(7)]

        # Gráfica de historial de agua
        self.ax_agua.clear()
        barras_agua = self.ax_agua.bar(dias, consumo_agua, color='blue', width=0.6)
        self.ax_agua.set_title('Consumo de Agua (ml/día)')
        # Añadir etiquetas de valor sobre cada barra
        for barra in barras_agua:
            altura = barra.get_height()
            self.ax_agua.text(barra.get_x() + barra.get_width() / 2., altura + 5,
                              f'{int(altura)}', ha='center', va='bottom')
        self.figure_agua.tight_layout()
        self.canvas_agua.draw()

        # Gráfica de historial de comida
        self.ax_comida.clear()
        barras_comida = self.ax_comida.bar(dias, consumo_comida, color='orange', width=0.6)
        self.ax_comida.set_title('Consumo de Alimento (g/día)')
        # Añadir etiquetas de valor sobre cada barra
        for barra in barras_comida:
            altura = barra.get_height()
            self.ax_comida.text(barra.get_x() + barra.get_width() / 2., altura + 5,
                                f'{int(altura)}', ha='center', va='bottom')
        self.figure_comida.tight_layout()
        self.canvas_comida.draw()

        # Actualizar etiquetas
        self.labelGraficaAgua.setText("Historial de Consumo de Agua")
        self.labelGraficaComida.setText("Historial de Consumo de Alimento")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())