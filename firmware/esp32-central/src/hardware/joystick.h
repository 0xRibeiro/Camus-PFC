#pragma once

namespace joystick {
  enum class Evento { NENHUM, ESQUERDA, DIREITA, CIMA, BAIXO, CLIQUE };

  void iniciar();
  Evento atualizar();
}
