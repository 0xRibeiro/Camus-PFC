#pragma once

#include "../hardware/joystick.h"

// as 3 telas da esp e a troca entre elas pelo joystick
namespace telas {
  void iniciar();
  void atualizar(joystick::Evento evento);
}
