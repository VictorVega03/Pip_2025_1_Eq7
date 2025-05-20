import sys
from PyQt5 import QtWidgets, QtCore, QtGui


class ESP32ConfigDialog(QtWidgets.QDialog):
    """
    Diálogo para configurar parámetros del ESP32.
    Permite modificar la configuración que se envía al endpoint /config.
    """

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)

        self.controller = controller
        if not self.controller:
            from PetFeederController import PetFeederController
            self.controller = PetFeederController()

        self.setWindowTitle("Configuración del ESP32")
        self.setMinimumWidth(500)

        # Crear layout principal
        layout = QtWidgets.QVBoxLayout(self)

        # Mostrar estado de conexión al ESP32
        connection_layout = QtWidgets.QHBoxLayout()
        connection_label = QtWidgets.QLabel("Estado de conexión:", self)
        connection_layout.addWidget(connection_label)

        self.connection_status = QtWidgets.QLabel(self)
        if self.controller.is_esp32_connected():
            self.connection_status.setText(f"Conectado a {self.controller.esp32.ip_address}")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.connection_status.setText("Desconectado")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        connection_layout.addWidget(self.connection_status)

        # Botón para probar conexión
        self.test_connection_btn = QtWidgets.QPushButton("Probar conexión", self)
        self.test_connection_btn.clicked.connect(self.test_connection)
        connection_layout.addWidget(self.test_connection_btn)

        layout.addLayout(connection_layout)

        # Línea separadora
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        # Obtener configuración actual
        current_config = self._get_current_config()

        # Crear grupo de dispensador de alimento
        food_group = QtWidgets.QGroupBox("Dispensador de Alimento", self)
        food_layout = QtWidgets.QFormLayout(food_group)

        # Duración servicio alimento (mostrar en segundos con 1 decimal)
        self.food_duration = QtWidgets.QDoubleSpinBox(self)
        self.food_duration.setRange(0.1, 10.0)  # 0.1s a 10s
        self.food_duration.setSingleStep(0.1)
        self.food_duration.setDecimals(1)
        self.food_duration.setSuffix(" s")
        # Convertir de ms a segundos con 1 decimal
        food_duration_s = current_config.get('dur_serv_alim', 3000) / 1000.0
        self.food_duration.setValue(food_duration_s)
        food_layout.addRow("Duración servicio:", self.food_duration)
        # Agregar tooltip explicativo
        self.food_duration.setToolTip("Tiempo que el motor dispensador de alimento estará activo en cada servicio")

        # Intervalo alimentación automática
        self.food_interval = QtWidgets.QSpinBox(self)
        self.food_interval.setRange(0, 86400)  # 0s a 24h
        self.food_interval.setSingleStep(3600)  # Incrementos de 1h
        self.food_interval.setSuffix(" s")
        self.food_interval.setSpecialValueText("Desactivado")  # 0 = desactivado
        self.food_interval.setValue(current_config.get('intv_alim', 0) // 1000)  # Convertir ms a s
        food_layout.addRow("Intervalo alimentación:", self.food_interval)
        self.food_interval.setToolTip("Intervalo de tiempo para la alimentación automática (0 = desactivado)")

        # Umbral nivel bajo
        self.food_threshold = QtWidgets.QSpinBox(self)
        self.food_threshold.setRange(5, 50)  # 5% a 50%
        self.food_threshold.setSuffix(" %")
        self.food_threshold.setValue(current_config.get('umbral_alim', 15))
        food_layout.addRow("Umbral nivel bajo:", self.food_threshold)
        self.food_threshold.setToolTip("Nivel mínimo de alimento para generar alerta")

        layout.addWidget(food_group)

        # Crear grupo de dispensador de agua
        water_group = QtWidgets.QGroupBox("Dispensador de Agua", self)
        water_layout = QtWidgets.QFormLayout(water_group)

        # Duración servicio agua (mostrar en segundos con 1 decimal)
        self.water_duration = QtWidgets.QDoubleSpinBox(self)
        self.water_duration.setRange(0.1, 10.0)  # 0.1s a 10s
        self.water_duration.setSingleStep(0.1)
        self.water_duration.setDecimals(1)
        self.water_duration.setSuffix(" s")
        # Convertir de ms a segundos con 1 decimal
        water_duration_s = current_config.get('dur_serv_agua', 3000) / 1000.0
        self.water_duration.setValue(water_duration_s)
        water_layout.addRow("Duración servicio:", self.water_duration)
        self.water_duration.setToolTip("Tiempo que la válvula de agua estará abierta en cada servicio")

        # Intervalo cambio agua
        self.water_change_interval = QtWidgets.QSpinBox(self)
        self.water_change_interval.setRange(0, 30)  # 0 a 30 días
        self.water_change_interval.setSingleStep(1)
        self.water_change_interval.setSuffix(" días")
        self.water_change_interval.setSpecialValueText("Desactivado")  # 0 = desactivado
        # Convertir ms a días
        days_value = current_config.get('intv_cambio_agua', 0) // (86400 * 1000)
        self.water_change_interval.setValue(days_value)
        water_layout.addRow("Recordatorio cambio:", self.water_change_interval)
        self.water_change_interval.setToolTip("Intervalo para recordatorio de cambio de agua (0 = desactivado)")

        # Umbral nivel bajo
        self.water_threshold = QtWidgets.QSpinBox(self)
        self.water_threshold.setRange(5, 50)  # 5% a 50%
        self.water_threshold.setSuffix(" %")
        self.water_threshold.setValue(current_config.get('umbral_agua', 20))
        water_layout.addRow("Umbral nivel bajo:", self.water_threshold)
        self.water_threshold.setToolTip("Nivel mínimo de agua para generar alerta o activar el rellenado automático")

        # Auto-relleno agua
        self.water_auto_refill = QtWidgets.QCheckBox("Activado", self)
        self.water_auto_refill.setChecked(current_config.get('auto_refill_agua', True))
        water_layout.addRow("Auto-rellenar agua:", self.water_auto_refill)
        self.water_auto_refill.setToolTip("Activa el rellenado automático del comedero cuando se detecta bajo nivel")

        layout.addWidget(water_group)

        # Crear grupo de sensores
        sensor_group = QtWidgets.QGroupBox("Sensores", self)
        sensor_layout = QtWidgets.QFormLayout(sensor_group)

        # Umbral sensor agua en comedero
        self.water_slot_threshold = QtWidgets.QSpinBox(self)
        self.water_slot_threshold.setRange(0, 4095)  # Rango ADC para ESP32
        self.water_slot_threshold.setSingleStep(100)
        self.water_slot_threshold.setValue(current_config.get('umbral_agua_slot', 1000))
        sensor_layout.addRow("Umbral sensor agua:", self.water_slot_threshold)
        self.water_slot_threshold.setToolTip("Valor ADC para determinar si hay agua en el comedero (0-4095)")

        layout.addWidget(sensor_group)

        # Botones
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save |
            QtWidgets.QDialogButtonBox.Cancel |
            QtWidgets.QDialogButtonBox.Reset,
            QtCore.Qt.Horizontal,
            self
        )

        buttons.accepted.connect(self.save_config)
        buttons.rejected.connect(self.reject)
        # Conectar el botón Reset para restaurar valores predeterminados
        reset_button = buttons.button(QtWidgets.QDialogButtonBox.Reset)
        reset_button.clicked.connect(self.reset_defaults)

        layout.addWidget(buttons)

    def test_connection(self):
        """Prueba la conexión con el ESP32 y actualiza el estado"""
        if self.controller.is_esp32_connected():
            # Intentar obtener datos para verificar comunicación
            status = self.controller.esp32.get_status()
            if status:
                self.connection_status.setText(f"Conectado a {self.controller.esp32.ip_address}")
                self.connection_status.setStyleSheet("color: green; font-weight: bold;")
                QtWidgets.QMessageBox.information(
                    self,
                    "Conexión exitosa",
                    f"Conectado correctamente al ESP32 en {self.controller.esp32.ip_address}.\n"
                    f"Nivel de agua: {status.get('nivel_agua', 'N/A')}%\n"
                    f"Nivel de alimento: {status.get('nivel_alimento', 'N/A')}%"
                )
            else:
                self.connection_status.setText("Error de comunicación")
                self.connection_status.setStyleSheet("color: orange; font-weight: bold;")
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error de comunicación",
                    "Se estableció conexión con el ESP32 pero no se pudieron obtener datos."
                )
        else:
            # Intentar reconectar
            if self.controller.connect_to_esp32():
                self.connection_status.setText(f"Conectado a {self.controller.esp32.ip_address}")
                self.connection_status.setStyleSheet("color: green; font-weight: bold;")
                QtWidgets.QMessageBox.information(
                    self,
                    "Conexión exitosa",
                    f"Conectado correctamente al ESP32 en {self.controller.esp32.ip_address}."
                )
            else:
                self.connection_status.setText("Desconectado")
                self.connection_status.setStyleSheet("color: red; font-weight: bold;")
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error de conexión",
                    "No se pudo conectar con el ESP32. Verifique que esté encendido y en la misma red."
                )

    def _get_current_config(self):
        """Obtiene la configuración actual del ESP32"""
        if not self.controller.is_esp32_connected():
            # Si no hay conexión, usar valores por defecto
            return {
                'dur_serv_alim': 3000,
                'dur_serv_agua': 3000,
                'intv_alim': 12 * 3600 * 1000,  # 12 horas en ms
                'intv_cambio_agua': 3 * 24 * 3600 * 1000,  # 3 días en ms
                'umbral_agua': 20,
                'umbral_alim': 15,
                'umbral_agua_slot': 1000,
                'auto_refill_agua': True
            }

        # Intentar obtener la configuración actual
        status = self.controller.esp32.get_status()
        if not status:
            # Si no se puede obtener el estado, usar valores por defecto
            return {
                'dur_serv_alim': 3000,
                'dur_serv_agua': 3000,
                'intv_alim': 12 * 3600 * 1000,
                'intv_cambio_agua': 3 * 24 * 3600 * 1000,
                'umbral_agua': 20,
                'umbral_alim': 15,
                'umbral_agua_slot': 1000,
                'auto_refill_agua': True
            }

        # Extraer configuración del estado
        config = {}
        if 'config' in status:
            config = status['config']
        else:
            # Si no hay sección config, usar valores predeterminados
            config = {
                'dur_serv_alim': 3000,
                'dur_serv_agua': 3000,
                'intv_alim': 12 * 3600 * 1000,
                'intv_cambio_agua': 3 * 24 * 3600 * 1000,
                'umbral_agua': 20,
                'umbral_alim': 15,
                'umbral_agua_slot': 1000,
                'auto_refill_agua': True
            }

        return config

    def reset_defaults(self):
        """Restaura los valores predeterminados"""
        # Valores predeterminados
        defaults = {
            'dur_serv_alim': 3.0,  # 3 segundos
            'dur_serv_agua': 3.0,  # 3 segundos
            'intv_alim': 12 * 3600,  # 12 horas en segundos
            'intv_cambio_agua': 3,  # 3 días
            'umbral_agua': 20,
            'umbral_alim': 15,
            'umbral_agua_slot': 1000,
            'auto_refill_agua': True
        }

        # Actualizar controles
        self.food_duration.setValue(defaults['dur_serv_alim'])
        self.water_duration.setValue(defaults['dur_serv_agua'])
        self.food_interval.setValue(defaults['intv_alim'])
        self.water_change_interval.setValue(defaults['intv_cambio_agua'])
        self.food_threshold.setValue(defaults['umbral_alim'])
        self.water_threshold.setValue(defaults['umbral_agua'])
        self.water_slot_threshold.setValue(defaults['umbral_agua_slot'])
        self.water_auto_refill.setChecked(defaults['auto_refill_agua'])

    def save_config(self):
        """Guarda la configuración en el ESP32"""
        if not self.controller.is_esp32_connected():
            QtWidgets.QMessageBox.warning(
                self,
                "Error de conexión",
                "No hay conexión con el ESP32. No se puede guardar la configuración."
            )
            return

        # Convertir duraciones de segundos a milisegundos
        food_duration_ms = int(self.food_duration.value() * 1000)
        water_duration_ms = int(self.water_duration.value() * 1000)

        # Crear diccionario de configuración
        config = {
            'dur_serv_alim': food_duration_ms,  # De segundos a ms
            'dur_serv_agua': water_duration_ms,  # De segundos a ms
            'intv_alim': self.food_interval.value() * 1000,  # Convertir a ms
            'intv_cambio_agua': self.water_change_interval.value() * 86400 * 1000,  # Convertir a ms
            'umbral_agua': self.water_threshold.value(),
            'umbral_alim': self.food_threshold.value(),
            'umbral_agua_slot': self.water_slot_threshold.value(),
            'auto_refill_agua': self.water_auto_refill.isChecked()
        }

        # Mostrar diálogo de confirmación
        confirm_msg = (
            "Se enviará la siguiente configuración al ESP32:\n\n"
            f"• Duración servicio alimento: {self.food_duration.value()} s ({food_duration_ms} ms)\n"
            f"• Duración servicio agua: {self.water_duration.value()} s ({water_duration_ms} ms)\n"
            f"• Intervalo alimentación: {self.food_interval.value()} segundos\n"
            f"• Intervalo cambio agua: {self.water_change_interval.value()} días\n"
            f"• Umbral nivel bajo agua: {config['umbral_agua']}%\n"
            f"• Umbral nivel bajo alimento: {config['umbral_alim']}%\n"
            f"• Umbral sensor agua: {config['umbral_agua_slot']} (ADC)\n"
            f"• Auto-rellenar agua: {'Activado' if config['auto_refill_agua'] else 'Desactivado'}\n\n"
            "¿Confirma estos valores?"
        )
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirmar configuración",
            confirm_msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if confirm != QtWidgets.QMessageBox.Yes:
            return

        # Mostrar diálogo de progreso
        progress = QtWidgets.QProgressDialog("Enviando configuración al ESP32...", "Cancelar", 0, 100, self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setAutoClose(True)
        progress.setValue(20)
        progress.show()
        QtWidgets.QApplication.processEvents()

        # Enviar configuración al ESP32
        success = self.controller.update_esp32_config(config)

        progress.setValue(80)
        QtWidgets.QApplication.processEvents()

        if success:
            progress.setValue(100)
            QtWidgets.QApplication.processEvents()
            QtWidgets.QMessageBox.information(
                self,
                "Configuración guardada",
                "La configuración se ha guardado correctamente en el ESP32."
            )
            self.accept()
        else:
            progress.setValue(100)
            QtWidgets.QApplication.processEvents()
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                "No se pudo guardar la configuración en el ESP32."
            )

        progress.close()


# Función para mostrar el diálogo desde cualquier parte del código
def show_esp32_config_dialog(parent=None, controller=None):
    """
    Muestra el diálogo de configuración del ESP32.

    Args:
        parent (QWidget): Widget padre
        controller (PetFeederController): Instancia del controlador

    Returns:
        bool: True si se guardó la configuración, False en caso contrario
    """
    dialog = ESP32ConfigDialog(parent, controller)
    result = dialog.exec_()
    return result == QtWidgets.QDialog.Accepted


if __name__ == "__main__":
    # Prueba del diálogo
    app = QtWidgets.QApplication(sys.argv)
    show_esp32_config_dialog()
    sys.exit(0)