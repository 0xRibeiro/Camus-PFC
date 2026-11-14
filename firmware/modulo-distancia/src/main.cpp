#include <Arduino.h>
#include <EEPROM.h>
#include <Wire.h>
#include <protocolo.h>

#define TRIG 2
#define ECHO 3
#define INTERVALO_MS 5000

// sem eco em 30ms = nada na frente (~5m)
#define ECO_TIMEOUT_US 30000

uint32_t serial = 0;

// escritas no loop, lidas na interrupcao do i2c
volatile uint8_t registrador = 0;
volatile int16_t distanciaMm = 0;
volatile bool temNova = false;

unsigned long ultimaMedida = 0;

void carregarSerial() {
  EEPROM.get(0, serial);

  // eeprom 
  if (serial != 0xFFFFFFFF && serial != 0) {
    return;
  }

  // ruido do pino solto + tempo, so pra n repetir entre placas
  uint32_t semente = micros();
  for (int i = 0; i < 32; i++) {
    semente = (semente << 1) ^ analogRead(A0);
  }
  randomSeed(semente);

  serial = ((uint32_t) random(0x10000) << 16) | random(0x10000);
  EEPROM.put(0, serial);
}

void aoReceber(int quantidade) {
  registrador = Wire.read();

  while (Wire.available()) {
    Wire.read();
  }
}

void responderIdentificacao() {
  uint8_t resposta[TAM_IDENTIFICACAO];
  resposta[0] = PROTOCOLO_VERSAO;
  resposta[1] = (uint8_t) TipoModulo::DISTANCIA;
  resposta[2] = serial >> 24;
  resposta[3] = serial >> 16;
  resposta[4] = serial >> 8;
  resposta[5] = serial;
  resposta[6] = crc8(resposta, TAM_IDENTIFICACAO - 1);
  Wire.write(resposta, TAM_IDENTIFICACAO);
}

void responderLeitura() {
  uint8_t resposta[TAM_LEITURA] = {0};
  resposta[0] = temNova;
  resposta[1] = 1;
  resposta[2] = distanciaMm >> 8;
  resposta[3] = distanciaMm;
  resposta[TAM_LEITURA - 1] = crc8(resposta, TAM_LEITURA - 1);
  Wire.write(resposta, TAM_LEITURA);

  temNova = false;
}

// roda na interrupcao, so responde
void aoPedir() {
  if (registrador == REG_IDENTIFICACAO) {
    responderIdentificacao();
  } else if (registrador == REG_LEITURA) {
    responderLeitura();
  }
}

// valor em cm x10 = mm
int16_t medir() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  unsigned long duracao = pulseIn(ECHO, HIGH, ECO_TIMEOUT_US);

  // som a 0,343 mm/us, ida e volta
  return duracao * 343 / 2000;
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  carregarSerial();
  Serial.print("serial: ");
  Serial.println(serial, HEX);

  Wire.begin(ENDERECO_DISTANCIA);
  // tira o pull-up de 5v, o barramento fica no 3v3 do esp
  digitalWrite(SDA, LOW);
  digitalWrite(SCL, LOW);
  Wire.onReceive(aoReceber);
  Wire.onRequest(aoPedir);
}

void loop() {
  if (millis() - ultimaMedida < INTERVALO_MS) {
    return;
  }
  ultimaMedida = millis();

  int16_t medida = medir();
  if (medida == 0) {
    return;
  }

  noInterrupts();
  distanciaMm = medida;
  temNova = true;
  interrupts();

  Serial.print("distancia mm: ");
  Serial.println(medida);
}