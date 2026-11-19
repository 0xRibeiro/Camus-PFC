#pragma once

#include <protocolo.h>
#include <stdint.h>

namespace barramento {
  enum class Evento { NENHUM, ENTROU, SAIU, REPETIDO };

  // cada valor q o modulo manda na leitura, na msm ordem
  // escala: valor bruto / escala = valor real
  struct InfoLeitura {
    const char* nome;
    const char* rotulo;
    const char* unidade;
    float escala;
    uint8_t casas;
  };

  struct Modulo {
    uint8_t endereco;
    uint8_t tipo;
    uint32_t serial;
    bool temValor;
    float valores[MAX_VALORES];

    // so atuador, confirmado pelo ESTADO do modulo
    bool ligado;
  };

  void iniciar();
  Evento atualizar();

  int quantidade();
  const Modulo& modulo(int indice);
  bool temRepetido();

  // muda a cada alteracao, a tela redesenha qnd muda
  int versao();

  const char* nomeTipo(uint8_t tipo);
  int quantidadeLeituras(uint8_t tipo);
  const InfoLeitura& leituraTipo(uint8_t tipo, int indice);
  bool atuadorTipo(uint8_t tipo);

  void publicarModulos();

  // so atuador, quem confirma e o ESTADO
  void comandar(uint32_t serial, bool ligar);
}
