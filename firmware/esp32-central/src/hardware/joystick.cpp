#include "joystick.h"

#include <Arduino.h>

#include "../config.h"

namespace joystick {
  unsigned long ultimaLeitura = 0;

  // só dispara de novo depois de voltar pro meio
  bool centralizado = true;

  void iniciar() {
    pinMode(JOY_SW, INPUT_PULLUP);
  }

  Evento atualizar() {
    // só lê a cada intervalo, sem delay
    if (millis() - ultimaLeitura < JOY_INTERVALO_MS) {
      return Evento::NENHUM;
    }
    ultimaLeitura = millis();

    int horizontal = analogRead(JOY_HORIZONTAL);
    int vertical = analogRead(JOY_VERTICAL);
    bool apertado = digitalRead(JOY_SW) == LOW;

    bool noMeio = horizontal >= JOY_LIMITE_BAIXO && horizontal <= JOY_LIMITE_ALTO
               && vertical >= JOY_LIMITE_BAIXO && vertical <= JOY_LIMITE_ALTO
               && !apertado;

    if (noMeio) {
      centralizado = true;
      return Evento::NENHUM;
    }
    if (!centralizado) {
      return Evento::NENHUM;
    }
    centralizado = false;

    // diagonal vai pela ordem
    if (apertado) return Evento::CLIQUE;
    if (horizontal < JOY_LIMITE_BAIXO) return Evento::ESQUERDA;
    if (horizontal > JOY_LIMITE_ALTO) return Evento::DIREITA;
    if (vertical > JOY_LIMITE_ALTO) return Evento::CIMA;
    if (vertical < JOY_LIMITE_BAIXO) return Evento::BAIXO;
    return Evento::NENHUM;
  }
}