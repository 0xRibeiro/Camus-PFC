#include <Arduino.h>

#include "hardware/buzzer.h"
#include "hardware/display.h"
#include "hardware/joystick.h"
#include "hardware/sons.h"
#include "modulos/barramento.h"
#include "rede/mqtt.h"
#include "rede/wifi.h"
#include "ui/navbar.h"
#include "ui/navegacao.h"

void setup() {
  Serial.begin(115200);

  display::iniciar();
  joystick::iniciar();
  buzzer::iniciar();
  wifi::iniciar();
  mqtt::iniciar();
  barramento::iniciar();
  navegacao::iniciar();
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
    barramento::publicarModulos();
  } else if (eventoMqtt == mqtt::Evento::CAIU) {
    navbar::definirBroker(false);
  }

  barramento::Evento eventoModulo = barramento::atualizar();
  if (eventoModulo == barramento::Evento::ENTROU) {
    navbar::avisarModuloNovo();
    buzzer::tocar(sons::MODULO_NOVO);
  } else if (eventoModulo == barramento::Evento::SAIU) {
    navbar::avisarModuloSaiu();
    buzzer::tocar(sons::MODULO_SAIU);
  } else if (eventoModulo == barramento::Evento::REPETIDO) {
    buzzer::tocar(sons::ERRO);
  }
}
