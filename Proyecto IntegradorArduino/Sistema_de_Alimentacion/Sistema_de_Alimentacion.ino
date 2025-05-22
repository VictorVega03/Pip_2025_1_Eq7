#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <EEPROM.h>
#include <Ticker.h>

// Configuración WiFi
const char* WIFI_SSID = "Falex";
const char* WIFI_PASSWORD = "123456789w";

// EEPROM Config
#define EEPROM_SIZE 512
#define WIFI_CONFIG_ADDR 0
#define SYSTEM_CONFIG_ADDR 128

struct WifiConfig {
  char ssid[32];
  char password[64];
  bool configurado;
};

// Servidor HTTP
WebServer server(80);

// Intervalos
constexpr unsigned long DATA_INTERVAL_MS = 5000;
Ticker dataTicker;

// Pinout ESP32
// Ultrasónico agua
constexpr uint8_t TRIG_PIN_AGUA   = 13;
constexpr uint8_t ECHO_PIN_AGUA   = 12;
// Ultrasónico alimento
constexpr uint8_t TRIG_PIN_ALIM   = 14;
constexpr uint8_t ECHO_PIN_ALIM   = 27;
// Motor paso a paso
constexpr uint8_t M1 = 26;
constexpr uint8_t M2 = 25;
constexpr uint8_t M3 = 33;
constexpr uint8_t M4 = 32;
// Válvula solenoide agua (relé)
constexpr uint8_t VALVE_PIN       = 17;
// Sensor nivel en comedero
constexpr uint8_t WATER_SLOT_PIN  = 34;

// Constantes
constexpr int MAX_DIST_AGUA = 30;
constexpr int MAX_DIST_ALIM = 25;
constexpr int FACTOR_ML_POR_CM = 10;
constexpr int FACTOR_G_POR_CM = 5;

// Estructuras
struct Stats {
  unsigned long aguaConsumida    = 0;
  unsigned long alimConsumido    = 0;
  uint16_t      vecesRellenoAgua = 0;
  uint16_t      vecesAlimentacion= 0;
  int           lastNivelAgua    = 0;
  int           lastNivelAlim    = 0;
} stats;

struct Config {
  unsigned long durServAlim     = 3000;
  unsigned long durServAgua     = 3000;
  unsigned long intvAlim       = 12UL*3600UL*1000UL;
  unsigned long intvCambioAgua = 3UL*24UL*3600UL*1000UL;
  int           umbralAgua      = 20;
  int           umbralAlim      = 15;
  int           umbralAguaSlot  = 1000;
  bool          autoRefillAgua  = true;
} config;

// Control de temporización
unsigned long lastFeedTime    = 0;
unsigned long lastWaterCheck  = 0;
unsigned long lastWaterChange = 0;
unsigned long lastDataSent    = 0;

// Secuencia motor (medio paso)
constexpr uint8_t STEPS = 8;
const uint8_t seq[STEPS][4] = {
  {1,0,0,0},{1,1,0,0},{0,1,0,0},{0,1,1,0},
  {0,0,1,0},{0,0,1,1},{0,0,0,1},{1,0,0,1}
};

// Variables para configuración por serial
String inputString = "";
bool stringComplete = false;

// Declaraciones
void medirYPublicar();
void configurarServidor();
int  leerUltrasonico(uint8_t trig, uint8_t echo, int maxDistCm);
bool hayAguaSlot();
void servirAlimento(unsigned long durMs);
void servirAgua(unsigned long durMs);
void guardarConfig();
void cargarConfig();
bool conectarWifiEstatico();
void procesarSerial();

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n====== Sistema Alimentador Automático ======");
  
  EEPROM.begin(EEPROM_SIZE);
  
  // Configuración de pines
  pinMode(TRIG_PIN_AGUA, OUTPUT);
  pinMode(ECHO_PIN_AGUA, INPUT);
  pinMode(TRIG_PIN_ALIM, OUTPUT);
  pinMode(ECHO_PIN_ALIM, INPUT);
  pinMode(M1, OUTPUT); pinMode(M2, OUTPUT);
  pinMode(M3, OUTPUT); pinMode(M4, OUTPUT);
  pinMode(VALVE_PIN, OUTPUT);
  digitalWrite(VALVE_PIN, LOW);
  pinMode(WATER_SLOT_PIN, INPUT);

  // Inicializar pines del motor
  digitalWrite(M1, LOW); digitalWrite(M2, LOW);
  digitalWrite(M3, LOW); digitalWrite(M4, LOW);

  cargarConfig();
  
  Serial.println("Intentando conectar con WiFi estático...");
  if (conectarWifiEstatico()) {
    configurarServidor();
    server.begin();
    Serial.println("Servidor HTTP iniciado");
    dataTicker.attach_ms(DATA_INTERVAL_MS, medirYPublicar);
  } else {
    Serial.println("No se pudo conectar al WiFi estático.");
    Serial.println("Use el monitor serial para comandos manuales:");
    Serial.println("1. Servir alimento");
    Serial.println("2. Servir agua");
    Serial.println("3. Reiniciar contador de agua");
  }

  // Inicializar tiempos
  lastFeedTime    = millis();
  lastWaterCheck  = millis();
  lastWaterChange = millis();
}

