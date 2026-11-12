#include "mqtt.h"

#include <WiFi.h>
#include <mqtt_client.h>

#include "../config.h"

namespace mqtt {
  esp_mqtt_client_handle_t cliente;

  // quem escreve é a tarefa da esp-mqtt, o loop só lê
  bool conectado = false;

  // último valor q o atualizar() já avisou
  bool avisado = false;

  // MAC em minúsculo e sem ":", 12 + \0
  char id[13];

  void gerarId() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    snprintf(id, sizeof(id), "%02x%02x%02x%02x%02x%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  }

  // roda na tarefa da esp-mqtt, então só marca o estado e mais nada
  // o formato é obrigatório da lib, só o evento interessa
  void aoEvento(void*, esp_event_base_t, int32_t evento, void*) {
    if (evento == MQTT_EVENT_CONNECTED) {
      conectado = true;
    } else if (evento == MQTT_EVENT_DISCONNECTED) {
      conectado = false;
    }
  }

  // liga direto, se n tiver wifi ainda a lib tenta de novo sozinha
  void iniciar() {
    gerarId();

    esp_mqtt_client_config_t config = {};
    config.broker.address.uri = MQTT_URI;
    config.credentials.client_id = id;

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
