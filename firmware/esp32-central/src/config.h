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

// olha se o wifi caiu ou voltou
#define WIFI_INTERVALO_MS 1000

// portal fecha sozinho depois de 5 min parado
#define WIFI_PORTAL_TIMEOUT_S 300

// Buzzer passivo
#define BUZZER 18

// broker MQTT local
#define MQTT_URI "mqtt://192.168.0.13:1883"

// vai no status
#define FIRMWARE_VERSAO "0.1.0"