void loop() {
  unsigned long currentMillis = millis();
  
  procesarSerial();
  
  if (WiFi.status() == WL_CONNECTED) {
    server.handleClient();
    
    // Alimentación automática
    if (config.intvAlim > 0 && currentMillis - lastFeedTime >= config.intvAlim) {
      Serial.println("Alimentación automática programada");
      servirAlimento(config.durServAlim);
      lastFeedTime = currentMillis;
      stats.vecesAlimentacion++;
    }
    
    // Verificación de agua y relleno automático
    if (config.autoRefillAgua && currentMillis - lastWaterCheck >= 30000) {
      lastWaterCheck = currentMillis;
      
      if (!hayAguaSlot()) {
        int nivelAgua = leerUltrasonico(TRIG_PIN_AGUA, ECHO_PIN_AGUA, MAX_DIST_AGUA);
        if (nivelAgua > config.umbralAgua) {
          Serial.println("Rellenando agua automáticamente");
          servirAgua(config.durServAgua);
          stats.vecesRellenoAgua++;
        }
      }
    }
    
    // Publicar datos periódicamente
    if (currentMillis - lastDataSent >= DATA_INTERVAL_MS + 1000) {
      medirYPublicar();
      lastDataSent = currentMillis;
    }
  } else {
    // Reintentar conexión cada 30 segundos
    static unsigned long lastReconnectAttempt = 0;
    if (currentMillis - lastReconnectAttempt >= 30000) {
      lastReconnectAttempt = currentMillis;
      Serial.println("Reintentando conexión WiFi...");
      conectarWifiEstatico();
    }
  }
}

void procesarSerial() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) {
        stringComplete = true;
      }
    } else {
      inputString += inChar;
    }
  }
  
  if (stringComplete) {
    inputString.trim();
    
    if (inputString == "1") {
      Serial.println("Sirviendo alimento manualmente...");
      servirAlimento(config.durServAlim);
      lastFeedTime = millis();
      stats.vecesAlimentacion++;
    } 
    else if (inputString == "2") {
      Serial.println("Sirviendo agua manualmente...");
      servirAgua(config.durServAgua);
      stats.vecesRellenoAgua++;
    } 
    else if (inputString == "3") {
      Serial.println("Reiniciando contador de agua...");
      lastWaterChange = millis();
    }
    else if (inputString == "status") {
      Serial.println("\n--- ESTADO DEL SISTEMA ---");
      Serial.print("Nivel de agua: ");
      Serial.print(leerUltrasonico(TRIG_PIN_AGUA, ECHO_PIN_AGUA, MAX_DIST_AGUA));
      Serial.println("%");
      
      Serial.print("Nivel de alimento: ");
      Serial.print(leerUltrasonico(TRIG_PIN_ALIM, ECHO_PIN_ALIM, MAX_DIST_ALIM));
      Serial.println("%");
      
      Serial.print("Agua en comedero: ");
      Serial.println(hayAguaSlot() ? "Sí" : "No");
      
      Serial.print("Estado WiFi: ");
      Serial.println(WiFi.status() == WL_CONNECTED ? "Conectado" : "Desconectado");
      
      if (WiFi.status() == WL_CONNECTED) {
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
      }
    }
    else if (inputString == "help") {
      Serial.println("\n--- COMANDOS DISPONIBLES ---");
      Serial.println("1: Servir alimento");
      Serial.println("2: Servir agua");
      Serial.println("3: Reiniciar contador de agua");
      Serial.println("status: Mostrar estado del sistema");
      Serial.println("help: Mostrar esta ayuda");
    }
    else {
      Serial.println("Comando no reconocido. Escriba 'help' para ver la lista de comandos.");
    }
    
    inputString = "";
    stringComplete = false;
  }
}

