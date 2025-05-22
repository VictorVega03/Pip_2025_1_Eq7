import sys
from PyQt5 import uic, QtWidgets
import DetailsServiceView
from PetFeederController import PetFeederController
import datetime

qtCreatorFile = "ServiceHistoryView.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class HistorialServiciosWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.pet_feeder = PetFeederController()

        self.btnVolver.clicked.connect(self.volver)
        self.btnVerRegistro.clicked.connect(self.ver_detalles)
        self.btnPrevious.clicked.connect(self.pagina_anterior)
        self.btnNext.clicked.connect(self.pagina_siguiente)

        self.pagina_actual = 1
        self.registros_por_pagina = 10

        self.cargar_registros()

    def volver(self):
        self.close()

    def ver_detalles(self):
        try:
            if hasattr(self, 'tableWidgetRegistros'):
                fila_seleccionada = self.tableWidgetRegistros.currentRow()
                if fila_seleccionada >= 0:
                    indice_registro = (self.pagina_actual - 1) * self.registros_por_pagina + fila_seleccionada
                    registros = self.pet_feeder.get_service_history(page=1, items_per_page=1000)

                    if indice_registro < len(registros):
                        registro = registros[indice_registro]

                        self.ventana_detalles = DetailsServiceView.DetallesOperacionWindow()

                        # Actualizar campos en la ventana de detalles
                        if hasattr(self.ventana_detalles, 'labelTipoServicio'):
                            self.ventana_detalles.labelTipoServicio.setText(registro['type'].capitalize())

                        if hasattr(self.ventana_detalles, 'labelFechaHora'):
                            try:
                                fecha_hora = datetime.datetime.fromisoformat(registro['timestamp'])
                                self.ventana_detalles.labelFechaHora.setText(fecha_hora.strftime("%d/%m/%Y %H:%M:%S"))
                            except (ValueError, KeyError):
                                self.ventana_detalles.labelFechaHora.setText("Fecha no disponible")

                        if hasattr(self.ventana_detalles, 'labelDuracion'):
                            duracion = registro.get('duration', 'No especificada')
                            self.ventana_detalles.labelDuracion.setText(str(duracion))

                        if hasattr(self.ventana_detalles, 'labelEstado'):
                            estado = "Exitoso" if registro.get('success', False) else "Fallido"
                            self.ventana_detalles.labelEstado.setText(estado)

                        if hasattr(self.ventana_detalles, 'labelDispositivo') and 'device_ip' in registro:
                            self.ventana_detalles.labelDispositivo.setText(registro['device_ip'])

                        self.ventana_detalles.show()
                    else:
                        self.mostrar_mensaje_error("Índice de registro fuera de rango")
                else:
                    self.mostrar_mensaje_error("No has seleccionado ningún registro")
            else:
                self.ventana_detalles = DetailsServiceView.DetallesOperacionWindow()
                self.ventana_detalles.show()
        except Exception as e:
            print(f"Error al abrir detalles: {e}")
            self.ventana_detalles = DetailsServiceView.DetallesOperacionWindow()
            self.ventana_detalles.show()

    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.lineEditPage.setText(str(self.pagina_actual))
            self.cargar_registros()

    def pagina_siguiente(self):
        total_paginas = self.pet_feeder.get_total_history_pages(self.registros_por_pagina)
        if self.pagina_actual < total_paginas:
            self.pagina_actual += 1
            self.lineEditPage.setText(str(self.pagina_actual))
            self.cargar_registros()

    def cargar_registros(self):
        """Carga los registros de la página actual en la tabla"""
        registros = self.pet_feeder.get_service_history(
            page=self.pagina_actual,
            items_per_page=self.registros_por_pagina
        )

        if hasattr(self, 'tableWidgetRegistros'):
            self.tableWidgetRegistros.setRowCount(0)

            if self.tableWidgetRegistros.columnCount() < 4:
                self.tableWidgetRegistros.setColumnCount(4)
                self.tableWidgetRegistros.setHorizontalHeaderLabels([
                    "Tipo", "Fecha/Hora", "Duración", "Estado"
                ])

            for i, registro in enumerate(registros):
                self.tableWidgetRegistros.insertRow(i)

                tipo_item = QtWidgets.QTableWidgetItem(registro.get('type', 'desconocido').capitalize())
                self.tableWidgetRegistros.setItem(i, 0, tipo_item)

                try:
                    fecha_hora = datetime.datetime.fromisoformat(registro['timestamp'])
                    fecha_item = QtWidgets.QTableWidgetItem(fecha_hora.strftime("%d/%m/%Y %H:%M"))
                except (ValueError, KeyError):
                    fecha_item = QtWidgets.QTableWidgetItem("Desconocida")
                self.tableWidgetRegistros.setItem(i, 1, fecha_item)

                duracion = str(registro.get('duration', 'N/A'))
                duracion_item = QtWidgets.QTableWidgetItem(duracion)
                self.tableWidgetRegistros.setItem(i, 2, duracion_item)

                estado = "Exitoso" if registro.get('success', False) else "Fallido"
                estado_item = QtWidgets.QTableWidgetItem(estado)
                self.tableWidgetRegistros.setItem(i, 3, estado_item)

        # Actualizar información de paginación
        total_paginas = self.pet_feeder.get_total_history_pages(self.registros_por_pagina)
        if hasattr(self, 'labelTotalPages'):
            self.labelTotalPages.setText(f"de {total_paginas}")

    def mostrar_mensaje_error(self, mensaje):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(mensaje)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = HistorialServiciosWindow()
    window.show()
    sys.exit(app.exec_())