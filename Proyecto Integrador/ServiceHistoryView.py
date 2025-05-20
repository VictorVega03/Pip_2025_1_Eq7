import sys
from PyQt5 import uic, QtWidgets
import DetailsServiceView  # Importamos la vista de detalles
from PetFeederController import PetFeederController  # Importamos el controlador
import datetime

qtCreatorFile = "ServiceHistoryView.ui"  # Nombre del archivo UI
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class HistorialServiciosWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Inicializar el controlador del alimentador
        self.pet_feeder = PetFeederController()

        # Área de los Signals
        self.btnVolver.clicked.connect(self.volver)
        self.btnVerRegistro.clicked.connect(self.ver_detalles)
        self.btnPrevious.clicked.connect(self.pagina_anterior)
        self.btnNext.clicked.connect(self.pagina_siguiente)

        # Inicializar variables
        self.pagina_actual = 1
        self.registros_por_pagina = 10

        # Cargar registros iniciales
        self.cargar_registros()

    # Área de los Slots
    def volver(self):
        self.close()

    def ver_detalles(self):
        """Abre la ventana de detalles para el registro seleccionado"""
        # Obtener el índice seleccionado (esto depende de cómo esté implementada tu UI)
        try:
            if hasattr(self, 'tableWidgetRegistros'):
                fila_seleccionada = self.tableWidgetRegistros.currentRow()
                if fila_seleccionada >= 0:
                    # Obtener el registro correspondiente
                    indice_registro = (self.pagina_actual - 1) * self.registros_por_pagina + fila_seleccionada
                    registros = self.pet_feeder.get_service_history(page=1,
                                                                    items_per_page=1000)  # Obtener todos los registros

                    if indice_registro < len(registros):
                        registro = registros[indice_registro]

                        # Abrir ventana de detalles y pasar el registro
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

                        # Si hay dirección IP, mostrarla
                        if hasattr(self.ventana_detalles, 'labelDispositivo') and 'device_ip' in registro:
                            self.ventana_detalles.labelDispositivo.setText(registro['device_ip'])

                        self.ventana_detalles.show()
                    else:
                        self.mostrar_mensaje_error("Índice de registro fuera de rango")
                else:
                    self.mostrar_mensaje_error("No has seleccionado ningún registro")
            else:
                # Si no hay una tabla, simplemente abrimos la ventana de detalles sin datos específicos
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
        # Obtener los registros de la página actual
        registros = self.pet_feeder.get_service_history(
            page=self.pagina_actual,
            items_per_page=self.registros_por_pagina
        )

        # Actualizar la tabla (esto depende de cómo esté implementada tu UI)
        if hasattr(self, 'tableWidgetRegistros'):
            # Limpiar tabla
            self.tableWidgetRegistros.setRowCount(0)

            # Configurar columnas si es necesario
            if self.tableWidgetRegistros.columnCount() < 4:
                self.tableWidgetRegistros.setColumnCount(4)
                self.tableWidgetRegistros.setHorizontalHeaderLabels([
                    "Tipo", "Fecha/Hora", "Duración", "Estado"
                ])

            # Añadir filas
            for i, registro in enumerate(registros):
                self.tableWidgetRegistros.insertRow(i)

                # Tipo de servicio
                tipo_item = QtWidgets.QTableWidgetItem(registro.get('type', 'desconocido').capitalize())
                self.tableWidgetRegistros.setItem(i, 0, tipo_item)

                # Fecha/Hora
                try:
                    fecha_hora = datetime.datetime.fromisoformat(registro['timestamp'])
                    fecha_item = QtWidgets.QTableWidgetItem(fecha_hora.strftime("%d/%m/%Y %H:%M"))
                except (ValueError, KeyError):
                    fecha_item = QtWidgets.QTableWidgetItem("Desconocida")
                self.tableWidgetRegistros.setItem(i, 1, fecha_item)

                # Duración
                duracion = str(registro.get('duration', 'N/A'))
                duracion_item = QtWidgets.QTableWidgetItem(duracion)
                self.tableWidgetRegistros.setItem(i, 2, duracion_item)

                # Estado
                estado = "Exitoso" if registro.get('success', False) else "Fallido"
                estado_item = QtWidgets.QTableWidgetItem(estado)
                self.tableWidgetRegistros.setItem(i, 3, estado_item)

        # Actualizar información de paginación
        total_paginas = self.pet_feeder.get_total_history_pages(self.registros_por_pagina)
        if hasattr(self, 'labelTotalPages'):
            self.labelTotalPages.setText(f"de {total_paginas}")

    def mostrar_mensaje_error(self, mensaje):
        """Muestra un mensaje de error"""
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