#include "mqtt.h"

#include <ArduinoJson.h>
#include <WiFi.h>
#include <esp_crt_bundle.h>
#include <mqtt_client.h>

#include "../config.h"
#include "credencial.h"

// o cliente mqtt roda numa task separada, ao msm tempo q o loop.
// tela, buzzer e i2c n podem ser usados de 2 lugares ao msm tempo,
// entao o q chega aqui so vira marcacao e o loop le depois
namespace mqtt {
  esp_mqtt_client_handle_t cliente;

  bool conectado = false;

  // ultimo estado ja avisado pro main
  bool avisado = false;

  // mac sem ":" tem 12 letras, +1 do \0 q fecha o texto
  char id[13];

  // camus/dispositivos/<mac>/... cabe folgado em 64
  char topicoStatus[64];
  char topicoPedido[64];
  char topicoResposta[64];
  char topicoComandos[64];

  // ultima resposta do vinculo, a tela le e apaga a marca
  bool temCodigo = false;
  char codigoRecebido[7];
  int validadeRecebida = 0;
  bool temContagem = false;
  int vinculadosRecebidos = 0;
  bool temDesvinculo = false;

  // ultimo comando, o loop le e manda pro modulo
  bool temComando = false;
  uint32_t serialRecebido = 0;
  bool ligarRecebido = false;

  // ---- topicos ----

  void gerarId() {
    uint8_t mac[6];
    WiFi.macAddress(mac);
    snprintf(id, sizeof(id), "%02x%02x%02x%02x%02x%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  }

  void montarTopico(char destino[64], const char* final) {
    snprintf(destino, 64, "camus/dispositivos/%s/%s", id, final);
  }

  // o topico q vem no evento n tem o \0 no fim, entao compara o tamanho e as letras
  bool ehTopico(esp_mqtt_event_handle_t mensagem, const char* topico) {
    bool mesmoTamanho = mensagem->topic_len == (int) strlen(topico);
    return mesmoTamanho && strncmp(mensagem->topic, topico, mensagem->topic_len) == 0;
  }

  // ---- eventos ----

  // status retido sobrescreve o offline q o broker publicou quando caiu
  void aoConectar() {
    conectado = true;

    char mensagem[48];
    snprintf(mensagem, sizeof(mensagem), "{\"estado\":\"online\",\"firmware\":\"%s\"}", FIRMWARE_VERSAO);
    esp_mqtt_client_publish(cliente, topicoStatus, mensagem, 0, 0, 1);

    esp_mqtt_client_subscribe(cliente, topicoResposta, 0);
    esp_mqtt_client_subscribe(cliente, topicoComandos, 0);
  }

  void guardarComando(JsonDocument& json) {
    serialRecebido = strtoul(json["serial"] | "", nullptr, 16);
    ligarRecebido = json["acao"] == "ativar";
    temComando = true;
  }

  // resposta do vinculo, a acao diz qual pedido foi respondido
  void guardarResposta(JsonDocument& json) {
    if (json["acao"] == "gerar_codigo") {
      strlcpy(codigoRecebido, json["codigo"] | "", sizeof(codigoRecebido));
      validadeRecebida = json["expira_em"];
      temCodigo = true;
    } else if (json["acao"] == "contar_vinculados") {
      vinculadosRecebidos = json["vinculados"];
      temContagem = true;
    } else if (json["acao"] == "desvincular_todos") {
      temDesvinculo = true;
    }
  }

  void aoReceberMensagem(esp_mqtt_event_handle_t mensagem) {
    JsonDocument json;
    deserializeJson(json, mensagem->data, mensagem->data_len);

    if (ehTopico(mensagem, topicoComandos)) {
      guardarComando(json);
    } else {
      guardarResposta(json);
    }
  }

  // formato q a lib exige. void* aceita qualquer tipo de dado,
  // no evento de mensagem converte pro tipo da mensagem
  void aoEvento(void*, esp_event_base_t, int32_t evento, void* dados) {
    if (evento == MQTT_EVENT_CONNECTED) {
      aoConectar();
    } else if (evento == MQTT_EVENT_DISCONNECTED) {
      conectado = false;
    } else if (evento == MQTT_EVENT_DATA) {
      aoReceberMensagem((esp_mqtt_event_handle_t) dados);
    }
  }

  // ---- usado pelo resto ----

  // sem wifi a lib fica tentando sozinha
  void iniciar() {
    gerarId();
    montarTopico(topicoStatus, "status");
    montarTopico(topicoPedido, "vinculo/pedido");
    montarTopico(topicoResposta, "vinculo/resposta");
    montarTopico(topicoComandos, "comandos");

    // sem senha gravada o broker recusa, nem tenta
    if (!credencial::temSenha()) {
      return;
    }

    esp_mqtt_client_config_t config = {};
    config.broker.address.uri = MQTT_URI;

    // so vale no mqtts de producao, confere o certificado do servidor
    config.broker.verification.crt_bundle_attach = esp_crt_bundle_attach;
    config.credentials.client_id = id;
    config.credentials.username = id;
    config.credentials.authentication.password = credencial::senha();

    // de quanto em quanto tempo da sinal de vida, o padrao de 120s demorava demais pra ficar offline
    config.session.keepalive = 30;

    // o broker publica isso sozinho se a esp sumir
    config.session.last_will.topic = topicoStatus;
    config.session.last_will.msg = "{\"estado\":\"offline\"}";
    config.session.last_will.retain = 1;

    cliente = esp_mqtt_client_init(&config);
    esp_mqtt_client_register_event(cliente, MQTT_EVENT_ANY, aoEvento, nullptr);
    esp_mqtt_client_start(cliente);
  }

  // so avisa quando muda
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

  bool estaConectado() {
    return conectado;
  }

  const char* identificador() {
    return id;
  }

  // retido = o broker guarda a ultima e entrega pra quem se inscrever depois
  void publicar(const char* final, const char* mensagem, bool retido) {
    if (!conectado) {
      return;
    }

    char topico[64];
    montarTopico(topico, final);
    esp_mqtt_client_publish(cliente, topico, mensagem, 0, 0, retido);
  }

  void pedirCodigo() {
    esp_mqtt_client_publish(cliente, topicoPedido, "{\"acao\":\"gerar_codigo\"}", 0, 0, 0);
  }

  void pedirContagem() {
    esp_mqtt_client_publish(cliente, topicoPedido, "{\"acao\":\"contar_vinculados\"}", 0, 0, 0);
  }

  void pedirDesvincularTodos() {
    esp_mqtt_client_publish(cliente, topicoPedido, "{\"acao\":\"desvincular_todos\"}", 0, 0, 0);
  }

  // os chegouX devolvem true uma vez so por mensagem e ja apagam a marca
  bool chegouCodigo() {
    bool chegou = temCodigo;
    temCodigo = false;
    return chegou;
  }

  bool chegouContagem() {
    bool chegou = temContagem;
    temContagem = false;
    return chegou;
  }

  bool chegouDesvinculo() {
    bool chegou = temDesvinculo;
    temDesvinculo = false;
    return chegou;
  }

  bool chegouComando() {
    bool chegou = temComando;
    temComando = false;
    return chegou;
  }

  const char* codigo() {
    return codigoRecebido;
  }

  int validade() {
    return validadeRecebida;
  }

  int vinculados() {
    return vinculadosRecebidos;
  }

  uint32_t serialComando() {
    return serialRecebido;
  }

  bool ligarComando() {
    return ligarRecebido;
  }
}
