#include "mqtt.h"

#include <ArduinoJson.h>
#include <WiFi.h>
#include <esp_crt_bundle.h>
#include <mqtt_client.h>

#include "../config.h"
#include "credencial.h"

namespace mqtt {
  esp_mqtt_client_handle_t cliente;

  bool conectado = false;

  // ultimo estado ja avisado
  bool avisado = false;

  // mac sem ":", 12 + \0
  char id[13];

  // camus/dispositivos/<mac>/status + \0
  char topicoStatus[39];

  // camus/dispositivos/<mac>/vinculo/pedido + \0
  char topicoPedido[47];

  // camus/dispositivos/<mac>/vinculo/resposta + \0
  char topicoResposta[49];

  // camus/dispositivos/<mac>/comandos + \0
  char topicoComandos[41];

  // ultima resposta do vinculo, a tela le e limpa a marca
  bool temCodigo = false;
  char codigoRecebido[7];
  int validadeRecebida = 0;
  bool temDesvinculo = false;
  int removidosRecebidos = 0;

  // ultimo comando, o loop le e manda pro modulo (i2c n roda nessa task)
  bool temComando = false;
  uint32_t serialRecebido = 0;
  bool ligarRecebido = false;

  void gerarId() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    snprintf(id, sizeof(id), "%02x%02x%02x%02x%02x%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  }

  // roda na task do mqtt, sem tela/buzzer aqui
  void aoEvento(void*, esp_event_base_t, int32_t evento, void* dados) {
    if (evento == MQTT_EVENT_CONNECTED) {
      conectado = true;

      // retido, sobrescreve o offline
      char mensagem[48];
      snprintf(mensagem, sizeof(mensagem), "{\"estado\":\"online\",\"firmware\":\"%s\"}", FIRMWARE_VERSAO);
      esp_mqtt_client_publish(cliente, topicoStatus, mensagem, 0, 0, 1);
      esp_mqtt_client_subscribe(cliente, topicoResposta, 0);
      esp_mqtt_client_subscribe(cliente, topicoComandos, 0);
    } else if (evento == MQTT_EVENT_DISCONNECTED) {
      conectado = false;
    } else if (evento == MQTT_EVENT_DATA) {
      // assina comandos e vinculo/resposta, o topico diz qual chegou
      esp_mqtt_event_handle_t mensagem = (esp_mqtt_event_handle_t) dados;
      JsonDocument json;
      deserializeJson(json, mensagem->data, mensagem->data_len);

      // topico do evento n termina em \0
      bool ehComando = mensagem->topic_len == (int) strlen(topicoComandos) &&
                       strncmp(mensagem->topic, topicoComandos, mensagem->topic_len) == 0;

      if (ehComando) {
        serialRecebido = strtoul(json["serial"] | "", nullptr, 16);
        ligarRecebido = json["acao"] == "ativar";
        temComando = true;
      } else if (json["acao"] == "gerar_codigo") {
        strlcpy(codigoRecebido, json["codigo"] | "", sizeof(codigoRecebido));
        validadeRecebida = json["expira_em"];
        temCodigo = true;
      } else if (json["acao"] == "desvincular_todos") {
        removidosRecebidos = json["removidos"];
        temDesvinculo = true;
      }
    }
  }

  // sem wifi a lib tenta de novo sozinha
  void iniciar() {
    gerarId();
    snprintf(topicoStatus, sizeof(topicoStatus), "camus/dispositivos/%s/status", id);
    snprintf(topicoPedido, sizeof(topicoPedido), "camus/dispositivos/%s/vinculo/pedido", id);
    snprintf(topicoResposta, sizeof(topicoResposta), "camus/dispositivos/%s/vinculo/resposta", id);
    snprintf(topicoComandos, sizeof(topicoComandos), "camus/dispositivos/%s/comandos", id);

    // sem cadastro o broker recusa, nem tenta
    if (!credencial::temSenha()) {
      return;
    }

    esp_mqtt_client_config_t config = {};
    config.broker.address.uri = MQTT_URI;

    // so vale no mqtts, confere o certificado
    config.broker.verification.crt_bundle_attach = esp_crt_bundle_attach;
    config.credentials.client_id = id;
    config.credentials.username = id;
    config.credentials.authentication.password = credencial::senha();

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

  const char* identificador() {
    return id;
  }

  void publicar(const char* sufixo, const char* mensagem, bool retido) {
    if (!conectado) {
      return;
    }

    char topico[64];
    snprintf(topico, sizeof(topico), "camus/dispositivos/%s/%s", id, sufixo);
    esp_mqtt_client_publish(cliente, topico, mensagem, 0, 0, retido);
  }

  void pedirCodigo() {
    esp_mqtt_client_publish(cliente, topicoPedido, "{\"acao\":\"gerar_codigo\"}", 0, 0, 0);
  }

  void pedirDesvincularTodos() {
    esp_mqtt_client_publish(cliente, topicoPedido, "{\"acao\":\"desvincular_todos\"}", 0, 0, 0);
  }

  // true so uma vez por resposta
  bool chegouCodigo() {
    if (!temCodigo) {
      return false;
    }
    temCodigo = false;
    return true;
  }

  const char* codigo() {
    return codigoRecebido;
  }

  int validade() {
    return validadeRecebida;
  }

  bool chegouDesvinculo() {
    if (!temDesvinculo) {
      return false;
    }
    temDesvinculo = false;
    return true;
  }

  int removidos() {
    return removidosRecebidos;
  }

  bool chegouComando() {
    if (!temComando) {
      return false;
    }
    temComando = false;
    return true;
  }

  uint32_t serialComando() {
    return serialRecebido;
  }

  bool ligarComando() {
    return ligarRecebido;
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
