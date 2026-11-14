#include "navegacao.h"

#include "../hardware/display.h"
#include "navbar.h"
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

  // só redesenha tudo na troca
  void trocarPara(int indice) {
    ativa = indice;
    display::tft.fillScreen(ST77XX_BLACK);

    // +1 pq o índice começa no 0
    navbar::desenhar(telas[ativa]->nome(), ativa + 1, QUANTIDADE);
    telas[ativa]->desenhar();
  }

  void iniciar() {
    trocarPara(0);
  }

  void atualizar(joystick::Evento evento) {
    if (evento != joystick::Evento::NENHUM) {
      navbar::limparAvisos();
    }

    // % faz dar a volta nas pontas
    if (evento == joystick::Evento::DIREITA) {
      trocarPara((ativa + 1) % QUANTIDADE);
    } else if (evento == joystick::Evento::ESQUERDA) {
      trocarPara((ativa + QUANTIDADE - 1) % QUANTIDADE);
    } else if (evento != joystick::Evento::NENHUM) {
      telas[ativa]->aoEvento(evento);
    }

    telas[ativa]->atualizar();
    navbar::atualizar();
  }
}
