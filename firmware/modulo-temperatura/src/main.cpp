#include <Arduino.h>
#include <DallasTemperature.h>
#include <EEPROM.h>
#include <OneWire.h>
#include <Wire.h>
#include <protocolo.h>

#define SENSOR 2
#define RELE 3

// ky-019, transistor npn: ativo em high
#define RELE_LIGA HIGH
#define INTERVALO_MS 5000

// 12 bits leva ate 750ms
#define CONVERSAO_MS 750

uint32_t serial = 0;

// escritas no loop, lidas na interrupcao do i2c
volatile uint8_t registrador = 0;
volatile int16_t temperatura = 0;
volatile bool temNova = false;

// escrito na interrupcao, o loop aplica no pino
volatile bool releLigado = false;

unsigned long ultimaMedida = 0;
bool convertendo = false;

OneWire barramento(SENSOR);
DallasTemperature sensor(&barramento);

void carregarSerial() {
  EEPROM.get(0, serial);

  // eeprom
  if (serial != 0xFFFFFFFF && serial != 0) {
    return;
  }

  
  uint32_t semente = micros();
  for (int i = 0; i < 32; i++) {
    semente = (semente << 1) ^ analogRead(A0);
  }
  randomSeed(semente);

  serial = ((uint32_t) random(0x10000) << 16) | random(0x10000);
  EEPROM.put(0, serial);
}

// comando vem junto do registrador
void aoReceber(int quantidade) {
  registrador = Wire.read();

  if (registrador == REG_COMANDO && Wire.available()) {
    releLigado = Wire.read() == 1;
  }

  while (Wire.available()) {
    Wire.read();
  }
}

void responderIdentificacao() {
  uint8_t resposta[TAM_IDENTIFICACAO];
  resposta[0] = PROTOCOLO_VERSAO;
  resposta[1] = (uint8_t) TipoModulo::TEMPERATURA;
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
  resposta[2] = temperatura >> 8;
  resposta[3] = temperatura;
  resposta[TAM_LEITURA - 1] = crc8(resposta, TAM_LEITURA - 1);
  Wire.write(resposta, TAM_LEITURA);

  temNova = false;
}

void responderEstado() {
  uint8_t resposta[TAM_ESTADO];
  resposta[0] = releLigado;
  resposta[1] = crc8(resposta, TAM_ESTADO - 1);
  Wire.write(resposta, TAM_ESTADO);
}

// roda na interrupcao, so responde
void aoPedir() {
  if (registrador == REG_IDENTIFICACAO) {
    responderIdentificacao();
  } else if (registrador == REG_LEITURA) {
    responderLeitura();
  } else if (registrador == REG_ESTADO) {
    responderEstado();
  }
}

// valor em c x100, -12700 = sensor solto ou sem pull-up
int16_t lerTemperatura() {
  float celsius = sensor.getTempCByIndex(0);
  return celsius * 100;
}

void aplicarRele() {
  if (releLigado) {
    digitalWrite(RELE, RELE_LIGA);
  } else {
    digitalWrite(RELE, !RELE_LIGA);
  }
}

void setup() {
  Serial.begin(115200);

  // nivel de desligado antes de virar saida, pra n dar um pulso no boot
  aplicarRele();
  pinMode(RELE, OUTPUT);

  sensor.begin();
  sensor.setWaitForConversion(false);

  carregarSerial();
  Serial.print("serial: ");
  Serial.println(serial, HEX);

  Wire.begin(ENDERECO_TEMPERATURA);
  // tira o pull-up de 5v, o barramento fica no 3v3 do esp
  digitalWrite(SDA, LOW);
  digitalWrite(SCL, LOW);
  Wire.onReceive(aoReceber);
  Wire.onRequest(aoPedir);
}

void loop() {
  aplicarRele();

  // pede a conversao e volta, sem esperar
  if (!convertendo && millis() - ultimaMedida >= INTERVALO_MS) {
    sensor.requestTemperatures();
    ultimaMedida = millis();
    convertendo = true;
    return;
  }

  if (!convertendo || millis() - ultimaMedida < CONVERSAO_MS) {
    return;
  }
  convertendo = false;

  int16_t medida = lerTemperatura();
  if (medida == DEVICE_DISCONNECTED_C * 100) {
    Serial.println("sem sensor");
    return;
  }

  noInterrupts();
  temperatura = medida;
  temNova = true;
  interrupts();

  Serial.print("temperatura c x100: ");
  Serial.println(medida);
}