bool conectarWifiEstatico() {
  Serial.print("Conectando a WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);
  delay(100);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  unsigned long startTime = millis();
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < 20000) {
    delay(500);
    Serial.print(".");
    
    if (intentos++ >= 10) {
      WiFi.disconnect();
      delay(100);
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
      intentos = 0;
    }
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado a WiFi");
    Serial.print("Dirección IP: ");
    Serial.println(WiFi.localIP());
    return true;
  } else {
    Serial.println("\nError de conexión WiFi");
    return false;
  }
}

void medirYPublicar() {
  int nivelAg = leerUltrasonico(TRIG_PIN_AGUA, ECHO_PIN_AGUA, MAX_DIST_AGUA);
  int nivelAl = leerUltrasonico(TRIG_PIN_ALIM, ECHO_PIN_ALIM, MAX_DIST_ALIM);
  bool slot   = hayAguaSlot();

  // Estadísticas consumo
  if (abs(nivelAg - stats.lastNivelAgua) > 2 && nivelAg >= 0 && nivelAg <= 100) {
    if (nivelAg < stats.lastNivelAgua)
      stats.aguaConsumida += (stats.lastNivelAgua - nivelAg) * FACTOR_ML_POR_CM;
    stats.lastNivelAgua = nivelAg;
  }
  
  if (abs(nivelAl - stats.lastNivelAlim) > 2 && nivelAl >= 0 && nivelAl <= 100) {
    if (nivelAl < stats.lastNivelAlim)
      stats.alimConsumido += (stats.lastNivelAlim - nivelAl) * FACTOR_G_POR_CM;
    stats.lastNivelAlim = nivelAl;
  }

  // Construir JSON
  StaticJsonDocument<512> doc;
  doc["nivel_agua"] = nivelAg;
  doc["nivel_alimento"] = nivelAl;
  doc["agua_en_comedero"] = slot;
  doc["tiempo_desde_cambio_agua_s"] = (millis() - lastWaterChange) / 1000;
  doc["tiempo_hasta_prox_alim_s"] = (config.intvAlim ? (config.intvAlim - (millis() - lastFeedTime)) / 1000 : -1);
  doc["alertas"] = JsonObject();
  
  // Agregar alertas
  JsonObject alertas = doc["alertas"];
  if (nivelAg < config.umbralAgua) {
    alertas["agua_baja"] = true;
  }
  if (nivelAl < config.umbralAlim) {
    alertas["alimento_bajo"] = true;
  }
  if (config.intvCambioAgua > 0 && (millis() - lastWaterChange) > config.intvCambioAgua) {
    alertas["cambio_agua"] = true;
  }
  
  JsonObject st = doc.createNestedObject("estadisticas");
  st["agua_ml"] = stats.aguaConsumida;
  st["alimento_g"] = stats.alimConsumido;
  st["veces_agua"] = stats.vecesRellenoAgua;
  st["veces_alim"] = stats.vecesAlimentacion;

  String out;
  serializeJson(doc, out);
  
  // Actualizar endpoint para servir datos JSON
  server.on("/data", HTTP_GET, [out]() {
    server.send(200, "application/json", out);
  });
  
  lastDataSent = millis();
}

