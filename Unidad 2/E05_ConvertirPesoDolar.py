import sys
from PyQt5 import uic, QtWidgets

# Cargar la interfaz creada en Qt Designer
qtCreatorFile = "E05_ConvertirPesoDolar.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_convertir.clicked.connect(self.calcular)

    def calcular(self):
        try:
            cantidad_text = self.txt_cantidad.text()

            # Validar que sean números enteros o decimales
            try:
                cantidad = float(cantidad_text)

            except ValueError:
                self.mostrar_mensaje("Por favor, ingrese un número entero o decimal.")
                return
            dolares = cantidad / 20.68
            self.txt_res.setText(f"{dolares:.2f}")

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