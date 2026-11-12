#pragma once

// Tela ST7735 
#define TFT_CS 32
#define TFT_RST 33
#define TFT_DC 25
#define TFT_SDA 26
#define TFT_SCK 27
#define TFT_LED 14

// Joystick pins
#define JOY_VERTICAL 34
#define JOY_HORIZONTAL 35
#define JOY_SW 19

// menos q 1000 ou mais q 3000 conta como empurrado
#define JOY_LIMITE_BAIXO 1000
#define JOY_LIMITE_ALTO 3000
#define JOY_INTERVALO_MS 100

// Buzzer passivo
#define BUZZER 18