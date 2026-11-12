#pragma once

namespace mqtt {
  enum class Evento { NENHUM, CONECTOU, CAIU };

  void iniciar();
  Evento atualizar();

  bool estaConectado();
}