void configurarServidor() {
  server.on("/", HTTP_GET, []() {
    String html = "<html><head><title>Alimentador de Mascotas</title>";
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
    html += "<style>body{font-family:Arial;margin:20px;text-align:center;}";
    html += "button{padding:12px 24px;margin:10px;background:#4CAF50;color:white;border:none;border-radius:4px;cursor:pointer;}";
    html += "button:hover{background:#45a049;}</style></head>";
    html += "<body><h1>Alimentador Automatico de Mascotas</h1>";
    html += "<p>Estado del sistema: <b>ACTIVO</b></p>";
    html += "<button onclick='fetch(\"/alimentar\",{method:\"POST\"}).then(()=>alert(\"Alimento servido\"))'>Servir Alimento</button><br>";
    html += "<button onclick='fetch(\"/agua\",{method:\"POST\"}).then(()=>alert(\"Agua servida\"))'>Servir Agua</button><br>";
    html += "<button onclick='fetch(\"/reset_agua\",{method:\"POST\"}).then(()=>alert(\"Contador de agua reiniciado\"))'>Reiniciar contador de agua</button><br>";
    html += "<p><a href='/config'>Configuración avanzada</a> | <a href='/data'>Datos JSON</a></p>";
    html += "</body></html>";
    server.send(200, "text/html", html);
  });
  
  // Endpoint para configuración web
  server.on("/config", HTTP_GET, []() {
    String html = "<html><head><title>Configuración</title>";
    html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
    html += "<style>body{font-family:Arial;margin:20px;text-align:center;}";
    html += "form{max-width:500px;margin:0 auto;text-align:left;}";
    html += "label{display:block;margin:15px 0 5px;}";
    html += "input{width:100%;padding:8px;box-sizing:border-box;}";
    html += "button{padding:10px 20px;margin-top:20px;background:#4CAF50;color:white;border:none;}</style></head>";
    html += "<body><h1>Configuración del Alimentador</h1><form id='configForm'>";
    html += "<label>Duración servir alimento (ms):</label>";
    html += "<input type='number' name='dur_serv_alim' value='" + String(config.durServAlim) + "'>";
    html += "<label>Duración servir agua (ms):</label>";
    html += "<input type='number' name='dur_serv_agua' value='" + String(config.durServAgua) + "'>";
    html += "<label>Intervalo alimentación (ms, 0=desactivado):</label>";
    html += "<input type='number' name='intv_alim' value='" + String(config.intvAlim) + "'>";
    html += "<label>Intervalo cambio agua (ms, 0=desactivado):</label>";
    html += "<input type='number' name='intv_cambio_agua' value='" + String(config.intvCambioAgua) + "'>";
    html += "<label>Umbral bajo nivel agua (%):</label>";
    html += "<input type='number' name='umbral_agua' value='" + String(config.umbralAgua) + "'>";
    html += "<label>Umbral bajo nivel alimento (%):</label>";
    html += "<input type='number' name='umbral_alim' value='" + String(config.umbralAlim) + "'>";
    html += "<label>Umbral sensor agua (ADC):</label>";
    html += "<input type='number' name='umbral_agua_slot' value='" + String(config.umbralAguaSlot) + "'>";
    html += "<label>Auto-rellenar agua:</label>";
    html += "<input type='checkbox' name='auto_refill_agua' " + String(config.autoRefillAgua ? "checked" : "") + ">";
    html += "<button type='button' onclick='guardarConfig()'>Guardar</button>";
    html += "</form><p><a href='/'>Volver</a></p>";
    html += "<script>function guardarConfig() {";
    html += "const form = document.getElementById('configForm');";
    html += "const data = {";
    html += "dur_serv_alim: parseInt(form.dur_serv_alim.value),";
    html += "dur_serv_agua: parseInt(form.dur_serv_agua.value),";
    html += "intv_alim: parseInt(form.intv_alim.value),";
    html += "intv_cambio_agua: parseInt(form.intv_cambio_agua.value),";
    html += "umbral_agua: parseInt(form.umbral_agua.value),";
    html += "umbral_alim: parseInt(form.umbral_alim.value),";
    html += "umbral_agua_slot: parseInt(form.umbral_agua_slot.value),";
    html += "auto_refill_agua: form.auto_refill_agua.checked";
    html += "};";
    html += "fetch('/config', {";
    html += "method: 'POST',";
    html += "headers: {'Content-Type': 'application/json'},";
    html += "body: JSON.stringify(data)";
    html += "}).then(response => response.json())";
    html += ".then(data => alert('Configuración guardada'))";
    html += ".catch(error => alert('Error: ' + error));";
    html += "}</script></body></html>";
    server.send(200, "text/html", html);
  });
  
  // Endpoints manuales
  server.on("/alimentar", HTTP_POST, []() {
    servirAlimento(config.durServAlim);
    lastFeedTime = millis();
    stats.vecesAlimentacion++;
    server.send(200, "application/json", "{\"status\":\"ok\"}");
  });
  
  server.on("/agua", HTTP_POST, []() {
    servirAgua(config.durServAgua);
    stats.vecesRellenoAgua++;
    server.send(200, "application/json", "{\"status\":\"ok\"}");
  });
  
  server.on("/reset_agua", HTTP_POST, []() {
    lastWaterChange = millis();
    server.send(200, "application/json", "{\"status\":\"ok\"}");
  });
  
  // API de Configuración
  server.on("/config", HTTP_POST, []() {
    if (!server.hasArg("plain")) {
      server.send(400, "application/json", "{\"error\":\"no body\"}");
      return;
    }
    
    StaticJsonDocument<512> doc;
    auto err = deserializeJson(doc, server.arg("plain"));
    if (err) {
      server.send(400, "application/json", "{\"error\":\"json\"}");
      return;
    }
    
    if (doc.containsKey("dur_serv_alim"))   config.durServAlim    = doc["dur_serv_alim"];
    if (doc.containsKey("dur_serv_agua"))   config.durServAgua    = doc["dur_serv_agua"];
    if (doc.containsKey("intv_alim"))       config.intvAlim       = doc["intv_alim"];
    if (doc.containsKey("intv_cambio_agua")) config.intvCambioAgua = doc["intv_cambio_agua"];
    if (doc.containsKey("umbral_agua"))     config.umbralAgua     = doc["umbral_agua"];
    if (doc.containsKey("umbral_alim"))     config.umbralAlim     = doc["umbral_alim"];
    if (doc.containsKey("umbral_agua_slot")) config.umbralAguaSlot = doc["umbral_agua_slot"];
    if (doc.containsKey("auto_refill_agua")) config.autoRefillAgua = doc["auto_refill_agua"];
    
    guardarConfig();
    server.send(200, "application/json", "{\"status\":\"saved\"}");
  });
  
  server.onNotFound([]() {
    server.send(404, "application/json", "{\"error\":\"not found\"}");
  });
}

