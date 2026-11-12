#include <Arduino.h>

#include "hardware/display.h"
#include "hardware/joystick.h"
#include "ui/navbar.h"
#include "ui/navegacao.h"

bool wifiTeste = true;

void setup() {
  Serial.begin(115200);

  display::iniciar();
  joystick::iniciar();
  navegacao::iniciar();

  // TESTE: liga os dois avisos pra ver piscando
  navbar::avisarModuloNovo();
  navbar::avisarModuloSaiu();
}

void loop() {
  joystick::Evento evento = joystick::atualizar();
  navegacao::atualizar(evento);

  // TESTE: clique liga/desliga o wifi falso, sai quando tiver wifi de vdd
  if (evento == joystick::Evento::CLIQUE) {
    wifiTeste = !wifiTeste;
    navbar::definirWifi(wifiTeste);
  }

  // TESTE: cima liga o +, baixo liga o -
  if (evento == joystick::Evento::CIMA) {
    navbar::avisarModuloNovo();
  } else if (evento == joystick::Evento::BAIXO) {
    navbar::avisarModuloSaiu();
  }
}
