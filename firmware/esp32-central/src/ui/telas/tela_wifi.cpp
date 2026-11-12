#include "tela_wifi.h"

#include "../../hardware/display.h"
#include "../navbar.h"

void TelaWifi::desenhar() {
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(1);
  display::tft.setCursor(4, navbar::ALTURA + 4);
  display::tft.print("Sem rede configurada");
}

void TelaWifi::aoEvento(joystick::Evento evento) {}

const char* TelaWifi::nome() {
  return "Wi-Fi";
}