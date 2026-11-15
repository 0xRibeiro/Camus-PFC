#pragma once

#include "../tela.h"

class TelaWifi : public Tela {
public:
  void desenhar() override;
  void aoEvento(joystick::Evento evento) override;
  void atualizar() override;
  const char* nome() override;

private:
  // o q tava na tela da última vez, pra saber qnd redesenhar
  bool portalDesenhado = false;
  bool conectadoDesenhado = false;
};
