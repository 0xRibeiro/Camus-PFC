#include <Arduino.h>

// ---- teste inicial: led + serial ----
#define LED_PIN 2

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_PIN, !digitalRead(LED_PIN));
  Serial.println("esp32 vivo");
  delay(2000);
}