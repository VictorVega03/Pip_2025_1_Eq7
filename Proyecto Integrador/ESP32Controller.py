import requests
import json
import time
import threading
import serial  # Se mantiene para compatibilidad con modo de respaldo


class ESP32Controller:
    """
    Clase para controlar el ESP32 del alimentador automático de mascotas.
    Utiliza principalmente conexión WiFi para comunicarse con el dispositivo
    a través de los endpoints HTTP que expone el ESP32.
    """

    def __init__(self, ip_address='192.168.0.1', serial_port='COM3', baudrate=115200, timeout=1):
        """
        Inicializa la conexión con el ESP32.

        Args:
            ip_address (str): Dirección IP del ESP32 en la red local
            serial_port (str): Puerto COM donde está conectado el ESP32 (como respaldo)
            baudrate (int): Velocidad de comunicación serial (si es necesario)
            timeout (float): Tiempo de espera para conexiones
        """
        self.ip_address = ip_address
        self.base_url = f"http://{ip_address}"
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None
        self._connected_wifi = False
        self._connected_serial = False
        self._lock = threading.Lock()
        self._last_data = {}
        self._running = False
        self._monitor_thread = None

    def connect(self):
        """Intenta conectar con el ESP32 vía WiFi y como respaldo serial."""
        print(f"Iniciando conexión con ESP32 en {self.ip_address}...")

        # Primero intentar conexión WiFi
        wifi_success = self._check_wifi_connection()

        # Si la conexión WiFi falla, intentar conexión serial
        serial_success = False
        if not wifi_success:
            print("Conexión WiFi fallida, intentando conexión serial...")
            serial_success = self._connect_serial()

        success = wifi_success or serial_success
        if success:
            print("Conexión con ESP32 establecida correctamente")
        else:
            print("Todos los métodos de conexión fallaron")

        return success

    def _check_wifi_connection(self):
        """Verifica si puede conectarse al ESP32 vía WiFi."""
        from requests.exceptions import RequestException

        try:
            print(f"Intentando conexión HTTP a {self.base_url}...")

            # Intentar obtener la página principal (timeout corto)
            try:
                response = requests.get(f"{self.base_url}/", timeout=3.0)
                print(f"Respuesta recibida con código: {response.status_code}")

                if response.status_code == 200:
                    # Comprobar si es realmente el ESP32 que buscamos
                    response_text = response.text.lower()
                    if any(keyword in response_text for keyword in ["alimentador", "mascota", "esp32", "pet feeder"]):
                        self._connected_wifi = True
                        print(f"Conectado vía WiFi a {self.ip_address}. Identificado como ESP32 del alimentador.")

                        # Intentar obtener datos para verificar comunicación completa
                        try:
                            data_response = requests.get(f"{self.base_url}/data", timeout=2.0)
                            if data_response.status_code == 200:
                                print("Comunicación de datos verificada correctamente")
                                # Almacenar los datos para su uso posterior
                                try:
                                    self._last_data = data_response.json()
                                except json.JSONDecodeError:
                                    print("Error al decodificar JSON de respuesta")
                            else:
                                print(f"Advertencia: Endpoint /data devolvió código {data_response.status_code}")
                        except RequestException as e:
                            print(f"Advertencia: No se pudo acceder al endpoint /data: {e}")

                        return True
                    else:
                        self._connected_wifi = False
                        print(
                            f"El dispositivo en {self.ip_address} respondió, pero no parece ser el ESP32 del alimentador")
                        print(f"Contenido HTML recibido: {response.text[:100]}...")
                        return False
                else:
                    self._connected_wifi = False
                    print(f"Conexión WiFi fallida. Código HTTP: {response.status_code}")
                    return False
            except RequestException as e:
                self._connected_wifi = False
                print(f"Error al conectar vía HTTP: {e}")
                return False

        except Exception as e:
            self._connected_wifi = False
            print(f"Error general al conectar vía WiFi: {e}")
            return False

    def _connect_serial(self):
        """Conecta con el ESP32 vía serial (como respaldo)."""
        try:
            self._serial = serial.Serial(self.serial_port, self.baudrate, timeout=self.timeout)
            time.sleep(2)  # Esperar a que Arduino se reinicie después de la conexión
            self._connected_serial = True

            # Iniciar hilo de monitoreo serial
            if not self._running:
                self._running = True
                self._monitor_thread = threading.Thread(target=self._monitor_serial)
                self._monitor_thread.daemon = True
                self._monitor_thread.start()

            print(f"Conectado vía Serial a {self.serial_port}")
            return True
        except Exception as e:
            self._connected_serial = False
            print(f"Error al conectar vía Serial: {e}")
            return False

    def disconnect(self):
        """Desconecta del ESP32."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)

        if self._serial and self._serial.is_open:
            self._serial.close()

        self._connected_wifi = False
        self._connected_serial = False

    def is_connected(self):
        """Retorna True si está conectado al ESP32 por cualquier método."""
        # Si perdimos la conexión WiFi, intentar reconectar
        if self._connected_wifi:
            try:
                # Hacer una petición simple para verificar conectividad
                response = requests.get(f"{self.base_url}/", timeout=1.0)
                if response.status_code != 200:
                    self._connected_wifi = False
            except:
                self._connected_wifi = False

        return self._connected_wifi or (self._connected_serial and self._serial and self._serial.is_open)

    def _monitor_serial(self):
        """Hilo que monitorea continuamente los datos enviados por el ESP32."""
        while self._running and self._serial and self._serial.is_open:
            try:
                if self._serial.in_waiting > 0:
                    line = self._serial.readline().decode('utf-8').strip()

                    # Intentar interpretar como JSON si comienza con '{'
                    if line and line.startswith('{'):
                        try:
                            data = json.loads(line)
                            with self._lock:
                                self._last_data = data
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                print(f"Error en el monitor serial: {e}")
                time.sleep(0.1)

    def _send_serial_command(self, command):
        """
        Envía un comando al ESP32 vía serial.

        Args:
            command (str): Comando a enviar

        Returns:
            bool: True si el comando se envió correctamente, False en caso contrario
        """
        if not self._connected_serial or not self._serial or not self._serial.is_open:
            print("No hay conexión serial")
            return False

        try:
            with self._lock:
                self._serial.write(f"{command}\n".encode('utf-8'))
                self._serial.flush()
            return True
        except Exception as e:
            print(f"Error al enviar comando serial: {e}")
            return False

    # Métodos para las acciones específicas con preferencia por WiFi
    def serve_food(self):
        """
        Activa el dispensador de alimento.
        Intenta primero por WiFi, luego por serial si es necesario.

        Returns:
            bool: True si tuvo éxito
        """
        if self._connected_wifi:
            try:
                # Endpoint correcto según el código Arduino: "/alimentar"
                response = requests.post(f"{self.base_url}/alimentar", timeout=5.0)
                return response.status_code == 200
            except Exception as e:
                print(f"Error al servir alimento vía WiFi: {e}")
                # Si WiFi falla, intentar vía serial

        # Método de respaldo: serial
        if self._connected_serial:
            return self._send_serial_command("1")

        return False

    def serve_water(self):
        """
        Activa la válvula de agua.
        Intenta primero por WiFi, luego por serial si es necesario.

        Returns:
            bool: True si tuvo éxito
        """
        if self._connected_wifi:
            try:
                # Endpoint correcto según el código Arduino: "/agua"
                response = requests.post(f"{self.base_url}/agua", timeout=5.0)
                return response.status_code == 200
            except Exception as e:
                print(f"Error al servir agua vía WiFi: {e}")
                # Si WiFi falla, intentar vía serial

        # Método de respaldo: serial
        if self._connected_serial:
            return self._send_serial_command("2")

        return False

    def reset_water_counter(self):
        """
        Reinicia el contador de agua.
        Intenta primero por WiFi, luego por serial si es necesario.

        Returns:
            bool: True si tuvo éxito
        """
        if self._connected_wifi:
            try:
                # Endpoint correcto según el código Arduino: "/reset_agua"
                response = requests.post(f"{self.base_url}/reset_agua", timeout=5.0)
                return response.status_code == 200
            except Exception as e:
                print(f"Error al reiniciar contador vía WiFi: {e}")
                # Si WiFi falla, intentar vía serial

        # Método de respaldo: serial
        if self._connected_serial:
            return self._send_serial_command("3")

        return False

    def get_status(self):
        """
        Obtiene el estado actual del sistema.
        Intenta primero por WiFi, luego por serial si es necesario.

        Returns:
            dict: Estado actual del sistema con los niveles de agua, alimento, etc.
        """
        if self._connected_wifi:
            try:
                # Endpoint para obtener datos según el Arduino: "/data"
                response = requests.get(f"{self.base_url}/data", timeout=5.0)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        with self._lock:
                            self._last_data = data
                        return data
                    except json.JSONDecodeError:
                        print("Error al decodificar respuesta JSON")
            except Exception as e:
                print(f"Error al obtener estado vía WiFi: {e}")
                # Si WiFi falla, intentar vía serial

        # Método de respaldo: serial
        if self._connected_serial:
            if self._send_serial_command("status"):
                time.sleep(0.5)  # Dar tiempo para recibir la respuesta
                with self._lock:
                    return self._last_data.copy()

        return self._last_data.copy() if self._last_data else None

    def update_config(self, config_dict):
        """
        Actualiza la configuración del ESP32.

        Args:
            config_dict (dict): Diccionario con los parámetros a actualizar

        Returns:
            bool: True si tuvo éxito
        """
        if not self._connected_wifi:
            print("No hay conexión WiFi para actualizar configuración")
            return False

        try:
            # Endpoint para actualizar configuración según el Arduino: "/config"
            response = requests.post(
                f"{self.base_url}/config",
                json=config_dict,
                headers={'Content-Type': 'application/json'},
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error al actualizar configuración: {e}")
            return False

    def scan_network(self, ip_range=None):
        """
        Busca el ESP32 en la red local con reporte detallado del progreso.

        Args:
            ip_range (str, optional): Rango de IPs a escanear. Por defecto usa una subred común.

        Returns:
            str: IP del ESP32 si se encuentra, None en caso contrario
        """
        import socket
        import subprocess
        import platform

        # Para reportar progreso
        print("Iniciando escaneo de red para encontrar ESP32...")

        # Primero, intentar obtener información de la red local
        local_ip = None
        subnet_mask = None

        try:
            # Obtener la IP local usando socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Conectar a un servidor DNS de Google
            local_ip = s.getsockname()[0]
            s.close()
            print(f"IP local detectada: {local_ip}")

            # Intentar obtener la máscara de subred (solo en sistemas basados en Unix)
            if platform.system() != "Windows":
                try:
                    import netifaces
                    for interface in netifaces.interfaces():
                        addresses = netifaces.ifaddresses(interface)
                        if netifaces.AF_INET in addresses:
                            addr_info = addresses[netifaces.AF_INET][0]
                            if addr_info.get('addr') == local_ip:
                                subnet_mask = addr_info.get('netmask')
                                break
                except (ImportError, Exception) as e:
                    print(f"No se pudo determinar la máscara de subred: {e}")
        except Exception as e:
            print(f"Error al obtener la IP local: {e}")

        # Si se proporciona un rango, usarlo
        if ip_range:
            print(f"Usando rango proporcionado: {ip_range}")
        elif local_ip:
            # Construir un rango basado en la IP local
            base_ip = ".".join(local_ip.split(".")[:3])
            ip_range = f"{base_ip}.1-254"
            print(f"Rango generado automáticamente: {ip_range}")
        else:
            # Si no se puede determinar, usar rangos comunes
            possible_ranges = [
                "192.168.0.1-254",
                "192.168.1.1-254",
                "10.0.0.1-254",
                "172.16.0.1-254"
            ]
            for possible_range in possible_ranges:
                print(f"Probando rango: {possible_range}")
                result = self._scan_ip_range(possible_range)
                if result:
                    return result
            print("No se encontró el ESP32 en los rangos comunes.")
            return None

        # Escanear el rango construido
        return self._scan_ip_range(ip_range)

    def _scan_ip_range(self, ip_range):
        """
        Escanea un rango específico de IPs buscando el ESP32.

        Args:
            ip_range (str): Rango de IPs a escanear (formato: "192.168.1.1-254")

        Returns:
            str: IP del ESP32 si se encuentra, None en caso contrario
        """
        import concurrent.futures
        import time
        from requests.exceptions import RequestException

        # Parsear el rango
        if "-" in ip_range:
            try:
                base_ip, range_str = ip_range.rsplit(".", 1)
                start, end = map(int, range_str.split("-"))
                if start < 1 or end > 254 or start > end:
                    print(f"Rango inválido: {ip_range}. Usando 1-254")
                    start, end = 1, 254
            except Exception as e:
                print(f"Error al parsear rango {ip_range}: {e}")
                base_ip = ip_range.rsplit(".", 1)[0]
                start, end = 1, 254
        else:
            print(f"Formato de rango inválido: {ip_range}")
            return None

        print(f"Buscando ESP32 en rango {base_ip}.{start}-{end}...")

        # Función para verificar una IP específica
        def check_ip(ip):
            url = f"http://{ip}/"
            try:
                response = requests.get(url, timeout=0.5)
                if response.status_code == 200:
                    response_text = response.text.lower()
                    # Buscar patrones que indiquen que es el ESP32 del alimentador
                    if any(keyword in response_text for keyword in ["alimentador", "mascota", "esp32", "pet feeder"]):
                        print(f"ESP32 encontrado en {ip}!")
                        return ip
                    else:
                        print(f"Dispositivo encontrado en {ip}, pero no parece ser el ESP32 del alimentador")
            except RequestException:
                # No hacer nada, es normal que muchas IPs no respondan
                pass
            except Exception as e:
                # Solo mostrar errores inesperados
                print(f"Error inesperado al verificar {ip}: {e}")
            return None

        # Usar ThreadPoolExecutor para escanear en paralelo
        ip_addresses = [f"{base_ip}.{i}" for i in range(start, end + 1)]
        found_ip = None

        # Dividir en bloques más pequeños para reportar progreso
        block_size = 25
        total_blocks = (end - start + 1) // block_size + 1

        for block_num in range(total_blocks):
            block_start = block_num * block_size
            block_end = min((block_num + 1) * block_size, len(ip_addresses))
            block_ips = ip_addresses[block_start:block_end]

            print(f"Escaneando bloque {block_num + 1}/{total_blocks}: {block_ips[0]} a {block_ips[-1]}")

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_ip = {executor.submit(check_ip, ip): ip for ip in block_ips}
                for future in concurrent.futures.as_completed(future_to_ip):
                    result = future.result()
                    if result:
                        found_ip = result
                        # Cancelar el resto de las tareas
                        for f in future_to_ip:
                            f.cancel()
                        break

            if found_ip:
                break

            # Pequeña pausa para no saturar la red
            time.sleep(0.2)

        if not found_ip:
            print(f"ESP32 no encontrado en el rango {ip_range}")

        return found_ip