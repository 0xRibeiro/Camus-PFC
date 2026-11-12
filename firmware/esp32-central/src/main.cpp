#include <Arduino.h>

#include "hardware/display.h"
#include "hardware/joystick.h"

// teste, sai na etapa 3
const char* nomeDoEvento(joystick::Evento evento) {
  switch (evento) {
    case joystick::Evento::ESQUERDA: return "ESQUERDA";
    case joystick::Evento::DIREITA: return "DIREITA";
    case joystick::Evento::CIMA: return "CIMA";
    case joystick::Evento::BAIXO: return "BAIXO";
    case joystick::Evento::CLIQUE: return "CLIQUE";
    default: return "NENHUM";
  }
}

void setup() {
  Serial.begin(115200);

  display::iniciar();
  joystick::iniciar();

  display::tft.setTextColor(ST77XX_GREEN);
  display::tft.setTextSize(2);
}

void loop() {
  joystick::Evento evento = joystick::atualizar();

  if (evento != joystick::Evento::NENHUM) {
    Serial.println(nomeDoEvento(evento));

    // apaga o texto anterior e escreve o novo
    display::tft.fillRect(0, 50, 160, 20, ST77XX_BLACK);
    display::tft.setCursor(10, 50);
    display::tft.print(nomeDoEvento(evento));
  }
}
