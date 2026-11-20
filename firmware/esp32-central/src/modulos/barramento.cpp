#include "barramento.h"

#include <ArduinoJson.h>
#include <Wire.h>

#include "../config.h"
#include "../rede/mqtt.h"

namespace barramento {
  const int MAX_MODULOS = 8;

  // procurar todos os enderecos trava a esp uns ms, por isso so a cada 2s
  const unsigned long INTERVALO_VARREDURA = 2000;
  const unsigned long INTERVALO_LEITURA = 1000;

  // ---- catalogo: o q a esp sabe de cada tipo de modulo ----

  struct Catalogo {
    uint8_t tipo;
    const char* nome;
    uint8_t quantidade;
    InfoLeitura leituras[MAX_VALORES];

    // atuador tem rele: aceita COMANDO e responde ESTADO
    bool atuador;
  };

  // leituras na msm ordem q o nano manda
  const Catalogo CATALOGO[] = {
    { (uint8_t) TipoModulo::DISTANCIA, "Distancia", 1, {
      { "distancia", "Distancia", "cm", 10, 1 },
    }, false },
    { (uint8_t) TipoModulo::TEMPERATURA, "Temperatura", 1, {
      { "temperatura", "Temperatura", "C", 100, 1 },
    }, true },
    { (uint8_t) TipoModulo::QUALIDADE_AGUA, "Qualidade agua", 2, {
      { "tds", "TDS", "ppm", 1, 0 },
      { "turbidez", "Turbidez", "NTU", 10, 1 },
    }, false },
  };

  // sizeof do array todo / sizeof de um item = quantos itens tem
  const int TAMANHO_CATALOGO = sizeof(CATALOGO) / sizeof(CATALOGO[0]);

  // ---- estado ----

  Modulo modulos[MAX_MODULOS];
  int total = 0;
  bool repetido = false;
  int versaoAtual = 0;
  unsigned long ultimaVarredura = 0;
  unsigned long ultimaLeitura = 0;

  // ---- buscas ----

  int posicaoNoCatalogo(uint8_t tipo) {
    for (int i = 0; i < TAMANHO_CATALOGO; i++) {
      if (CATALOGO[i].tipo == tipo) {
        return i;
      }
    }
    return -1;
  }

  // posicao do serial na lista, -1 se n ta
  int posicaoNaLista(const Modulo lista[], int quantidadeLista, uint32_t serial) {
    for (int i = 0; i < quantidadeLista; i++) {
      if (lista[i].serial == serial) {
        return i;
      }
    }
    return -1;
  }

  // ---- i2c ----

  // so bate na porta: endTransmission devolve 0 se alguem respondeu no endereco
  bool responde(uint8_t endereco) {
    Wire.beginTransmission(endereco);
    return Wire.endTransmission() == 0;
  }

  // escreve o registrador, pede a resposta e confere o crc
  bool ler(uint8_t endereco, uint8_t registrador, uint8_t resposta[], uint8_t tamanho) {
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

    return mensagemIntegra(resposta, tamanho);
  }

  // ---- json pro mqtt ----

  // serial em texto: 8 letras hex + o \0 q marca o fim do texto em c
  void textoSerial(uint32_t serial, char destino[9]) {
    snprintf(destino, 9, "%08lx", (unsigned long) serial);
  }

  void publicarLeitura(Modulo modulo) {
    const Catalogo& catalogo = CATALOGO[modulo.catalogo];
    char serial[9];
    textoSerial(modulo.serial, serial);

    JsonDocument json;
    json["serial"] = serial;
    json["tipo"] = modulo.tipo;

    JsonArray leituras = json["leituras"].to<JsonArray>();
    for (int i = 0; i < catalogo.quantidade; i++) {
      JsonObject item = leituras.add<JsonObject>();
      item["nome"] = catalogo.leituras[i].nome;
      item["valor"] = modulo.valores[i];
      item["unidade"] = catalogo.leituras[i].unidade;
    }

    char mensagem[320];
    serializeJson(json, mensagem);
    mqtt::publicar("leituras", mensagem, false);
  }

  // lista inteira, retida no broker: o backend recebe a atual assim q conecta
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

