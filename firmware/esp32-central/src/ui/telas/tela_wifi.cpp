#include "tela_wifi.h"

#include "../../hardware/display.h"

void TelaWifi::desenhar() {
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(2);
  display::tft.setCursor(10, 50);
  display::tft.print("Wi-Fi");
}

void TelaWifi::aoEvento(joystick::Evento evento) {}