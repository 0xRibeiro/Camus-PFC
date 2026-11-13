#pragma once

namespace mqtt {
  enum class Evento { NENHUM, CONECTOU, CAIU };

  void iniciar();
  Evento atualizar();

  bool estaConectado();

  // sufixo depois de camus/dispositivos/<mac>/
  void publicar(const char* sufixo, const char* mensagem, bool retido);

  void pedirCodigo();
  void pedirDesvincularTodos();

  bool chegouCodigo();
  const char* codigo();
  int validade();

  bool chegouDesvinculo();
  int removidos();
}
