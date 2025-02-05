import sys
from PyQt5 import uic, QtWidgets
qtCreatorFile = "P01_EjemploBoton.ui"
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
        print("HOLA, BUENOS DIAS")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
