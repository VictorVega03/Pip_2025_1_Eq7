import sys
from PyQt5 import uic, QtWidgets

# Cargar la interfaz creada en Qt Designer
qtCreatorFile = "E06_AreaPentagono.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_calcular.clicked.connect(self.calcular)

    def calcular(self):
        try:
            lado_text = self.txt_lado.text()
            apotema_text = self.txt_apotema.text()

            # Validar que sean números enteros o decimales
            try:
                lado = float(lado_text)
                apotema = float(apotema_text)

                if lado <= 0 or apotema <= 0:
                    self.mostrar_mensaje("Por favor, ingrese un número positivo.")
                    return

            except ValueError:
                self.mostrar_mensaje("Por favor, ingrese un número entero o decimal.")
                return

            # Calcular el área
            area = 5 * lado * apotema / 2
            self.txt_res.setText(f"{area:.2f}")

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