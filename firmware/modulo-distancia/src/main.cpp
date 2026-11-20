#include <Arduino.h>
#include <modulo.h>

// sensor ultrassonico: trig solta o som e echo fica em high ate o eco voltar
#define TRIG 2
#define ECHO 3

#define INTERVALO_MS 5000

// sem eco em 30ms = nada na frente, uns 5m
#define ECO_TIMEOUT_US 30000

unsigned long ultimaMedida = 0;

// pulso de 10us no trig faz o sensor soltar o som
void dispararSom() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
}

// distancia em mm, q e cm x10. 0 = eco n voltou
int16_t medirDistancia() {
  dispararSom();
  unsigned long duracao = pulseIn(ECHO, HIGH, ECO_TIMEOUT_US);

  // som anda 0,343 mm por us, divide por 2 pq o tempo e de ida e volta
  return duracao * 343 / 2000;
}

void setup() {
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  modulo::iniciar(TipoModulo::DISTANCIA, ENDERECO_DISTANCIA, A0);
}

void loop() {
  if (millis() - ultimaMedida < INTERVALO_MS) {
    return;
  }
  ultimaMedida = millis();

  int16_t milimetros = medirDistancia();
  if (milimetros == 0) {
    return;
  }

  modulo::entregarLeitura(milimetros);

  Serial.print("distancia mm: ");
  Serial.println(milimetros);
}
