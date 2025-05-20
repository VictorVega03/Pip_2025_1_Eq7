import os
import json
import datetime
from ESP32Controller import ESP32Controller


class PetFeederController:
    """
    Controlador Singleton para el alimentador de mascotas.
    Proporciona acceso centralizado al hardware ESP32 y mantiene los estados.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PetFeederController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Configuración por defecto
        self.config = {
            'esp32_ip': '192.168.1.1',  # IP por defecto, se actualizará desde config.json
            'serial_port': 'COM3',  # Puerto serial de respaldo
            'baudrate': 115200,
            'water_level': 80,  # Porcentaje
            'food_level': 65,  # Porcentaje
            'last_service_time': None,
            'scan_network': True  # Buscar automáticamente el ESP32 en la red
        }

        # Cargar configuración si existe
        self._load_config()

        # Inicializar controlador ESP32
        self.esp32 = ESP32Controller(
            ip_address=self.config['esp32_ip'],
            serial_port=self.config['serial_port'],
            baudrate=self.config['baudrate']
        )

        # Buscar ESP32 en la red si está configurado
        if self.config['scan_network']:
            self._scan_for_esp32()

        # Intentar conexión automática
        self.connect_to_esp32()

        # Historial de servicios
        self.service_history = []
        self._load_history()

        self._initialized = True

    def _scan_for_esp32(self):
        """Busca el ESP32 en la red local y actualiza la configuración si lo encuentra."""
        found_ip = self.esp32.scan_network()
        if found_ip:
            self.config['esp32_ip'] = found_ip
            self.esp32.ip_address = found_ip
            self.esp32.base_url = f"http://{found_ip}"
            self._save_config()
            print(f"ESP32 encontrado en {found_ip}")

    def _load_config(self):
        """Carga la configuración desde un archivo JSON."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")

    def _save_config(self):
        """Guarda la configuración en un archivo JSON."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")

    def _load_history(self):
        """Carga el historial de servicios desde un archivo JSON."""
        history_path = os.path.join(os.path.dirname(__file__), 'service_history.json')
        try:
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    self.service_history = json.load(f)
        except Exception as e:
            print(f"Error al cargar historial: {e}")

    def _save_history(self):
        """Guarda el historial de servicios en un archivo JSON."""
        history_path = os.path.join(os.path.dirname(__file__), 'service_history.json')
        try:
            with open(history_path, 'w') as f:
                json.dump(self.service_history, f, indent=4)
        except Exception as e:
            print(f"Error al guardar historial: {e}")

    def connect_to_esp32(self):
        """
        Conecta con el ESP32. Retorna True si tuvo éxito.
        Proporciona información detallada sobre el proceso de conexión.
        """
        print("Intentando conectar con el ESP32...")
        print(f"Dirección IP configurada: {self.config['esp32_ip']}")

        # Verificar si ya tenemos conexión
        if self.esp32.is_connected():
            print("Ya hay una conexión activa con el ESP32")
            return True

        # Intentar conexión directa con la IP configurada
        self.esp32.ip_address = self.config['esp32_ip']
        self.esp32.base_url = f"http://{self.config['esp32_ip']}"

        print(f"Probando conexión directa a {self.esp32.ip_address}...")
        result = self.esp32.connect()

        if result:
            print(f"Conexión establecida con ESP32 en {self.esp32.ip_address}")

            # Verificar que realmente podemos comunicarnos
            status = self.esp32.get_status()
            if status:
                print("Comunicación con ESP32 verificada correctamente")
                self._save_config()  # Guardar la configuración actual
                return True
            else:
                print("No se pudo obtener estado del ESP32, aunque la conexión parece estar establecida")

        # Si no se pudo conectar directamente, intentar buscar en la red
        if self.config.get('scan_network', True):
            print("Conexión directa fallida. Iniciando búsqueda en la red...")

            # Crear lista de rangos para probar, empezando por subredes comunes
            rangos_ip = [
                "192.168.0.1-254",  # Subred común para muchos routers
                "192.168.1.1-254",  # Otra subred muy común
                "10.0.0.1-254",  # Rango de red privada clase A
                "172.16.0.1-254"  # Rango de red privada clase B
            ]

            # Extraer los primeros segmentos de la IP configurada para probar primero
            try:
                ip_parts = self.config['esp32_ip'].split('.')
                if len(ip_parts) == 4:
                    base_ip = ".".join(ip_parts[:3])
                    # Añadir al inicio para probar primero
                    rangos_ip.insert(0, f"{base_ip}.1-254")
            except:
                pass

            # Eliminar duplicados
            rangos_ip = list(dict.fromkeys(rangos_ip))

            # Probar cada rango
            for rango in rangos_ip:
                print(f"Buscando ESP32 en rango: {rango}")
                found_ip = self.esp32.scan_network(rango)
                if found_ip:
                    print(f"ESP32 encontrado en {found_ip}")

                    # Actualizar la configuración
                    self.config['esp32_ip'] = found_ip
                    self.esp32.ip_address = found_ip
                    self.esp32.base_url = f"http://{found_ip}"

                    # Intentar conectar con la IP encontrada
                    if self.esp32.connect():
                        print(f"Conexión establecida con ESP32 en {found_ip}")
                        self._save_config()  # Guardar la nueva IP
                        return True
                    else:
                        print(f"No se pudo establecer conexión con ESP32 en {found_ip} a pesar de haberlo encontrado")
                else:
                    print(f"ESP32 no encontrado en rango {rango}")

        # Si llegamos aquí, no se pudo conectar
        print("No se pudo establecer conexión con el ESP32")

        # Intentar conexión serial como último recurso
        print("Intentando conexión serial como respaldo...")
        if self.esp32._connect_serial():
            print(f"Conexión serial establecida con ESP32 en {self.esp32.serial_port}")
            return True
        else:
            print("También falló la conexión serial. No hay disponibilidad de hardware.")

        return False

    def disconnect_from_esp32(self):
        """Desconecta del ESP32."""
        self.esp32.disconnect()

    def is_esp32_connected(self):
        """Retorna True si hay conexión con el ESP32."""
        return self.esp32.is_connected()

    def update_status(self):
        """
        Actualiza el estado de los niveles de agua y alimento desde el ESP32.
        Retorna True si pudo actualizar, False en caso contrario.
        """
        if not self.is_esp32_connected():
            return False

        status = self.esp32.get_status()
        if status:
            # Actualizar niveles si están disponibles
            if 'nivel_agua' in status:
                self.config['water_level'] = status['nivel_agua']

            if 'nivel_alimento' in status:
                self.config['food_level'] = status['nivel_alimento']

            self._save_config()
            return True

        return False

    def serve_food(self, duration=None):
        """
        Activa el dispensador de alimento.

        Args:
            duration (int, optional): Duración en ms. Si es None, usa la configuración del ESP32.

        Returns:
            bool: True si tuvo éxito
        """
        success = self.esp32.serve_food()

        if success:
            # Registrar en el historial
            service_record = {
                'type': 'food',
                'timestamp': datetime.datetime.now().isoformat(),
                'duration': duration,
                'success': True,
                'device_ip': self.esp32.ip_address
            }
            self.service_history.append(service_record)
            self._save_history()

            # Actualizar nivel de alimento
            self.update_status()

        return success

    def serve_water(self, duration=None):
        """
        Activa la válvula de agua.

        Args:
            duration (int, optional): Duración en ms. Si es None, usa la configuración del ESP32.

        Returns:
            bool: True si tuvo éxito
        """
        success = self.esp32.serve_water()

        if success:
            # Registrar en el historial
            service_record = {
                'type': 'water',
                'timestamp': datetime.datetime.now().isoformat(),
                'duration': duration,
                'success': True,
                'device_ip': self.esp32.ip_address
            }
            self.service_history.append(service_record)
            self._save_history()

            # Actualizar nivel de agua
            self.update_status()

        return success

    def reset_water_counter(self):
        """Reinicia el contador de agua. Retorna True si tuvo éxito."""
        return self.esp32.reset_water_counter()

    def get_water_level(self):
        """Retorna el nivel actual de agua en porcentaje."""
        self.update_status()
        return self.config['water_level']

    def get_food_level(self):
        """Retorna el nivel actual de alimento en porcentaje."""
        self.update_status()
        return self.config['food_level']

    def update_esp32_config(self, config_dict):
        """
        Actualiza la configuración del ESP32.

        Args:
            config_dict (dict): Diccionario con los parámetros a actualizar

        Returns:
            bool: True si tuvo éxito
        """
        return self.esp32.update_config(config_dict)

    def get_service_history(self, page=1, items_per_page=10):
        """
        Obtiene el historial de servicios paginado.

        Args:
            page (int): Número de página (comienza en 1)
            items_per_page (int): Elementos por página

        Returns:
            list: Lista de registros de servicio para la página solicitada
        """
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        # Ordenar por fecha descendente (más reciente primero)
        sorted_history = sorted(
            self.service_history,
            key=lambda x: x['timestamp'],
            reverse=True
        )

        return sorted_history[start_idx:end_idx]

    def get_total_history_pages(self, items_per_page=10):
        """
        Retorna el número total de páginas en el historial.

        Args:
            items_per_page (int): Elementos por página

        Returns:
            int: Número total de páginas
        """
        import math
        return math.ceil(len(self.service_history) / items_per_page)

    def get_daily_consumption(self):
        """
        Calcula el consumo diario promedio de los últimos 7 días.
        Intenta obtener datos reales del ESP32, o calcula en base al historial.

        Returns:
            tuple: (consumo_agua_ml, consumo_alimento_g)
        """
        # Primero, intentar obtener estadísticas del ESP32
        if self.is_esp32_connected():
            status = self.esp32.get_status()
            if status and 'estadisticas' in status:
                est = status['estadisticas']
                # Usar datos del dispositivo si están disponibles
                agua_ml = est.get('agua_ml', 0) // 7 if 'agua_ml' in est else 0
                alimento_g = est.get('alimento_g', 0) // 7 if 'alimento_g' in est else 0
                return (agua_ml, alimento_g)

        # Si no hay datos del ESP32, calcular en base al historial
        now = datetime.datetime.now()
        week_ago = now - datetime.timedelta(days=7)

        water_count = 0
        food_count = 0

        for record in self.service_history:
            try:
                timestamp = datetime.datetime.fromisoformat(record['timestamp'])
                if timestamp > week_ago:
                    if record['type'] == 'water':
                        water_count += 1
                    elif record['type'] == 'food':
                        food_count += 1
            except (ValueError, KeyError):
                continue

        # Valores aproximados basados en el conteo
        water_ml = water_count * 600  # Aproximadamente 600ml por servicio
        food_g = food_count * 750  # Aproximadamente 750g por servicio

        return (water_ml // 7, food_g // 7)  # Dividir entre 7 días