#pragma once

#include <Adafruit_ST7735.h>

// o tft fica aberto pra navbar e telas desenharem
namespace display {
  extern Adafruit_ST7735 tft;
  void iniciar();
}