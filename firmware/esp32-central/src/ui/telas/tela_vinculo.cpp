#include "tela_vinculo.h"

#include "../../hardware/display.h"
#include "../navbar.h"

void TelaVinculo::desenhar() {
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(1);
  display::tft.setCursor(4, navbar::ALTURA + 4);
  display::tft.print("Sem codigo ainda");
}

void TelaVinculo::aoEvento(joystick::Evento evento) {}

const char* TelaVinculo::nome() {
  return "Vinculo";
}