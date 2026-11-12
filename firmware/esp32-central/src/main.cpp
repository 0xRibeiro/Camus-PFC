#include <Arduino.h>

#include "hardware/display.h"

void setup() {
  display::iniciar();

  // teste da tela
  display::tft.setCursor(0, 3);
  display::tft.setTextColor(ST77XX_GREEN);
  display::tft.setTextSize(1);
  display::tft.println("Camus vai dominar o mundo dos aquarios");
}

void loop() {}
