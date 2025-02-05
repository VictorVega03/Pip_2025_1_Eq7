import sys
from PyQt5 import uic, QtWidgets
qtCreatorFile = "E03_PuntoMedio.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        #Area de los Signals
        self.btn_Calcular.clicked.connect(self.calcular)

    #Area de los Slots
    def calcular(self):
        try:
            a_text = self.txt_A.text()
            b_text = self.txt_B.text()

            if not a_text.isdigit() or not b_text.isdigit():
                self.msj("Por favor, ingrese solo números.")
                return

            a = int(a_text)
            b = int(b_text)
            r = (a + b) / 2
            self.msj("El punto medio es: " + str(r))
        except Exception as error:
            print(error)

    def msj(self, txt):
        m = QtWidgets.QMessageBox()
        m.setText(txt)
        m.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
