#pragma once

#include <stdint.h>

namespace mqtt {
  enum class Evento { NENHUM, CONECTOU, CAIU };

  void iniciar();
  Evento atualizar();

  bool estaConectado();

  const char* identificador();

  // sufixo depois de camus/dispositivos/<mac>/
  void publicar(const char* sufixo, const char* mensagem, bool retido);

  void pedirCodigo();
  void pedirDesvincularTodos();

  bool chegouCodigo();
  const char* codigo();
  int validade();

  bool chegouDesvinculo();
  int removidos();

  // comando pra um modulo, true so uma vez por mensagem
  bool chegouComando();
  uint32_t serialComando();
  bool ligarComando();
}
