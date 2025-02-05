import sys
from PyQt5 import uic, QtWidgets
qtCreatorFile = "P03_EjemploLineEdit.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        #Area de los Signals
        self.btn_Saludar.clicked.connect(self.saludar)

    #Area de los Slots
    def saludar(self):
        cadena = self.txt_nombre.text()
        if cadena != "":
            self.msj("HOLA, " + cadena + " BUENOS DIAS!!  :)")
        else:
            self.msj("PORFAVOR INGRESE SU NOMBRE: ")



    def msj(self, txt):
        m = QtWidgets.QMessageBox()
        m.setText(txt)
        m.exec_()
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
