#pragma once

namespace mqtt {
  enum class Evento { NENHUM, CONECTOU, CAIU };

  void iniciar();
  Evento atualizar();

  bool estaConectado();

  void pedirCodigo();
  void pedirDesvincularTodos();

  bool chegouCodigo();
  const char* codigo();
  int validade();

  bool chegouDesvinculo();
  int removidos();
}
