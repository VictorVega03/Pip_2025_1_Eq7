import sys
from PyQt5 import QtWidgets
from Dashboard import MyApp  # Importamos la clase principal del Dashboard


def main():
    """
    Función principal para iniciar la aplicación del alimentador de mascotas.
    """
    print("Iniciando Aplicación de Control de Alimentador de Mascotas...")

    # Inicializar la aplicación PyQt
    app = QtWidgets.QApplication(sys.argv)

    # Mostrar la ventana principal (Dashboard)
    try:
        window = MyApp()
        window.show()

        # Ejecutar el bucle principal de la aplicación
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        # En caso de error crítico, mostrar una ventana de error
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