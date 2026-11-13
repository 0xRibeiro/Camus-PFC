#include "credencial.h"

#include <Arduino.h>
#include <Preferences.h>

namespace credencial {
  Preferences preferencias;

  char senhaSalva[64] = "";

  // linha da serial ate o \n
  char linha[80];
  int tamanhoLinha = 0;

  void iniciar() {
    preferencias.begin("camus", false);
    preferencias.getString("senha", senhaSalva, sizeof(senhaSalva));
  }

  // "senha:<x>" salva e reinicia pro mqtt subir com ela
  void processarLinha() {
    if (strncmp(linha, "senha:", 6) != 0) {
      return;
    }

    preferencias.putString("senha", linha + 6);
    Serial.println("ok");
    Serial.flush();
    ESP.restart();
  }

  void atualizar() {
    while (Serial.available()) {
      char letra = Serial.read();

      if (letra == '\r') {
        continue;
      }

      if (letra == '\n') {
        linha[tamanhoLinha] = '\0';
        processarLinha();
        tamanhoLinha = 0;
      } else if (tamanhoLinha < (int) sizeof(linha) - 1) {
        linha[tamanhoLinha] = letra;
        tamanhoLinha++;
      }
    }
  }

  bool temSenha() {
    return senhaSalva[0] != '\0';
  }

  const char* senha() {
    return senhaSalva;
  }
}
