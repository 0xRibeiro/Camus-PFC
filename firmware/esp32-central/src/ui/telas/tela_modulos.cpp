#include "tela_modulos.h"

#include "../../hardware/display.h"
#include "../navbar.h"

void TelaModulos::desenhar() {
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(1);
  display::tft.setCursor(4, navbar::ALTURA + 4);
  display::tft.print("Nenhum modulo");
}

// tela só de info, sem interação
void TelaModulos::aoEvento(joystick::Evento evento) {}

const char* TelaModulos::nome() {
  return "Modulos";
}

