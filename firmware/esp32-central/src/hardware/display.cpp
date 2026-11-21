#include "display.h"

#include <SPI.h>

#include "../config.h"

// a tela é criada aqui, o .h só avisa q ela existe
namespace display {
  Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);

  void iniciar() {
    pinMode(TFT_LED, OUTPUT);
    digitalWrite(TFT_LED, HIGH);

    // spi nos pinos da ordem
    SPI.begin(TFT_SCK, -1, TFT_SDA);
    tft.initR(INITR_BLACKTAB);

    // limpa a tela toda, 132x162
    tft.startWrite();
    tft.setAddrWindow(0, 0, 132, 162);
    tft.writeColor(ST77XX_BLACK, 132 * 162);
    tft.endWrite();

    tft.setRotation(3);
  }
}
