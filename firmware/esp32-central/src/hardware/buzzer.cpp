#include "buzzer.h"

#include <Arduino.h>

#include "../config.h"

namespace buzzer {
  // som q tá tocando agora
  const Nota* somAtual = nullptr;
  int quantidadeNotas = 0;
  int notaAtual = 0;
  unsigned long inicioNota = 0;

  // começa em silêncio
  void iniciar() {
    pinMode(BUZZER, OUTPUT);
    digitalWrite(BUZZER, LOW);
  }

  // solta a nota da vez e marca qnd começou
  void tocarNotaAtual() {
    Nota nota = somAtual[notaAtual];

    if (nota.frequencia == PAUSA) {
      noTone(BUZZER);
    } else {
      tone(BUZZER, nota.frequencia);
    }

    inicioNota = millis();
  }

  // o som novo passa por cima do q tiver tocando
  void tocar(const Nota* notas, int quantidade) {
    somAtual = notas;
    quantidadeNotas = quantidade;
    notaAtual = 0;
    tocarNotaAtual();
  }

  // passa pra próxima nota
  void atualizar() {
    if (somAtual == nullptr) {
      return;
    }

    if (millis() - inicioNota < somAtual[notaAtual].duracao) {
      return;
    }

    notaAtual++;

    // acabou o som, volta pro silêncio
    if (notaAtual >= quantidadeNotas) {
      noTone(BUZZER);
      somAtual = nullptr;
      return;
    }

    tocarNotaAtual();
  }
}