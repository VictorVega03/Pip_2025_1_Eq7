import os
import json
import datetime
from ESP32Controller import ESP32Controller


class PetFeederController:
    """Controlador Singleton para el alimentador de mascotas"""
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
            'esp32_ip': '192.168.1.1',
            'serial_port': 'COM3',
            'baudrate': 115200,
            'water_level': 80,
            'food_level': 65,
            'last_service_time': None,
            'scan_network': True
        }

        self._load_config()

        # Inicializar controlador ESP32
        self.esp32 = ESP32Controller(
            ip_address=self.config['esp32_ip'],
            serial_port=self.config['serial_port'],
            baudrate=self.config['baudrate']
        )

        if self.config['scan_network']:
            self._scan_for_esp32()

        self.connect_to_esp32()

        self.service_history = []
        self._load_history()

        self._initialized = True

    def _scan_for_esp32(self):
        """Busca el ESP32 en la red local y actualiza la configuración"""
        found_ip = self.esp32.scan_network()
        if found_ip:
            self.config['esp32_ip'] = found_ip
            self.esp32.ip_address = found_ip
            self.esp32.base_url = f"http://{found_ip}"
            self._save_config()
            print(f"ESP32 encontrado en {found_ip}")

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")

    def _save_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")

    def _load_history(self):
        history_path = os.path.join(os.path.dirname(__file__), 'service_history.json')
        try:
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    self.service_history = json.load(f)
        except Exception as e:
            print(f"Error al cargar historial: {e}")

    def _save_history(self):
        history_path = os.path.join(os.path.dirname(__file__), 'service_history.json')
        try:
            with open(history_path, 'w') as f:
                json.dump(self.service_history, f, indent=4)
        except Exception as e:
            print(f"Error al guardar historial: {e}")

    def connect_to_esp32(self):
        """Conecta con el ESP32"""
        print("Intentando conectar con el ESP32...")
        print(f"Dirección IP configurada: {self.config['esp32_ip']}")

        if self.esp32.is_connected():
            print("Ya hay una conexión activa con el ESP32")
            return True

        self.esp32.ip_address = self.config['esp32_ip']
        self.esp32.base_url = f"http://{self.config['esp32_ip']}"

        print(f"Probando conexión directa a {self.esp32.ip_address}...")
        result = self.esp32.connect()

        if result:
            print(f"Conexión establecida con ESP32 en {self.esp32.ip_address}")

            status = self.esp32.get_status()
            if status:
                print("Comunicación con ESP32 verificada correctamente")
                self._save_config()
                return True
            else:
                print("No se pudo obtener estado del ESP32, aunque la conexión parece estar establecida")

        # Buscar en la red si la conexión directa falla
        if self.config.get('scan_network', True):
            print("Conexión directa fallida. Iniciando búsqueda en la red...")

            rangos_ip = [
                "192.168.0.1-254",
                "192.168.1.1-254",
                "10.0.0.1-254",
                "172.16.0.1-254"
            ]

            try:
                ip_parts = self.config['esp32_ip'].split('.')
                if len(ip_parts) == 4:
                    base_ip = ".".join(ip_parts[:3])
                    rangos_ip.insert(0, f"{base_ip}.1-254")
            except:
                pass

            rangos_ip = list(dict.fromkeys(rangos_ip))

            for rango in rangos_ip:
                print(f"Buscando ESP32 en rango: {rango}")
                found_ip = self.esp32.scan_network(rango)
                if found_ip:
                    print(f"ESP32 encontrado en {found_ip}")

                    self.config['esp32_ip'] = found_ip
                    self.esp32.ip_address = found_ip
                    self.esp32.base_url = f"http://{found_ip}"

                    if self.esp32.connect():
                        print(f"Conexión establecida con ESP32 en {found_ip}")
                        self._save_config()
                        return True
                    else:
                        print(f"No se pudo establecer conexión con ESP32 en {found_ip} a pesar de haberlo encontrado")
                else:
                    print(f"ESP32 no encontrado en rango {rango}")

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
        self.esp32.disconnect()

    def is_esp32_connected(self):
        return self.esp32.is_connected()

    def update_status(self):
        """Actualiza el estado de los niveles desde el ESP32"""
        if not self.is_esp32_connected():
            return False

        status = self.esp32.get_status()
        if status:
            if 'nivel_agua' in status:
                self.config['water_level'] = status['nivel_agua']

            if 'nivel_alimento' in status:
                self.config['food_level'] = status['nivel_alimento']

            self._save_config()
            return True

        return False

    def serve_food(self, duration=None):
        """Activa el dispensador de alimento"""
        success = self.esp32.serve_food()

        if success:
            service_record = {
                'type': 'food',
                'timestamp': datetime.datetime.now().isoformat(),
                'duration': duration,
                'success': True,
                'device_ip': self.esp32.ip_address
            }
            self.service_history.append(service_record)
            self._save_history()
            self.update_status()

        return success

    def serve_water(self, duration=None):
        """Activa la válvula de agua"""
        success = self.esp32.serve_water()

        if success:
            service_record = {
                'type': 'water',
                'timestamp': datetime.datetime.now().isoformat(),
                'duration': duration,
                'success': True,
                'device_ip': self.esp32.ip_address
            }
            self.service_history.append(service_record)
            self._save_history()
            self.update_status()

        return success

    def reset_water_counter(self):
        return self.esp32.reset_water_counter()

    def get_water_level(self):
        self.update_status()
        return self.config['water_level']

    def get_food_level(self):
        self.update_status()
        return self.config['food_level']

    def update_esp32_config(self, config_dict):
        return self.esp32.update_config(config_dict)

    def get_service_history(self, page=1, items_per_page=10):
        """Obtiene el historial de servicios paginado"""
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page

        sorted_history = sorted(
            self.service_history,
            key=lambda x: x['timestamp'],
            reverse=True
        )

        return sorted_history[start_idx:end_idx]

    def get_total_history_pages(self, items_per_page=10):
        import math
        return math.ceil(len(self.service_history) / items_per_page)

    def get_daily_consumption(self):
        """Calcula el consumo diario promedio de los últimos 7 días"""
        # Intentar obtener estadísticas del ESP32
        if self.is_esp32_connected():
            status = self.esp32.get_status()
            if status and 'estadisticas' in status:
                est = status['estadisticas']
                agua_ml = est.get('agua_ml', 0) // 7 if 'agua_ml' in est else 0
                alimento_g = est.get('alimento_g', 0) // 7 if 'alimento_g' in est else 0
                return (agua_ml, alimento_g)

        # Calcular en base al historial si no hay datos del ESP32
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

        return (water_ml // 7, food_g // 7)  # Promedio diario