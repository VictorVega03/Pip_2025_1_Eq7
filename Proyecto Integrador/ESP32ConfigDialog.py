import sys
from PyQt5 import QtWidgets, QtCore, QtGui


class ESP32ConfigDialog(QtWidgets.QDialog):
    """Diálogo para configurar parámetros del ESP32"""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)

        self.controller = controller
        if not self.controller:
            from PetFeederController import PetFeederController
            self.controller = PetFeederController()

        self.setWindowTitle("Configuración del ESP32")
        self.setMinimumWidth(500)

        layout = QtWidgets.QVBoxLayout(self)

        # Estado de conexión
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

        self.test_connection_btn = QtWidgets.QPushButton("Probar conexión", self)
        self.test_connection_btn.clicked.connect(self.test_connection)
        connection_layout.addWidget(self.test_connection_btn)

        layout.addLayout(connection_layout)

        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        current_config = self._get_current_config()

        # Grupo dispensador de alimento
        food_group = QtWidgets.QGroupBox("Dispensador de Alimento", self)
        food_layout = QtWidgets.QFormLayout(food_group)

        self.food_duration = QtWidgets.QDoubleSpinBox(self)
        self.food_duration.setRange(0.1, 10.0)
        self.food_duration.setSingleStep(0.1)
        self.food_duration.setDecimals(1)
        self.food_duration.setSuffix(" s")
        food_duration_s = current_config.get('dur_serv_alim', 3000) / 1000.0
        self.food_duration.setValue(food_duration_s)
        food_layout.addRow("Duración servicio:", self.food_duration)
        self.food_duration.setToolTip("Tiempo que el motor dispensador de alimento estará activo en cada servicio")

        self.food_interval = QtWidgets.QSpinBox(self)
        self.food_interval.setRange(0, 86400)
        self.food_interval.setSingleStep(3600)
        self.food_interval.setSuffix(" s")
        self.food_interval.setSpecialValueText("Desactivado")
        self.food_interval.setValue(current_config.get('intv_alim', 0) // 1000)
        food_layout.addRow("Intervalo alimentación:", self.food_interval)
        self.food_interval.setToolTip("Intervalo de tiempo para la alimentación automática (0 = desactivado)")

        self.food_threshold = QtWidgets.QSpinBox(self)
        self.food_threshold.setRange(5, 50)
        self.food_threshold.setSuffix(" %")
        self.food_threshold.setValue(current_config.get('umbral_alim', 15))
        food_layout.addRow("Umbral nivel bajo:", self.food_threshold)
        self.food_threshold.setToolTip("Nivel mínimo de alimento para generar alerta")

        layout.addWidget(food_group)

        # Grupo dispensador de agua
        water_group = QtWidgets.QGroupBox("Dispensador de Agua", self)
        water_layout = QtWidgets.QFormLayout(water_group)

        self.water_duration = QtWidgets.QDoubleSpinBox(self)
        self.water_duration.setRange(0.1, 10.0)
        self.water_duration.setSingleStep(0.1)
        self.water_duration.setDecimals(1)
        self.water_duration.setSuffix(" s")
        water_duration_s = current_config.get('dur_serv_agua', 3000) / 1000.0
        self.water_duration.setValue(water_duration_s)
        water_layout.addRow("Duración servicio:", self.water_duration)
        self.water_duration.setToolTip("Tiempo que la válvula de agua estará abierta en cada servicio")

        self.water_change_interval = QtWidgets.QSpinBox(self)
        self.water_change_interval.setRange(0, 30)
        self.water_change_interval.setSingleStep(1)
        self.water_change_interval.setSuffix(" días")
        self.water_change_interval.setSpecialValueText("Desactivado")
        days_value = current_config.get('intv_cambio_agua', 0) // (86400 * 1000)
        self.water_change_interval.setValue(days_value)
        water_layout.addRow("Recordatorio cambio:", self.water_change_interval)
        self.water_change_interval.setToolTip("Intervalo para recordatorio de cambio de agua (0 = desactivado)")

        self.water_threshold = QtWidgets.QSpinBox(self)
        self.water_threshold.setRange(5, 50)
        self.water_threshold.setSuffix(" %")
        self.water_threshold.setValue(current_config.get('umbral_agua', 20))
        water_layout.addRow("Umbral nivel bajo:", self.water_threshold)
        self.water_threshold.setToolTip("Nivel mínimo de agua para generar alerta o activar el rellenado automático")

        self.water_auto_refill = QtWidgets.QCheckBox("Activado", self)
        self.water_auto_refill.setChecked(current_config.get('auto_refill_agua', True))
        water_layout.addRow("Auto-rellenar agua:", self.water_auto_refill)
        self.water_auto_refill.setToolTip("Activa el rellenado automático del comedero cuando se detecta bajo nivel")

        layout.addWidget(water_group)

        # Grupo sensores
        sensor_group = QtWidgets.QGroupBox("Sensores", self)
        sensor_layout = QtWidgets.QFormLayout(sensor_group)

        self.water_slot_threshold = QtWidgets.QSpinBox(self)
        self.water_slot_threshold.setRange(0, 4095)
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
        reset_button = buttons.button(QtWidgets.QDialogButtonBox.Reset)
        reset_button.clicked.connect(self.reset_defaults)

        layout.addWidget(buttons)

    def test_connection(self):
        if self.controller.is_esp32_connected():
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
        if not self.controller.is_esp32_connected():
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

        status = self.controller.esp32.get_status()
        if not status:
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

        config = {}
        if 'config' in status:
            config = status['config']
        else:
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
        defaults = {
            'dur_serv_alim': 3.0,
            'dur_serv_agua': 3.0,
            'intv_alim': 12 * 3600,
            'intv_cambio_agua': 3,
            'umbral_agua': 20,
            'umbral_alim': 15,
            'umbral_agua_slot': 1000,
            'auto_refill_agua': True
        }

        self.food_duration.setValue(defaults['dur_serv_alim'])
        self.water_duration.setValue(defaults['dur_serv_agua'])
        self.food_interval.setValue(defaults['intv_alim'])
        self.water_change_interval.setValue(defaults['intv_cambio_agua'])
        self.food_threshold.setValue(defaults['umbral_alim'])
        self.water_threshold.setValue(defaults['umbral_agua'])
        self.water_slot_threshold.setValue(defaults['umbral_agua_slot'])
        self.water_auto_refill.setChecked(defaults['auto_refill_agua'])

    def save_config(self):
        if not self.controller.is_esp32_connected():
            QtWidgets.QMessageBox.warning(
                self,
                "Error de conexión",
                "No hay conexión con el ESP32. No se puede guardar la configuración."
            )
            return

        food_duration_ms = int(self.food_duration.value() * 1000)
        water_duration_ms = int(self.water_duration.value() * 1000)

        config = {
            'dur_serv_alim': food_duration_ms,
            'dur_serv_agua': water_duration_ms,
            'intv_alim': self.food_interval.value() * 1000,
            'intv_cambio_agua': self.water_change_interval.value() * 86400 * 1000,
            'umbral_agua': self.water_threshold.value(),
            'umbral_alim': self.food_threshold.value(),
            'umbral_agua_slot': self.water_slot_threshold.value(),
            'auto_refill_agua': self.water_auto_refill.isChecked()
        }

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

        progress = QtWidgets.QProgressDialog("Enviando configuración al ESP32...", "Cancelar", 0, 100, self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setAutoClose(True)
        progress.setValue(20)
        progress.show()
        QtWidgets.QApplication.processEvents()

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


def show_esp32_config_dialog(parent=None, controller=None):
    """Muestra el diálogo de configuración del ESP32"""
    dialog = ESP32ConfigDialog(parent, controller)
    result = dialog.exec_()
    return result == QtWidgets.QDialog.Accepted


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    show_esp32_config_dialog()
    sys.exit(0)