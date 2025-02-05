import sys
from PyQt5 import uic, QtWidgets
import os

qtCreatorFile = "P08_PromedioNumeros-Load_V2.ui"  # Nombre del archivo aquí.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        # Área de los Signals
        self.btn_cargar.clicked.connect(self.cargar)
        self.btn_agregar.clicked.connect(self.agregar)
        self.btn_guardar.clicked.connect(self.guardar)
        self.calificaciones = []
        self.califAgregadas = False

    # Área de los Slots
    def cargar(self):
        if self.califAgregadas:
            self.msj("Ya no se puede cargar un archivo después de agregar una calificación.")

            self.btn_cargar.visible = False
            self.btn_cargar.setEnabled(False)
            return

        if os.path.exists("../Archivos/calificaciones.csv"):
            archivo = open("../Archivos/calificaciones.csv")
            contenido = archivo.readlines()
            archivo.close()
            datos = [int(x) for x in contenido]
            self.calificaciones.extend(datos)
            self.promedio()
        else:
            self.msj("El archivo seleccionado no se encontro o no existe.")

        self.txt_lista_calificaciones.setText(str(self.calificaciones))

    def agregar(self):
        calificacion = int(self.txt_calificacion.text())
        self.calificaciones.append(calificacion)
        self.promedio()
        self.califAgregadas = True
        self.txt_lista_calificaciones.setText(str(self.calificaciones))

    def promedio(self):
        prom = sum(self.calificaciones) / len(self.calificaciones)
        self.txt_promedio.setText(str(prom))

    def guardar(self):
        archivo = open("../Archivos/calificaciones.csv", "w") # w = write  --- a = append
        for c in self.calificaciones:
            archivo.write(str(c) + "\n")
        archivo.flush()
        archivo.close()
        self.msj("Archivo Guardado con Exito!")

    def msj(self, txt):
        m = QtWidgets.QMessageBox()
        m.setText(txt)
        m.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
