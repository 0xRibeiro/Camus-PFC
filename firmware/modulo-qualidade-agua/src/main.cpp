#include <Arduino.h>
#include <EEPROM.h>
#include <Wire.h>
#include <protocolo.h>

#define TDS A0
#define TURBIDEZ A1

// a0 tem sensor agora, o a7 fica solto pro sorteio do serial
#define PINO_SEMENTE A7

#define INTERVALO_MS 5000
#define AMOSTRA_MS 40
#define AMOSTRAS 30

// adc de 10 bits no 5v do nano
#define TENSAO_REF 5.0
#define ADC_MAX 1024.0

// sem sensor de temperatura aqui, compensa como se fosse 25c
#define TEMPERATURA_TDS 25.0

uint32_t serial = 0;

// escritas no loop, lidas na interrupcao do i2c
volatile uint8_t registrador = 0;
volatile int16_t tdsPpm = 0;
volatile int16_t turbidezNtu = 0;
volatile bool temNova = false;

int amostrasTds[AMOSTRAS];
int amostrasTurbidez[AMOSTRAS];
int posicao = 0;
bool encheu = false;

unsigned long ultimaAmostra = 0;
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
    semente = (semente << 1) ^ analogRead(PINO_SEMENTE);
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
  resposta[1] = (uint8_t) TipoModulo::QUALIDADE_AGUA;
  resposta[2] = serial >> 24;
  resposta[3] = serial >> 16;
  resposta[4] = serial >> 8;
  resposta[5] = serial;
  resposta[6] = crc8(resposta, TAM_IDENTIFICACAO - 1);
  Wire.write(resposta, TAM_IDENTIFICACAO);
}

// ordem igual ao catalogo do esp: tds, turbidez
void responderLeitura() {
  uint8_t resposta[TAM_LEITURA] = {0};
  resposta[0] = temNova;
  resposta[1] = 2;
  resposta[2] = tdsPpm >> 8;
  resposta[3] = tdsPpm;
  resposta[4] = turbidezNtu >> 8;
  resposta[5] = turbidezNtu;
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

// mediana tira os picos de ruido do adc
float tensaoMediana(const int* amostras) {
  int ordenadas[AMOSTRAS];
  for (int i = 0; i < AMOSTRAS; i++) {
    ordenadas[i] = amostras[i];
  }

  for (int i = 1; i < AMOSTRAS; i++) {
    int atual = ordenadas[i];
    int j = i - 1;
    while (j >= 0 && ordenadas[j] > atual) {
      ordenadas[j + 1] = ordenadas[j];
      j--;
    }
    ordenadas[j + 1] = atual;
  }

  return ordenadas[AMOSTRAS / 2] * TENSAO_REF / ADC_MAX;
}

// curva da dfrobot (sen0244), resultado em ppm
int16_t calcularTds(float tensao) {
  float compensada = tensao / (1.0 + 0.02 * (TEMPERATURA_TDS - 25.0));
  float ppm = (133.42 * compensada * compensada * compensada
    - 255.86 * compensada * compensada
    + 857.39 * compensada) * 0.5;

  if (ppm < 0) {
    return 0;
  }
  return ppm;
}

// curva da dfrobot (sen0189), so vale de 2,5v a 4,2v. ntu x10
int16_t calcularTurbidez(float tensao) {
  if (tensao >= 4.2) {
    return 0;
  }
  if (tensao <= 2.5) {
    return 30000;
  }

  float ntu = -1120.4 * tensao * tensao + 5742.3 * tensao - 4352.9;
  if (ntu < 0) {
    return 0;
  }
  return ntu * 10;
}

void setup() {
  Serial.begin(115200);

  carregarSerial();
  Serial.print("serial: ");
  Serial.println(serial, HEX);

  Wire.begin(ENDERECO_QUALIDADE_AGUA);
  // tira o pull-up de 5v, o barramento fica no 3v3 do esp
  digitalWrite(SDA, LOW);
  digitalWrite(SCL, LOW);
  Wire.onReceive(aoReceber);
  Wire.onRequest(aoPedir);
}

void loop() {
  if (millis() - ultimaAmostra >= AMOSTRA_MS) {
    ultimaAmostra = millis();
    amostrasTds[posicao] = analogRead(TDS);
    amostrasTurbidez[posicao] = analogRead(TURBIDEZ);

    posicao++;
    if (posicao == AMOSTRAS) {
      posicao = 0;
      encheu = true;
    }
  }

  if (!encheu || millis() - ultimaMedida < INTERVALO_MS) {
    return;
  }
  ultimaMedida = millis();

  float tensaoTds = tensaoMediana(amostrasTds);
  float tensaoTurbidez = tensaoMediana(amostrasTurbidez);
  int16_t tds = calcularTds(tensaoTds);
  int16_t turbidez = calcularTurbidez(tensaoTurbidez);

  noInterrupts();
  tdsPpm = tds;
  turbidezNtu = turbidez;
  temNova = true;
  interrupts();

  Serial.print("tds v: ");
  Serial.print(tensaoTds, 2);
  Serial.print(" ppm: ");
  Serial.print(tds);
  Serial.print(" | turbidez v: ");
  Serial.print(tensaoTurbidez, 2);
  Serial.print(" ntu x10: ");
  Serial.println(turbidez);
}
