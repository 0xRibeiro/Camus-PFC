#pragma once

#include <stdint.h>

namespace barramento {
  enum class Evento { NENHUM, ENTROU, SAIU, REPETIDO };

  struct Modulo {
    uint8_t endereco;
    uint8_t tipo;
    uint32_t serial;
    bool temValor;
    float valor;
  };

  void iniciar();
  Evento atualizar();

  int quantidade();
  const Modulo& modulo(int indice);
  bool temRepetido();

  // muda a cada alteracao, a tela redesenha qnd muda
  int versao();

  const char* nomeTipo(uint8_t tipo);
  const char* unidadeTipo(uint8_t tipo);

  void publicarModulos();
}
