#pragma once

#include <Arduino.h>

namespace wifi {
  enum class Evento { NENHUM, CONECTOU, CAIU };

  void iniciar();
  void abrirPortal();
  Evento atualizar();

  bool portalAberto();
  const char* nomePortal();
  const char* senhaPortal();
  bool estaConectado();
  String redeAtual();
}
