#include <Arduino.h>

#include "hardware/display.h"
#include "hardware/joystick.h"
#include "ui/navegacao.h"

void setup() {
  Serial.begin(115200);

  display::iniciar();
  joystick::iniciar();
  navegacao::iniciar();
}

void loop() {
  joystick::Evento evento = joystick::atualizar();
  navegacao::atualizar(evento);
}
