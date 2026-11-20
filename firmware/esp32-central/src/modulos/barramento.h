#pragma once

#include <protocolo.h>
#include <stdint.h>

// conversa com os nanos pelo i2c: acha quem ta ligado, busca as leituras e publica no mqtt
namespace barramento {
  enum class Evento { NENHUM, ENTROU, SAIU, REPETIDO };

  // um valor q o modulo manda, ex: tds do de qualidade da agua
  struct InfoLeitura {
    // nome = o q vai pro backend, rotulo = o q aparece na telinha
    const char* nome;
    const char* rotulo;
    const char* unidade;

    // o modulo manda sem virgula: valor real = valor recebido / escala
    float escala;

    // casas depois da virgula na telinha
    uint8_t casas;
  };

  struct Modulo {
    uint8_t endereco;
    uint8_t tipo;
    uint32_t serial;

    // posicao do tipo no catalogo, -1 se a esp n conhece esse tipo
    int catalogo;

    // fica false ate chegar a 1a leitura
    bool temValor;
    float valores[MAX_VALORES];

    // so atuador, o q o modulo confirmou por ultimo
    bool ligado;
  };

  void iniciar();
  Evento atualizar();

  int quantidade();
  Modulo pegarModulo(int indice);
  bool temRepetido();

  // sobe a cada mudanca, a tela compara pra saber se redesenha
  int versao();

  // dados do catalogo pro tipo do modulo.
  // recebe uma copia do modulo, e pequeno e aqui so le
  const char* nomeTipo(Modulo modulo);
  int quantidadeLeituras(Modulo modulo);
  InfoLeitura leitura(Modulo modulo, int indice);
  bool ehAtuador(Modulo modulo);

  void publicarModulos();

  // so atuador. quem confirma e a leitura do ESTADO no proximo segundo
  void comandar(uint32_t serial, bool ligar);
}
