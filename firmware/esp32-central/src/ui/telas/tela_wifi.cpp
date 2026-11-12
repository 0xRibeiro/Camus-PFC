#include "tela_wifi.h"

#include "../../config.h"
#include "../../hardware/display.h"
#include "../../rede/wifi.h"
#include "../navbar.h"

void TelaWifi::desenhar() {
  portalDesenhado = wifi::portalAberto();
  conectadoDesenhado = wifi::estaConectado();

  // limpa só embaixo da navbar
  display::tft.fillRect(0, navbar::ALTURA, 160, 128 - navbar::ALTURA, ST77XX_BLACK);
  display::tft.setTextColor(ST77XX_WHITE);
  int topo = navbar::ALTURA + 4;

  // portal aberto: nome e senha grandes pra ler de longe
  if (portalDesenhado) {
    display::tft.setTextSize(1);
    display::tft.setCursor(4, topo);
    display::tft.print("Conecte na rede:");

    display::tft.setTextSize(2);
    display::tft.setCursor(4, topo + 10);
    display::tft.print(wifi::nomePortal());

    display::tft.setTextSize(1);
    display::tft.setCursor(4, topo + 32);
    display::tft.print("Senha:");

    display::tft.setTextSize(2);
    display::tft.setCursor(4, topo + 42);
    display::tft.print(wifi::senhaPortal());

    display::tft.setTextSize(1);
    display::tft.setCursor(4, topo + 66);
    display::tft.print("Fecha em ");
    display::tft.print(WIFI_PORTAL_TIMEOUT_S / 60);
    display::tft.print(" min");
    return;
  }

  display::tft.setTextSize(1);
  display::tft.setCursor(4, topo);
  if (conectadoDesenhado) {
    display::tft.print("Conectado em:");
    display::tft.setCursor(4, topo + 12);
    display::tft.print(wifi::redeAtual());
  } else {
    display::tft.print("Sem Wi-Fi");
  }

  display::tft.setCursor(4, topo + 36);
  display::tft.print("Clique pra configurar");
}

void TelaWifi::aoEvento(joystick::Evento evento) {
  if (evento == joystick::Evento::CLIQUE && !wifi::portalAberto()) {
    wifi::abrirPortal();
  }
}

// redesenha só qnd o portal abre/fecha ou a conexão muda
void TelaWifi::atualizar() {
  bool mudouPortal = wifi::portalAberto() != portalDesenhado;
  bool mudouConexao = wifi::estaConectado() != conectadoDesenhado;

  if (mudouPortal || mudouConexao) {
    desenhar();
  }
}

const char* TelaWifi::nome() {
  return "Wi-Fi";
}
