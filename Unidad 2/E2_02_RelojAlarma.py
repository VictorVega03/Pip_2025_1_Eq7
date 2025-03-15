import sys
from PyQt5 import uic, QtWidgets, QtCore
qtCreatorFile = "E2_02_RelojAlarma.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.horasR = 0
        self.minutosR = 0
        self.segundosR = 0
        self.horaActual = 0
        self.minutoActual = 0
        self.horaAlarma = 0
        self.minutoAlarma = 0

        # Conexión de botones a sus slots
        self.btn_aceptar.clicked.connect(self.obtenerHoraActual)
        self.btn_iniciar.clicked.connect(self.controlAlarmaSegundoPlano)

        # Configuración del temporizador
        self.alarmaSegundoPlano = QtCore.QTimer()
        self.alarmaSegundoPlano.timeout.connect(self.tiempoRestanteSegundoPlano)

    # Slot para obtener la hora actual
    def obtenerHoraActual(self):
        try:
            self.horaActual = int(self.txt_horas.text())
            self.minutoActual = int(self.txt_minutos.text())
            print(f"Hora actual: {self.horaActual}:{self.minutoActual}")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa valores numéricos válidos para la hora actual.")

    # Slot para obtener la hora de la alarma
    def obtenerAlarma(self):
        try:
            self.horaAlarma = int(self.txt_horaFinal.text())
            self.minutoAlarma = int(self.txt_minutoFinal.text())

            # Cálculo del tiempo restante
            self.horasR = self.horaAlarma - self.horaActual
            self.minutosR = self.minutoAlarma - self.minutoActual

            if self.minutosR < 0:
                self.minutosR += 60
                self.horasR -= 1

            if self.horasR < 0:
                self.horasR += 24

            self.segundosR = 0  # Reiniciar segundos

            print(f"Alarma establecida: {self.horaAlarma}:{self.minutoAlarma}")
            print(f"Tiempo restante: {self.horasR} horas, {self.minutosR} minutos, {self.segundosR} segundos")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Ingresa valores numéricos válidos para la alarma.")

    # Slot para actualizar el tiempo restante
    def tiempoRestanteSegundoPlano(self):
        self.segundosR -= 1

        if self.segundosR < 0:
            self.segundosR = 59
            self.minutosR -= 1

        if self.minutosR < 0:
            self.minutosR = 59
            self.horasR -= 1

        if self.horasR < 0:
            self.horasR = 0
            self.minutosR = 0
            self.segundosR = 0
            self.alarmaSegundoPlano.stop()
            QtWidgets.QMessageBox.information(self, "Alarma", "¡Es hora!")
            return

        # Actualizar la interfaz
        self.txt_horasR.setText(str(self.horasR))
        self.txt_minutosR.setText(str(self.minutosR))
        self.txt_segundosR.setText(str(self.segundosR))

        print(f"Tiempo restante: {self.horasR} horas, {self.minutosR} minutos, {self.segundosR} segundos")

    # Slot para iniciar la alarma
    def controlAlarmaSegundoPlano(self):
        self.obtenerAlarma()
        self.alarmaSegundoPlano.start(1000)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())