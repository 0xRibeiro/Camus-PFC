#include "barramento.h"

#include <ArduinoJson.h>
#include <Wire.h>
#include <protocolo.h>

#include "../config.h"
#include "../rede/mqtt.h"

namespace barramento {
  const int MAX_MODULOS = 8;
  const unsigned long INTERVALO_VARREDURA = 2000;
  const unsigned long INTERVALO_LEITURA = 1000;

  struct Catalogo {
    uint8_t tipo;
    const char* nome;
    uint8_t quantidade;
    InfoLeitura leituras[MAX_VALORES];
    bool atuador;
  };

  // atuador: tem rele, responde COMANDO e ESTADO
  const Catalogo CATALOGO[] = {
    { (uint8_t) TipoModulo::DISTANCIA, "Distancia", 1, { { "distancia", "Distancia", "cm", 10, 1 } }, false },
    { (uint8_t) TipoModulo::TEMPERATURA, "Temperatura", 1, { { "temperatura", "Temperatura", "C", 100, 1 } }, true },
    { (uint8_t) TipoModulo::QUALIDADE_AGUA, "Qualidade agua", 2, {
      { "tds", "TDS", "ppm", 1, 0 },
      { "turbidez", "Turbidez", "NTU", 10, 1 },
    }, false },
  };

  const InfoLeitura LEITURA_VAZIA = { "", "", "", 1, 0 };

  Modulo modulos[MAX_MODULOS];
  int total = 0;
  bool repetido = false;
  int versaoAtual = 0;
  unsigned long ultimaVarredura = 0;
  unsigned long ultimaLeitura = 0;

  const Catalogo* buscarCatalogo(uint8_t tipo) {
    for (const Catalogo& item : CATALOGO) {
      if (item.tipo == tipo) {
        return &item;
      }
    }
    return nullptr;
  }

  int buscarEm(const Modulo* lista, int quantidade, uint32_t serial) {
    for (int i = 0; i < quantidade; i++) {
      if (lista[i].serial == serial) {
        return i;
      }
    }
    return -1;
  }

  // 8 hex + \0
  void textoSerial(uint32_t serial, char* destino) {
    snprintf(destino, 9, "%08lx", (unsigned long) serial);
  }

  bool responde(uint8_t endereco) {
    Wire.beginTransmission(endereco);
    return Wire.endTransmission() == 0;
  }

  bool ler(uint8_t endereco, uint8_t registrador, uint8_t* resposta, uint8_t tamanho) {
    Wire.beginTransmission(endereco);
    Wire.write(registrador);
    if (Wire.endTransmission() != 0) {
      return false;
    }

    if (Wire.requestFrom(endereco, tamanho) != tamanho) {
      return false;
    }
    for (uint8_t i = 0; i < tamanho; i++) {
      resposta[i] = Wire.read();
    }

    return crc8(resposta, tamanho - 1) == resposta[tamanho - 1];
  }

  Evento varrer() {
    Modulo achados[MAX_MODULOS];
    int quantidadeAchados = 0;
    bool colidiu = false;

    for (uint8_t endereco = ENDERECO_PRIMEIRO; endereco <= ENDERECO_ULTIMO; endereco++) {
      if (quantidadeAchados == MAX_MODULOS || !responde(endereco)) {
        continue;
      }

      // crc errado 2x = dois modulos no mesmo endereco
      uint8_t id[TAM_IDENTIFICACAO];
      if (!ler(endereco, REG_IDENTIFICACAO, id, TAM_IDENTIFICACAO) &&
          !ler(endereco, REG_IDENTIFICACAO, id, TAM_IDENTIFICACAO)) {
        colidiu = true;
        continue;
      }

      Modulo& novo = achados[quantidadeAchados];
      novo.endereco = endereco;
      novo.tipo = id[1];
      novo.serial = ((uint32_t) id[2] << 24) | ((uint32_t) id[3] << 16) | ((uint32_t) id[4] << 8) | id[5];
      novo.temValor = false;
      novo.ligado = false;
      for (int v = 0; v < MAX_VALORES; v++) {
        novo.valores[v] = 0;
      }

      // mantem o ultimo valor de quem ja tava
      int antigo = buscarEm(modulos, total, novo.serial);
      if (antigo >= 0) {
        novo.temValor = modulos[antigo].temValor;
        novo.ligado = modulos[antigo].ligado;
        for (int v = 0; v < MAX_VALORES; v++) {
          novo.valores[v] = modulos[antigo].valores[v];
        }
      }
      quantidadeAchados++;
    }

    bool entrou = false;
    for (int i = 0; i < quantidadeAchados; i++) {
      if (buscarEm(modulos, total, achados[i].serial) < 0) {
        entrou = true;
      }
    }

    bool saiu = false;
    for (int i = 0; i < total; i++) {
      if (buscarEm(achados, quantidadeAchados, modulos[i].serial) < 0) {
        saiu = true;
      }
    }

    for (int i = 0; i < quantidadeAchados; i++) {
      modulos[i] = achados[i];
    }
    total = quantidadeAchados;

    bool ficouRepetido = colidiu && !repetido;
    if (colidiu != repetido) {
      repetido = colidiu;
      versaoAtual++;
    }

    if (entrou || saiu) {
      versaoAtual++;
      publicarModulos();
    }

    // um evento por varredura, repetido primeiro
    if (ficouRepetido) {
      return Evento::REPETIDO;
    }
    if (saiu) {
      return Evento::SAIU;
    }
    if (entrou) {
      return Evento::ENTROU;
    }
    return Evento::NENHUM;
  }

