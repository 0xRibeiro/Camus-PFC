#include <Arduino.h>
#include <Wire.h>
#include <protocolo.h>

#include "config.h"
#include "hardware/buzzer.h"
#include "hardware/display.h"
#include "hardware/joystick.h"
#include "hardware/sons.h"
#include "rede/mqtt.h"
#include "rede/wifi.h"
#include "ui/navbar.h"
#include "ui/navegacao.h"

// TESTE: le o modulo de distancia, sai na etapa 12
unsigned long ultimoTeste = 0;

bool lerRegistrador(uint8_t registrador, uint8_t* resposta, uint8_t tamanho) {
  Wire.beginTransmission(ENDERECO_DISTANCIA);
  Wire.write(registrador);
  uint8_t erro = Wire.endTransmission();
  if (erro != 0) {
    Serial.printf("i2c: erro %d no envio\n", erro);
    return false;
  }

  uint8_t recebidos = Wire.requestFrom(ENDERECO_DISTANCIA, tamanho);
  if (recebidos != tamanho) {
    Serial.printf("i2c: veio %d de %d bytes\n", recebidos, tamanho);
    return false;
  }
  for (uint8_t i = 0; i < tamanho; i++) {
    resposta[i] = Wire.read();
  }

  return crc8(resposta, tamanho - 1) == resposta[tamanho - 1];
}

void escanear() {
  Serial.println("scan: inicio");
  for (uint8_t endereco = ENDERECO_PRIMEIRO; endereco <= ENDERECO_ULTIMO; endereco++) {
    Wire.beginTransmission(endereco);
    if (Wire.endTransmission() == 0) {
      Serial.printf("scan: achou 0x%02X\n", endereco);
    }
  }
  Serial.println("scan: fim");
}

void testarModulo() {
  uint8_t id[TAM_IDENTIFICACAO];
  if (!lerRegistrador(REG_IDENTIFICACAO, id, TAM_IDENTIFICACAO)) {
    Serial.println("modulo: sem resposta ou crc errado");
    return;
  }

  unsigned long serial = ((unsigned long) id[2] << 24) | ((unsigned long) id[3] << 16) |
                         ((unsigned long) id[4] << 8) | id[5];
  Serial.printf("modulo: versao %d tipo %d serial %08lX\n", id[0], id[1], serial);

  uint8_t leitura[TAM_LEITURA];
  if (!lerRegistrador(REG_LEITURA, leitura, TAM_LEITURA)) {
    Serial.println("leitura: crc errado");
    return;
  }

  int16_t mm = (leitura[2] << 8) | leitura[3];
  Serial.printf("leitura: nova %d qtd %d mm %d\n", leitura[0], leitura[1], mm);
}

void setup() {
  Serial.begin(115200);

  display::iniciar();
  joystick::iniciar();
  buzzer::iniciar();
  wifi::iniciar();
  mqtt::iniciar();
  navegacao::iniciar();
  Wire.begin(I2C_SDA, I2C_SCL);
  escanear();

  // TESTE: liga os dois avisos pra ver piscando
  navbar::avisarModuloNovo();
  navbar::avisarModuloSaiu();
}

void loop() {
  joystick::Evento evento = joystick::atualizar();
  navegacao::atualizar(evento);
  buzzer::atualizar();

  // wifi avisa a navbar e o buzzer só qnd muda
  wifi::Evento eventoWifi = wifi::atualizar();
  if (eventoWifi == wifi::Evento::CONECTOU) {
    navbar::definirWifi(true);
    buzzer::tocar(sons::WIFI_CONECTOU);
  } else if (eventoWifi == wifi::Evento::CAIU) {
    navbar::definirWifi(false);
    buzzer::tocar(sons::WIFI_CAIU);
  }

  // broker so mexe no icone, sem som
  mqtt::Evento eventoMqtt = mqtt::atualizar();
  if (eventoMqtt == mqtt::Evento::CONECTOU) {
    navbar::definirBroker(true);
  } else if (eventoMqtt == mqtt::Evento::CAIU) {
    navbar::definirBroker(false);
  }

  // TESTE: modulo a cada 2s
  if (millis() - ultimoTeste > 2000) {
    ultimoTeste = millis();
    testarModulo();
  }

  // TESTE: cima liga o +, baixo liga o -
  if (evento == joystick::Evento::CIMA) {
    navbar::avisarModuloNovo();
    buzzer::tocar(sons::MODULO_NOVO);
  } else if (evento == joystick::Evento::BAIXO) {
    navbar::avisarModuloSaiu();
    buzzer::tocar(sons::MODULO_SAIU);
  }
}
