import sys
from PyQt5 import uic, QtWidgets
# qtCreatorFile = "P04_LoadImage-V5-PixMap.ui"
# Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

import P2_Python_Ejemplo as interfaz # importa el modulo que tiene la clase con la interfaz
class MyApp(QtWidgets.QMainWindow, interfaz.Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        interfaz.Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Área de los Signals
        self.btn_sumar.clicked.connect(self.sumar)

    # Área de los Slots
    def sumar(self):
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
