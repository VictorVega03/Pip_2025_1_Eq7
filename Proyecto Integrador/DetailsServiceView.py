import sys
from PyQt5 import uic, QtWidgets

qtCreatorFile = "DetailsServiceView.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DetallesOperacionWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Área de los Signals
        self.btnVolver.clicked.connect(self.volver)

    # Área de los Slots
    def volver(self):
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DetallesOperacionWindow()
    window.show()
    sys.exit(app.exec_())