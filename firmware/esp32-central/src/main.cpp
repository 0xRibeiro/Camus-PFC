/*
  ESP32 + ILI9341 LCD Basic Example

  https://wokwi.com/projects/325324981270479442
*/

#include "SPI.h"
#include "Adafruit_GFX.h"
#include "Adafruit_ST7735.h"

#define TFT_DC 2
#define TFT_CS 15
#define TFT_RST 4
#define TFT_LED 32

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);

void setup() {
  pinMode(TFT_LED, OUTPUT);
  digitalWrite(TFT_LED, HIGH);

  tft.initR(INITR_BLACKTAB);
  tft.startWrite();
  tft.setAddrWindow(0, 0, 132, 162);
  tft.writeColor(ST77XX_BLACK, 132 * 162);
  tft.endWrite();


  tft.setRotation(3);

  tft.setCursor(10, 40);
  tft.setTextColor(ST77XX_RED);
  tft.setTextSize(2);
  tft.println("Hello ESP32");

  tft.setCursor(0, 3);
  tft.setTextColor(ST77XX_GREEN);
  tft.setTextSize(2);
  tft.println("I can do SPI :-)");
}

void loop() { delay(10); }