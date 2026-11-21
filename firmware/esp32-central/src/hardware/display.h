#pragma once

#include <Adafruit_ST7735.h>

// tft e a tela. extern avisa q ela existe e e criada no display.cpp,
// assim navbar e telas usam a msm
namespace display {
  extern Adafruit_ST7735 tft;
  void iniciar();
}