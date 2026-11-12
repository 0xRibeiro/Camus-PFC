#include "tela_modulos.h"

#include "../../hardware/display.h"

void TelaModulos::desenhar() {
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(2);
  display::tft.setCursor(10, 50);
  display::tft.print("Modulos");
}

// tela só de info, sem interação
void TelaModulos::aoEvento(joystick::Evento evento) {}

