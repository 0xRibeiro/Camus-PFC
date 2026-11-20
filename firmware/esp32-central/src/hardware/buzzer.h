#pragma once

#include "notas.h"

namespace buzzer {
  // frequência em Hz e tempo
  struct Nota {
    int frequencia;
    int duracao;
  };

  void iniciar();
  void tocar(const Nota* notas, int quantidade);
  void atualizar();

  // template descobre sozinho quantas notas o som tem,
  // da pra chamar so tocar(sons::ERRO) sem passar a quantidade
  template <int N>
  void tocar(const Nota (&notas)[N]) {
    tocar(notas, N);
  }
}