  void publicarLeitura(const Modulo& modulo, const Catalogo* catalogo) {
    char serial[9];
    textoSerial(modulo.serial, serial);

    JsonDocument json;
    json["serial"] = serial;
    json["tipo"] = modulo.tipo;

    JsonArray leituras = json["leituras"].to<JsonArray>();
    for (int v = 0; v < catalogo->quantidade; v++) {
      JsonObject leitura = leituras.add<JsonObject>();
      leitura["nome"] = catalogo->leituras[v].nome;
      leitura["valor"] = modulo.valores[v];
      leitura["unidade"] = catalogo->leituras[v].unidade;
    }

    char mensagem[320];
    serializeJson(json, mensagem);
    mqtt::publicar("leituras", mensagem, false);
  }

  // so publica qnd o modulo marca leitura nova
  void lerModulos() {
    for (int i = 0; i < total; i++) {
      uint8_t resposta[TAM_LEITURA];
      if (!ler(modulos[i].endereco, REG_LEITURA, resposta, TAM_LEITURA) || !resposta[0]) {
        continue;
      }

      const Catalogo* catalogo = buscarCatalogo(modulos[i].tipo);
      if (catalogo == nullptr) {
        continue;
      }

      // modulo diz quantos mandou, mas so usa os q o catalogo conhece
      uint8_t quantidade = resposta[1];
      if (quantidade < catalogo->quantidade) {
        continue;
      }

      for (int v = 0; v < catalogo->quantidade; v++) {
        int16_t bruto = (resposta[2 + v * 2] << 8) | resposta[3 + v * 2];
        modulos[i].valores[v] = bruto / catalogo->leituras[v].escala;
      }
      modulos[i].temValor = true;
      versaoAtual++;
      publicarLeitura(modulos[i], catalogo);
    }
  }

  // estado do rele vai no modulos (retido), publica so qnd muda
  void lerEstados() {
    bool mudou = false;

    for (int i = 0; i < total; i++) {
      const Catalogo* catalogo = buscarCatalogo(modulos[i].tipo);
      if (catalogo == nullptr || !catalogo->atuador) {
        continue;
      }

      uint8_t resposta[TAM_ESTADO];
      if (!ler(modulos[i].endereco, REG_ESTADO, resposta, TAM_ESTADO)) {
        continue;
      }

      bool ligado = resposta[0] == 1;
      if (ligado != modulos[i].ligado) {
        modulos[i].ligado = ligado;
        mudou = true;
      }
    }

    if (mudou) {
      versaoAtual++;
      publicarModulos();
    }
  }

  void publicarModulos() {
    JsonDocument json;
    JsonArray lista = json["modulos"].to<JsonArray>();

    for (int i = 0; i < total; i++) {
      char serial[9];
      textoSerial(modulos[i].serial, serial);

      JsonObject item = lista.add<JsonObject>();
      item["serial"] = serial;
      item["tipo"] = modulos[i].tipo;
      item["endereco"] = modulos[i].endereco;

      const Catalogo* catalogo = buscarCatalogo(modulos[i].tipo);
      if (catalogo != nullptr && catalogo->atuador) {
        item["ligado"] = modulos[i].ligado;
      }
    }

    char mensagem[512];
    serializeJson(json, mensagem);

    // retido, backend pega a lista atual ao conectar
    mqtt::publicar("modulos", mensagem, true);
  }

  // [0x03, acao], o lerEstados confirma no proximo segundo
  void comandar(uint32_t serial, bool ligar) {
    int indice = buscarEm(modulos, total, serial);
    if (indice < 0) {
      return;
    }

    Wire.beginTransmission(modulos[indice].endereco);
    Wire.write(REG_COMANDO);
    Wire.write(ligar ? 1 : 0);
    Wire.endTransmission();
  }

  void iniciar() {
    Wire.begin(I2C_SDA, I2C_SCL);
  }

  // varredura bloqueia uns ms, por isso a cada 2s
  Evento atualizar() {
    if (millis() - ultimaLeitura >= INTERVALO_LEITURA) {
      ultimaLeitura = millis();
      lerModulos();
      lerEstados();
    }

    if (millis() - ultimaVarredura < INTERVALO_VARREDURA) {
      return Evento::NENHUM;
    }
    ultimaVarredura = millis();
    return varrer();
  }

  int quantidade() {
    return total;
  }

  const Modulo& modulo(int indice) {
    return modulos[indice];
  }

  bool temRepetido() {
    return repetido;
  }

  int versao() {
    return versaoAtual;
  }

  const char* nomeTipo(uint8_t tipo) {
    const Catalogo* catalogo = buscarCatalogo(tipo);
    if (catalogo == nullptr) {
      return "Desconhecido";
    }
    return catalogo->nome;
  }

  int quantidadeLeituras(uint8_t tipo) {
    const Catalogo* catalogo = buscarCatalogo(tipo);
    if (catalogo == nullptr) {
      return 0;
    }
    return catalogo->quantidade;
  }

  const InfoLeitura& leituraTipo(uint8_t tipo, int indice) {
    const Catalogo* catalogo = buscarCatalogo(tipo);
    if (catalogo == nullptr || indice >= catalogo->quantidade) {
      return LEITURA_VAZIA;
    }
    return catalogo->leituras[indice];
  }

  bool atuadorTipo(uint8_t tipo) {
    const Catalogo* catalogo = buscarCatalogo(tipo);
    if (catalogo == nullptr) {
      return false;
    }
    return catalogo->atuador;
  }
}
