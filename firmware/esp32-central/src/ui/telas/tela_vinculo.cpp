#include "tela_vinculo.h"

#include "../../hardware/display.h"

void TelaVinculo::desenhar() {
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(2);
  display::tft.setCursor(10, 50);
  display::tft.print("Vinculo");
}

void TelaVinculo::aoEvento(joystick::Evento evento) {}