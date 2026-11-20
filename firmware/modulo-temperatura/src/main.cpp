#include <Arduino.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include <modulo.h>

// ds18b20 e digital e conversa por 1 fio so, o onewire
#define SENSOR 2
#define RELE 3

// rele ky-019 liga com high
#define RELE_LIGA HIGH
#define INTERVALO_MS 5000

// sensor leva ate 750ms pra medir na precisao maxima
#define CONVERSAO_MS 750

OneWire fio(SENSOR);
DallasTemperature sensor(&fio);

unsigned long inicioConversao = 0;
bool convertendo = false;

// segue o ultimo pedido da esp
void aplicarRele() {
  if (modulo::releLigado()) {
    digitalWrite(RELE, RELE_LIGA);
  } else {
    digitalWrite(RELE, !RELE_LIGA);
  }
}

// pede a medida e volta pro loop, sem travar os 750ms esperando
void pedirConversao() {
  sensor.requestTemperatures();
  inicioConversao = millis();
  convertendo = true;
}

bool conversaoPronta() {
  return convertendo && millis() - inicioConversao >= CONVERSAO_MS;
}

// vai em c x100, 25,37 c vira 2537
void lerEEntregar() {
  convertendo = false;
  float celsius = sensor.getTempCByIndex(0);

  // -127 = lib n achou o sensor, fio solto ou sem resistor
  if (celsius == DEVICE_DISCONNECTED_C) {
    Serial.println("sem sensor");
    return;
  }

  int16_t centesimos = celsius * 100;
  modulo::entregarLeitura(centesimos);

  Serial.print("temperatura c x100: ");
  Serial.println(centesimos);
}

void setup() {
  // deixa desligado antes de virar saida, senao o rele da um pulso no boot
  aplicarRele();
  pinMode(RELE, OUTPUT);

  sensor.begin();
  sensor.setWaitForConversion(false);

  modulo::iniciar(TipoModulo::TEMPERATURA, ENDERECO_TEMPERATURA, A0);
}

// pede a cada 5s e le 750ms depois
void loop() {
  aplicarRele();

  if (!convertendo && millis() - inicioConversao >= INTERVALO_MS) {
    pedirConversao();
  } else if (conversaoPronta()) {
    lerEEntregar();
  }
}
