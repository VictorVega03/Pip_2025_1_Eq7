import sys
import serial
from PyQt5 import uic, QtWidgets
from PyQt5.uic.properties import QtCore

qtCreatorFile = "P39_ArduinoyPthonGUI_Read.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.arduino = None
        self.btn_accion.clicked.connect(self.btn_accion)
        self.segundoPlano = QtCore.Qtimer()
        self.segundoPlano.timeout(self.lecturas)
        self.btn_accion.clicked.connect(self.accion)
        self.bandera = 0
        self.datos = []

    def lecturas(self):
        if self.arduino.isOpen():
            cadena = self.arduino.readLine().decode().strip()
            if cadena != "":
                self.datos.append(cadena)
                if self.bandera == 0:
                    print(cadena)
    def accion(self):
        texto = self.btn_accion.text()
        com = self.txt_com.text()

        if texto == "CONECTAR":
            self.arduino = serial.Serial(com, baudrate=9600, timeout = 1)
            self.segundoPlano.start(100)
            self.btn_accion.setText("DESCONECTAR")
            self.txt_estado.setText("CONECTADO")
        elif texto == "DESCONECTAR":
            self.segundoPlano.stop()
            self.arduino.close()
            self.btn_accion.setText("RECONECTAR")
            self.txt_estado.setText("DESCONECTADO")
        elif texto == "RECONECTAR":
            self.segundoPlano.start(100)
            self.arduino.open()
            self.btn_accion.setText("DESCONECTAR")
            self.txt_estado.setText("RECONECTAR")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