      if (ehAtuador(modulos[i])) {
        item["ligado"] = modulos[i].ligado;
      }
    }

    char mensagem[512];
    serializeJson(json, mensagem);
    mqtt::publicar("modulos", mensagem, true);
  }

  // ---- varredura: quem ta ligado no fio ----
  //
  // Modulo& = a funcao mexe direto no modulo q recebeu, sem copiar.
  // e assim q ela preenche o modulo de quem chamou

  // pede a identificacao. crc errado 2x seguidas = 2 modulos no msm endereco falando junto
  bool identificar(uint8_t endereco, Modulo& novo) {
    uint8_t id[TAM_IDENTIFICACAO];
    bool leu = ler(endereco, REG_IDENTIFICACAO, id, TAM_IDENTIFICACAO);
    if (!leu) {
      leu = ler(endereco, REG_IDENTIFICACAO, id, TAM_IDENTIFICACAO);
    }
    if (!leu) {
      return false;
    }

    novo.endereco = endereco;
    novo.tipo = id[1];
    novo.serial = lerSerial(id, 2);
    novo.catalogo = posicaoNoCatalogo(novo.tipo);
    novo.temValor = false;
    novo.ligado = false;
    for (int i = 0; i < MAX_VALORES; i++) {
      novo.valores[i] = 0;
    }
    return true;
  }

  // modulo q ja tava ligado continua com o ultimo valor, sem piscar "..." na tela
  void aproveitarValoresAntigos(Modulo& novo) {
    int antigo = posicaoNaLista(modulos, total, novo.serial);
    if (antigo < 0) {
      return;
    }

    novo.temValor = modulos[antigo].temValor;
    novo.ligado = modulos[antigo].ligado;
    for (int i = 0; i < MAX_VALORES; i++) {
      novo.valores[i] = modulos[antigo].valores[i];
    }
  }

  // tem alguem nos achados q n tava na lista?
  bool algumEntrou(const Modulo achados[], int quantidadeAchados) {
    for (int i = 0; i < quantidadeAchados; i++) {
      if (posicaoNaLista(modulos, total, achados[i].serial) < 0) {
        return true;
      }
    }
    return false;
  }

  // tem alguem na lista q sumiu dos achados?
  bool algumSaiu(const Modulo achados[], int quantidadeAchados) {
    for (int i = 0; i < total; i++) {
      if (posicaoNaLista(achados, quantidadeAchados, modulos[i].serial) < 0) {
        return true;
      }
    }
    return false;
  }

  void trocarLista(const Modulo achados[], int quantidadeAchados) {
    for (int i = 0; i < quantidadeAchados; i++) {
      modulos[i] = achados[i];
    }
    total = quantidadeAchados;
  }

  // passa por todos os enderecos e monta a lista de novo
  Evento varrer() {
    Modulo achados[MAX_MODULOS];
    int quantidadeAchados = 0;
    bool colidiu = false;

    for (uint8_t endereco = ENDERECO_PRIMEIRO; endereco <= ENDERECO_ULTIMO; endereco++) {
      if (quantidadeAchados == MAX_MODULOS || !responde(endereco)) {
        continue;
      }

      if (!identificar(endereco, achados[quantidadeAchados])) {
        colidiu = true;
        continue;
      }

      aproveitarValoresAntigos(achados[quantidadeAchados]);
      quantidadeAchados++;
    }

    bool entrou = algumEntrou(achados, quantidadeAchados);
    bool saiu = algumSaiu(achados, quantidadeAchados);
    trocarLista(achados, quantidadeAchados);

    // so apita no momento q aparece o repetido, n a cada 2s
    bool acabouDeRepetir = colidiu && !repetido;
    if (colidiu != repetido) {
      repetido = colidiu;
      versaoAtual++;
    }

    if (entrou || saiu) {
      versaoAtual++;
      publicarModulos();
    }

    // um evento por vez, o mais importante primeiro
    if (acabouDeRepetir) {
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

  // ---- leituras ----

  // transforma os bytes da resposta nos valores com virgula
  void guardarValores(Modulo& modulo, const uint8_t resposta[]) {
    const Catalogo& catalogo = CATALOGO[modulo.catalogo];
    for (int i = 0; i < catalogo.quantidade; i++) {
      int16_t recebido = lerInt16(resposta, 2 + i * 2);
      modulo.valores[i] = recebido / catalogo.leituras[i].escala;
    }
    modulo.temValor = true;
  }

  // pergunta pra cada um se tem leitura nova, e so publica quem tiver
  void lerModulos() {
    for (int i = 0; i < total; i++) {
      if (modulos[i].catalogo < 0) {
        continue;
      }

      uint8_t resposta[TAM_LEITURA];
      if (!ler(modulos[i].endereco, REG_LEITURA, resposta, TAM_LEITURA)) {
        continue;
      }

      // [0] = tem nova, [1] = quantos valores vieram
      bool temNova = resposta[0] == 1;
      bool vieramTodos = resposta[1] >= CATALOGO[modulos[i].catalogo].quantidade;
      if (!temNova || !vieramTodos) {
        continue;
      }

      guardarValores(modulos[i], resposta);
      versaoAtual++;
      publicarLeitura(modulos[i]);
    }
  }

  // pergunta pros atuadores se o rele ta ligado, publica a lista so se algum mudou
  void lerEstados() {
    bool mudou = false;

    for (int i = 0; i < total; i++) {
      if (!ehAtuador(modulos[i])) {
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

  // ---- usado pelo main e pela tela ----

  void iniciar() {
    Wire.begin(I2C_SDA, I2C_SCL);
  }

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

  // manda [REG_COMANDO, 1 ou 0], sem resposta
  void comandar(uint32_t serial, bool ligar) {
    int posicao = posicaoNaLista(modulos, total, serial);
    if (posicao < 0) {
      return;
    }

    Wire.beginTransmission(modulos[posicao].endereco);
    Wire.write(REG_COMANDO);
    Wire.write(ligar ? 1 : 0);
    Wire.endTransmission();
  }

  int quantidade() {
    return total;
  }

  Modulo pegarModulo(int indice) {
    return modulos[indice];
  }

  bool temRepetido() {
    return repetido;
  }

  int versao() {
    return versaoAtual;
  }

  const char* nomeTipo(Modulo modulo) {
    if (modulo.catalogo < 0) {
      return "Desconhecido";
    }
    return CATALOGO[modulo.catalogo].nome;
  }

  int quantidadeLeituras(Modulo modulo) {
    if (modulo.catalogo < 0) {
      return 0;
    }
    return CATALOGO[modulo.catalogo].quantidade;
  }

  // indice tem q ser menor q quantidadeLeituras, tipo desconhecido tem 0
  InfoLeitura leitura(Modulo modulo, int indice) {
    return CATALOGO[modulo.catalogo].leituras[indice];
  }

  bool ehAtuador(Modulo modulo) {
    if (modulo.catalogo < 0) {
      return false;
    }
    return CATALOGO[modulo.catalogo].atuador;
  }
}
