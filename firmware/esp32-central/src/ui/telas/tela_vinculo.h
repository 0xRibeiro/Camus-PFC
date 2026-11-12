#pragma once

#include "../tela.h"

class TelaVinculo : public Tela {
public:
  void desenhar() override;
  void aoEvento(joystick::Evento evento) override;
  void atualizar() override;
  const char* nome() override;

private:
  enum class Estado { MENU, ESPERANDO, CODIGO, CONFIRMAR, RESULTADO };
  Estado estado = Estado::MENU;

  // 0 = gerar codigo, 1 = desvincular todos
  int opcao = 0;
  bool conectadoDesenhado = false;

  // comeca no nao pra n apagar sem querer
  bool confirmaSim = false;

  unsigned long pedidoEm = 0;
  unsigned long codigoChegouEm = 0;
  int segundosDesenhados = 0;

  void desenharOpcoes();
  void desenharConfirmacao();
  void desenharTempo(int restante);
  void voltarProMenu();
};
