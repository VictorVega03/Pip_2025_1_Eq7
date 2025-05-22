#include <ESP8266WiFi.h>

// Pin del sensor ultrasónico de alimento
constexpr uint8_t TRIG_PIN_ALIM = 14;  // D5 (GPIO14)
constexpr uint8_t ECHO_PIN_ALIM = 12;  // D6 (GPIO12)

void setup() {
  Serial.begin(9600);
  Serial.println("\n\nPrueba del sensor ultrasónico de alimento");
  
  pinMode(TRIG_PIN_ALIM, OUTPUT);
  pinMode(ECHO_PIN_ALIM, INPUT);
  
  digitalWrite(TRIG_PIN_ALIM, LOW);
  
  delay(2000);
}

void loop() {
  long duracion;
  float distanciaCm;
  int porcentaje;
  
  Serial.println("\n----- Nueva medición -----");
  
  // Generar pulso limpio
  digitalWrite(TRIG_PIN_ALIM, LOW);
  delayMicroseconds(5);
  
  digitalWrite(TRIG_PIN_ALIM, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN_ALIM, LOW);
  
  // Medir el tiempo de eco con timeout
  duracion = pulseIn(ECHO_PIN_ALIM, HIGH, 30000);
  
  Serial.print("Tiempo de eco (microsegundos): ");
  Serial.println(duracion);
  
  if (duracion > 0) {
    distanciaCm = duracion * 0.034 / 2.0;
    
    if (distanciaCm > 25) {
      distanciaCm = 25;
    }
    
    // Calcular porcentaje (0% = vacío/25cm, 100% = lleno/0cm)
    porcentaje = 100 - (distanciaCm * 100 / 25);
  } else {
    distanciaCm = -1;
    porcentaje = -1;
    Serial.println("ERROR: No se detectó eco - Verifica el cableado");
  }
  
  Serial.print("Distancia medida (cm): ");
  Serial.println(distanciaCm);
  Serial.print("Nivel de llenado (%): ");
  Serial.println(porcentaje);
  
  Serial.print("Estado actual del pin ECHO: ");
  Serial.println(digitalRead(ECHO_PIN_ALIM));
  
  delay(2000);
}