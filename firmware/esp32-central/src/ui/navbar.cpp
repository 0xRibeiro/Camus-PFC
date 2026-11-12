#include "navbar.h"

#include "../hardware/display.h"
#include "icones.h"
#include "logo.h"

namespace navbar {
  // começa cortado até o wifi avisar q conectou
  bool wifiConectado = false;
  bool moduloNovo = false;
  bool moduloSaiu = false;
  bool aceso = true;
  unsigned long ultimaPiscada = 0;
  const unsigned long INTERVALO_PISCA = 500;

  // wifi bem no canto direito, 160 - 16 - 1 de folga
  void desenharWifi() {
    if (wifiConectado) {
      display::tft.drawRGBBitmap(143, 1, WIFI, 16, 16);
    } else if (aceso) {
      display::tft.drawRGBBitmap(143, 1, WIFI_CORTADO, 16, 16);
    } else {
      display::tft.fillRect(143, 1, 16, 16, ST77XX_BLACK);
    }
  }

  // lugar fixo: + colado no wifi, - do lado dele
  void desenharAvisos() {
    if (moduloNovo && aceso) {
      display::tft.drawRGBBitmap(133, 5, MAIS, 8, 8);
    } else {
      display::tft.fillRect(133, 5, 8, 8, ST77XX_BLACK);
    }

    if (moduloSaiu && aceso) {
      display::tft.drawRGBBitmap(123, 5, MENOS, 8, 8);
    } else {
      display::tft.fillRect(123, 5, 8, 8, ST77XX_BLACK);
    }
  }

  // 160 / 32 = 5 ondinhas certinhas, logo abaixo da navbar
  void desenharDivisoria() {
    for (int x = 0; x < 160; x += 32) {
      display::tft.drawRGBBitmap(x, 18, MAR, 32, 8);
    }
  }

  // barra de cima, 18px de altura
  void desenhar(const char* nome, int pagina, int total) {
    display::tft.drawRGBBitmap(1, 1, LOGO, 16, 16);

    // pagina atual
    display::tft.setTextColor(ST77XX_WHITE);
    display::tft.setTextSize(1);
    display::tft.setCursor(20, 5);
    display::tft.print(pagina);
    display::tft.print("/");
    display::tft.print(total);
    display::tft.print(" ");

    // texto tamanho 1 tem 8px, y=5 centraliza nos 18
    display::tft.print(nome);


    desenharWifi();
    desenharAvisos();
    desenharDivisoria();
  }

  void definirWifi(bool conectado) {
    wifiConectado = conectado;
    aceso = true;
    desenharWifi();
  }

  void avisarModuloNovo() {
    moduloNovo = true;
    aceso = true;
    desenharAvisos();
  }

  void avisarModuloSaiu() {
    moduloSaiu = true;
    aceso = true;
    desenharAvisos();
  }

  void limparAvisos() {
    moduloNovo = false;
    moduloSaiu = false;
    desenharAvisos();
  }

  // pisca sem delay, só redesenha os quadrados dos ícones
  void atualizar() {
    if (wifiConectado && !moduloNovo && !moduloSaiu) {
      return;
    }

    if (millis() - ultimaPiscada < INTERVALO_PISCA) {
      return;
    }

    ultimaPiscada = millis();
    aceso = !aceso;
    desenharWifi();
    desenharAvisos();
  }
}
