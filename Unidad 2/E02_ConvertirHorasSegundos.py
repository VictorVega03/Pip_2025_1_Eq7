import sys
from PyQt5 import uic, QtWidgets

# Cargar la interfaz creada en Qt Designer
qtCreatorFile = "E02_ConvertirHorasSegundos.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Conectar botón con la función de cálculo
        self.btn_convertir.clicked.connect(self.calcular)

    def calcular(self):
        try:
            # Obtener valores de los campos
            horas_text = self.txt_horas.text()
            minutos_text = self.txt_min.text()
            segundos_text = self.txt_seg.text()

            # Validar que sean números
            if not (horas_text.isdigit() and minutos_text.isdigit() and segundos_text.isdigit()):
                self.mostrar_mensaje("Por favor, ingrese solo números enteros.")
                return

            # Convertir a enteros
            horas = int(horas_text)
            minutos = int(minutos_text)
            segundos = int(segundos_text)

            # Validar rangos correctos
            if not (0 <= horas < 24 and 0 <= minutos < 60 and 0 <= segundos < 60):
                self.mostrar_mensaje("Ingrese valores válidos: horas (0-23), minutos y segundos (0-59).")
                return

            # Calcular segundos totales
            total_segundos = (horas * 3600) + (minutos * 60) + segundos
            self.txt_res.setText(str(total_segundos))

        except Exception as error:
            print(error)
            self.mostrar_mensaje("Error Desconocido.")

    def mostrar_mensaje(self, mensaje):
        msg = QtWidgets.QMessageBox()
        msg.setText(mensaje)
        msg.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
