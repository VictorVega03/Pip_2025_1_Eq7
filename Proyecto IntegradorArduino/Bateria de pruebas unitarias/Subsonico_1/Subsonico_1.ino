// Sensor ultrasónico HC-SR04 con ESP8266
// TRIG -> D1 (GPIO5), ECHO -> D2 (GPIO4)

const int trigPin = 5;  // Pin D1 (GPIO5)
const int echoPin = 4;  // Pin D2 (GPIO4)

long duracion;
float distancia;

void setup() {
  Serial.begin(9600);
  delay(100);
  
  Serial.println();
  Serial.println("Prueba de Sensor Ultrasonico HC-SR04");
  Serial.println("====================================");
  
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  digitalWrite(trigPin, LOW);
  delay(500);
}

void loop() {
  // Limpiar el pin TRIG
  digitalWrite(trigPin