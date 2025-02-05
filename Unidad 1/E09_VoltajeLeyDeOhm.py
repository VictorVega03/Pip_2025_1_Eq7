import sys
from PyQt5 import uic, QtWidgets
qtCreatorFile = "E09_VoltajeLeyDeOhm.ui"
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
            I_text = self.txt_I.text()
            R_text = self.txt_R.text()

            if not I_text.isdigit() or not R_text.isdigit():
                self.msj("Por favor, ingrese solo números.")
                return

            b = int(I_text)
            h = int(R_text)
            r = (b * h)
            self.msj("El Voltaje es: " + str(r))
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
