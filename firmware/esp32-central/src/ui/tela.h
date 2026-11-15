#pragma once

#include "../hardware/joystick.h"

// contrato q toda tela segue
class Tela {
public:
  // desenho completo quando a tela aparece
  virtual void desenhar() = 0;
  virtual void aoEvento(joystick::Evento evento) = 0;

  // nome q aparece na navbar
  virtual const char* nome() = 0;

  // pra tela q muda sozinha
  virtual void atualizar() {}
};