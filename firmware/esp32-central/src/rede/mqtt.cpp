#include "mqtt.h"

#include <WiFi.h>
#include <mqtt_client.h>

#include "../config.h"

namespace mqtt {
  esp_mqtt_client_handle_t cliente;

  bool conectado = false;

  // ultimo estado ja avisado
  bool avisado = false;

  // mac sem ":", 12 + \0
  char id[13];

  // camus/dispositivos/<mac>/status + \0
  char topicoStatus[39];

  void gerarId() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    snprintf(id, sizeof(id), "%02x%02x%02x%02x%02x%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  }

  // roda na task do mqtt, sem tela/buzzer aqui
  void aoEvento(void*, esp_event_base_t, int32_t evento, void*) {
    if (evento == MQTT_EVENT_CONNECTED) {
      conectado = true;

      // retido, sobrescreve o offline
      char mensagem[48];
      snprintf(mensagem, sizeof(mensagem), "{\"estado\":\"online\",\"firmware\":\"%s\"}", FIRMWARE_VERSAO);
      esp_mqtt_client_publish(cliente, topicoStatus, mensagem, 0, 0, 1);
    } else if (evento == MQTT_EVENT_DISCONNECTED) {
      conectado = false;
    }
  }

  // sem wifi a lib tenta de novo sozinha
  void iniciar() {
    gerarId();
    snprintf(topicoStatus, sizeof(topicoStatus), "camus/dispositivos/%s/status", id);

    esp_mqtt_client_config_t config = {};
    config.broker.address.uri = MQTT_URI;
    config.credentials.client_id = id;

    // padrao 120s, offline demorava demais
    config.session.keepalive = 30;

    // broker publica se o esp cair
    config.session.last_will.topic = topicoStatus;
    config.session.last_will.msg = "{\"estado\":\"offline\"}";
    config.session.last_will.retain = 1;

    cliente = esp_mqtt_client_init(&config);
    esp_mqtt_client_register_event(cliente, MQTT_EVENT_ANY, aoEvento, nullptr);
    esp_mqtt_client_start(cliente);
  }

  bool estaConectado() {
    return conectado;
  }

  Evento atualizar() {
    if (conectado == avisado) {
      return Evento::NENHUM;
    }
    avisado = conectado;

    if (avisado) {
      return Evento::CONECTOU;
    }
    return Evento::CAIU;
  }
}
