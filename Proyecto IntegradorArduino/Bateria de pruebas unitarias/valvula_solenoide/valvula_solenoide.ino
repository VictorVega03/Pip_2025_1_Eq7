#include <Arduino.h>

// Pin para el relé (ESP32)
const uint8_t RELE_PIN = 17;  // GPIO17

void setup() {
  Serial.begin(115200);
  Serial.println("Iniciando control de válvula solenoide ARD-317");
  
  pinMode(RELE_PIN, OUTPUT);
  
  // Válvula cerrada al inicio
  digitalWrite(RELE_PIN, LOW);
  Serial.println("Válvula cerrada al inicio");
}

void loop() {
  // Abrir válvula por 5 segundos
  Serial.println("Abriendo válvula...");
  digitalWrite(RELE_PIN, HIGH);
  delay(5000);
  
  // Cerrar válvula por 5 segundos
  Serial.println("Cerrando válvula...");
  digitalWrite(RELE_PIN, LOW);
  delay(5000);
}