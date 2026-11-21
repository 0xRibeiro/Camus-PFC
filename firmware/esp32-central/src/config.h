#pragma once

// ---- tela ----

// tela colorida st7735 de 160x128, conversa por spi.
// spi e outro tipo de fio de dados, mais rapido q o i2c
#define TFT_CS 32
#define TFT_RST 33
#define TFT_DC 25
#define TFT_SDA 26
#define TFT_SCK 27

// luz de fundo da tela
#define TFT_LED 14

// ---- joystick ----

// os 2 eixos sao analogicos, vao de 0 a 4095 com o meio perto de 2000
#define JOY_VERTICAL 34
#define JOY_HORIZONTAL 35

// botao de apertar o joystick
#define JOY_SW 19

// menos q 1000 ou mais q 3000 conta como empurrado
#define JOY_LIMITE_BAIXO 1000
#define JOY_LIMITE_ALTO 3000
#define JOY_INTERVALO_MS 100

// ---- wifi ----

// de quanto em quanto tempo olha se o wifi caiu ou voltou
#define WIFI_INTERVALO_MS 1000

// portal de configurar o wifi fecha sozinho depois de 5 min parado
#define WIFI_PORTAL_TIMEOUT_S 300

// ---- buzzer ----

// buzzer passivo, toca a frequencia q mandar
#define BUZZER 18

// ---- i2c dos modulos ----

// direto nos nanos, com os puxadores no 3,3v da esp
#define I2C_SDA 21
#define I2C_SCL 22

// ---- mqtt ----

// MQTT_URI vem do ambiente escolhido no platformio.ini, dev ou producao
#ifndef MQTT_URI
#error "MQTT_URI nao definido, use -e dev ou -e producao"
#endif

// sem resposta do backend nesse tempo, desiste do pedido de vinculo
#define VINCULO_ESPERA_MS 10000

// vai no status pro backend
#define FIRMWARE_VERSAO "0.1.0"
