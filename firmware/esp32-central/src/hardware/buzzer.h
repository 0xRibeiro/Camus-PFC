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

  // pega o tamanho do array de notas
  template <int N>
  void tocar(const Nota (&notas)[N]) {
    tocar(notas, N);
  }
}