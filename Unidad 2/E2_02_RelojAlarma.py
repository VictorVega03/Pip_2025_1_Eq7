import sys
from PyQt5 import uic, QtWidgets, QtCore
from datetime import datetime, timedelta

qtCreatorFile = 'E2_02_RelojAlarma.ui'  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        try:
            QtWidgets.QMainWindow.__init__(self)
            Ui_MainWindow.__init__(self)
            self.setupUi(self)

            # Área de los Signals
            self.btn_temporizar.clicked.connect(self.temporizar2doPlano)
            self.segundoPlano = QtCore.QTimer()
            self.segundoPlano.timeout.connect(self.controlSegundoPlano)
            self.valorN = -1
        except Exception as e:
            print(f"Error during initialization: {e}")

    # Área de los Slots
    def controlSegundoPlano(self):
        try:
            self.txt_temporizador.setText(str(self.valorN))
            self.valorN -= 1
            if self.valorN == -1:
                self.segundoPlano.stop()
                self.triggerAlarm()
        except Exception as e:
            print(f"Error in controlSegundoPlano: {e}")

    def temporizar2doPlano(self):
        try:
            horas = int(self.txt_horas.text())
            minutos = int(self.txt_minutos.text())
            segundos = int(self.txt_segundos.text())
            target_time = timedelta(hours=horas, minutes=minutos, seconds=seconds)

            current_time = datetime.now().time()
            current_time_delta = timedelta(hours=current_time.hour, minutes=current_time.minute, seconds=current_time.second)

            time_difference = target_time - current_time_delta
            if time_difference.total_seconds() < 0:
                time_difference += timedelta(days=1)  # Adjust for next day

            self.valorN = int(time_difference.total_seconds())
            self.segundoPlano.start(1000)
        except Exception as e:
            print(f"Error in temporizar2doPlano: {e}")

    def triggerAlarm(self):
        try:
            QtWidgets.QMessageBox.information(self, "Alarma", "¡Es la hora de la alarma!")
        except Exception as e:
            print(f"Error in triggerAlarm: {e}")

if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MyApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error during execution: {e}")