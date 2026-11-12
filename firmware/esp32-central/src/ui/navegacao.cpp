#include "navegacao.h"

#include "../hardware/display.h"
#include "logo.h"
#include "telas/tela_modulos.h"
#include "telas/tela_vinculo.h"
#include "telas/tela_wifi.h"

namespace navegacao {
  TelaModulos telaModulos;
  TelaVinculo telaVinculo;
  TelaWifi telaWifi;

  // guarda o endereço de cada tela
  Tela* telas[] = { &telaModulos, &telaVinculo, &telaWifi };
  const int QUANTIDADE = 3;
  int ativa = 0;

  // barra de cima, 18px de altura
  void desenharNavbar() {
    display::tft.drawRGBBitmap(1, 1, LOGO, 16, 16);
  }

  // só redesenha tudo na troca
  void trocarPara(int indice) {
    ativa = indice;
    display::tft.fillScreen(ST77XX_BLACK);
    desenharNavbar();
    telas[ativa]->desenhar();
  }

  void iniciar() {
    trocarPara(0);
  }

  void atualizar(joystick::Evento evento) {
    // % faz dar a volta nas pontas
    if (evento == joystick::Evento::DIREITA) {
      trocarPara((ativa + 1) % QUANTIDADE);
    } else if (evento == joystick::Evento::ESQUERDA) {
      trocarPara((ativa + QUANTIDADE - 1) % QUANTIDADE);
    } else if (evento != joystick::Evento::NENHUM) {
      telas[ativa]->aoEvento(evento);
    }

    telas[ativa]->atualizar();
  }
}
