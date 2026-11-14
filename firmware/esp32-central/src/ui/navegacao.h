#pragma once

#include "../hardware/joystick.h"

namespace navegacao {
  void iniciar();
  void atualizar(joystick::Evento evento);
}
