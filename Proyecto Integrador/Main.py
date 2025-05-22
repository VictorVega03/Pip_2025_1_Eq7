import sys
from PyQt5 import QtWidgets
from Dashboard import MyApp


def main():
    print("Iniciando Aplicación de Control de Alimentador de Mascotas...")

    app = QtWidgets.QApplication(sys.argv)

    try:
        window = MyApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setWindowTitle("Error de Inicio")
        error_dialog.setText(f"No se pudo iniciar la aplicación: {str(e)}")
        error_dialog.setDetailedText(f"Detalles del error:\n{str(e)}")
        error_dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
        error_dialog.exec_()
        sys.exit(1)


if __name__ == "__main__":
    main()