int leerUltrasonico(uint8_t trig, uint8_t echo, int maxDist) {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  
  long timeoutMicros = maxDist * 58 * 2;
  long dur = pulseIn(echo, HIGH, timeoutMicros);
  
  if (dur == 0) {
    return -1;
  }
  
  float dist = dur * 0.034 / 2;
  dist = min(dist, float(maxDist));
  int pct = 100 - int(dist / maxDist * 100);
  return constrain(pct, 0, 100);
}

bool hayAguaSlot() {
  int valorADC = analogRead(WATER_SLOT_PIN);
  return valorADC > config.umbralAguaSlot;
}

void servirAlimento(unsigned long durMs) {
  Serial.print("Sirviendo alimento durante ");
  Serial.print(durMs);
  Serial.println(" ms");
  
  unsigned long t0 = millis();
  while (millis() - t0 < durMs) {
    for (uint8_t s = 0; s < STEPS; s++) {
      digitalWrite(M1, seq[s][0]);
      digitalWrite(M2, seq[s][1]);
      digitalWrite(M3, seq[s][2]);
      digitalWrite(M4, seq[s][3]);
      delay(2);
    }
  }
  // Desactivar bobinas para evitar calentamiento
  digitalWrite(M1, LOW); digitalWrite(M2, LOW);
  digitalWrite(M3, LOW); digitalWrite(M4, LOW);
  
  Serial.println("Alimento servido");
}

void servirAgua(unsigned long durMs) {
  Serial.print("Sirviendo agua durante ");
  Serial.print(durMs);
  Serial.println(" ms");
  
  digitalWrite(VALVE_PIN, HIGH);
  delay(durMs);
  digitalWrite(VALVE_PIN, LOW);
  
  Serial.println("Agua servida");
}

void guardarConfig() {
  EEPROM.put(SYSTEM_CONFIG_ADDR, config);
  EEPROM.commit();
  Serial.println("Configuración guardada en EEPROM");
}

void cargarConfig() {
  EEPROM.get(SYSTEM_CONFIG_ADDR, config);
  // Validar configuración
  if (config.durServAlim == 0 || config.durServAlim > 60000 || 
      config.durServAgua == 0 || config.durServAgua > 60000) {
    Serial.println("Configuración inválida, cargando valores predeterminados");
    config = Config{};
    guardarConfig();
  } else {
    Serial.println("Configuración cargada desde EEPROM");
  }
}