#include <Arduino.h>

#include "hardware/buzzer.h"
#include "hardware/display.h"
#include "hardware/joystick.h"
#include "hardware/sons.h"
#include "ui/navbar.h"
#include "ui/navegacao.h"

bool wifiTeste = true;

void setup() {
  Serial.begin(115200);

  display::iniciar();
  joystick::iniciar();
  buzzer::iniciar();
  navegacao::iniciar();

  // TESTE: erro no boot só pra ouvir ele
  buzzer::tocar(sons::ERRO);

  // TESTE: liga os dois avisos pra ver piscando
  navbar::avisarModuloNovo();
  navbar::avisarModuloSaiu();
}

void loop() {
  joystick::Evento evento = joystick::atualizar();
  navegacao::atualizar(evento);
  buzzer::atualizar();

  // TESTE: clique liga/desliga o wifi falso, sai quando tiver wifi de vdd
  if (evento == joystick::Evento::CLIQUE) {
    wifiTeste = !wifiTeste;
    navbar::definirWifi(wifiTeste);

    if (wifiTeste) {
      buzzer::tocar(sons::WIFI_CONECTOU);
    } else {
      buzzer::tocar(sons::WIFI_CAIU);
    }
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
