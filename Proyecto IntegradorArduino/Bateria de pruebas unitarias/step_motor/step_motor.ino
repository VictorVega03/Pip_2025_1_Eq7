// Motor Paso a Paso 28BYJ-48 para ESP8266 NodeMCU

// Pines conectados al ULN2003
int IN1 = 13;  // D7 (GPIO13)
int IN2 = 15;  // D8 (GPIO15)
int IN3 = 14;  // D5 (GPIO14)
int IN4 = 12;  // D6 (GPIO12)

// Secuencia de pasos para el 28BYJ-48
int pasos[8][4] = {
  {1, 0, 0, 0},
  {1, 1, 0, 0},
  {0, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 0},
  {0, 0, 1, 1},
  {0, 0, 0, 1},
  {1, 0, 0, 1}
};

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  
  delay(1000);
}

void loop() {
  // Gira en sentido horario
  for (int i = 0; i < 512; i++) { // 512 pasos = 1 vuelta completa
    for (int j = 0; j < 8; j++) {
      digitalWrite(IN1, pasos[j][0]);
      digitalWrite(IN2, pasos[j][1]);
      digitalWrite(IN3, pasos[j][2]);
      digitalWrite(IN4, pasos[j][3]);
      delay(2);
    }
  }

  // Apagar las bobinas para evitar calentamiento
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  
  delay(1000);

  // Gira en sentido antihorario
  for (int i = 0; i < 512; i++) {
    for (int j = 7; j >= 0; j--) {
      digitalWrite(IN1, pasos[j][0]);
      digitalWrite(IN2, pasos[j][1]);
      digitalWrite(IN3, pasos[j][2]);
      digitalWrite(IN4, pasos[j][3]);
      delay(2);
    }
  }

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  
  delay(1000);
}