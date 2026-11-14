#pragma once

#include "buzzer.h"

namespace sons {

  const buzzer::Nota WIFI_CONECTOU[] = {
    { NOTE_C5, 80 },
    { NOTE_E5, 80 },
    { NOTE_G5, 80 },
    { NOTE_C6, 160 },
  };

  const buzzer::Nota WIFI_CAIU[] = {
    { NOTE_G5, 150 },
    { NOTE_DS5, 150 },
    { NOTE_C5, 150 },
    { PAUSA, 60 },
    { NOTE_FS4, 500 },
  };

  const buzzer::Nota MODULO_NOVO[] = {
    { NOTE_E6, 60 },
    { NOTE_A6, 100 },
  };

  const buzzer::Nota MODULO_SAIU[] = {
    { NOTE_A6, 60 },
    { NOTE_E6, 100 },
  };

  const buzzer::Nota ERRO[] = {
    { NOTE_C4, 200 },
    { PAUSA, 80 },
    { NOTE_C4, 300 },
  };
}
