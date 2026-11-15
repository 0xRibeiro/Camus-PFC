#include "wifi.h"

#include <WiFi.h>
#include <WiFiManager.h>

#include "../config.h"

namespace wifi {
  WiFiManager gerenciador;

  // começa desconectado, a 1ª conexão já conta como "conectou"
  bool conectado = false;
  unsigned long ultimaChecagem = 0;

  // "Camus-XXXX" + \0
  char nomeHotspot[11];

  // 8 é o mínimo do WPA2, + \0
  char senhaHotspot[9];

  // sem 0/o e 1/l/i pra n confundir lendo na telinha
  const char LETRAS_SENHA[] = "abcdefghjkmnpqrstuvwxyz23456789";

  // nome pelo fim do MAC, senha nova toda vez q abre o portal
  void gerarCredenciais() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    snprintf(nomeHotspot, sizeof(nomeHotspot), "Camus-%02X%02X", mac[4], mac[5]);

    // -1 pq o \0 do fim n conta como letra
    int quantidadeLetras = sizeof(LETRAS_SENHA) - 1;
    for (int i = 0; i < 8; i++) {
      senhaHotspot[i] = LETRAS_SENHA[esp_random() % quantidadeLetras];
    }
    senhaHotspot[8] = '\0';
  }

  // tenta a última rede salva na NVS
  void iniciar() {
    WiFi.mode(WIFI_STA);
    WiFi.begin();

    // portal roda junto com o loop e fecha sozinho se ninguém usar
    gerenciador.setConfigPortalBlocking(false);
    gerenciador.setConfigPortalTimeout(WIFI_PORTAL_TIMEOUT_S);
  }

  // liga o hotspot, quem chama é o botão da tela de wifi
  void abrirPortal() {
    gerarCredenciais();
    gerenciador.startConfigPortal(nomeHotspot, senhaHotspot);
  }

  // o q a tela de wifi precisa ler
  bool portalAberto() {
    return gerenciador.getConfigPortalActive();
  }

  const char* nomePortal() {
    return nomeHotspot;
  }

  const char* senhaPortal() {
    return senhaHotspot;
  }

  bool estaConectado() {
    return conectado;
  }

  String redeAtual() {
    return WiFi.SSID();
  }

  // só avisa qnd muda, igual o joystick
  Evento atualizar() {
    // o portal precisa rodar todo loop, fora do intervalo
    gerenciador.process();

    if (millis() - ultimaChecagem < WIFI_INTERVALO_MS) {
      return Evento::NENHUM;
    }
    ultimaChecagem = millis();

    bool agora = WiFi.status() == WL_CONNECTED;
    if (agora == conectado) {
      return Evento::NENHUM;
    }
    conectado = agora;

    if (conectado) {
      return Evento::CONECTOU;
    }
    return Evento::CAIU;
  }
}