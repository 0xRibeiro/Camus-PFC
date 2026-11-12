#pragma once

#include "../tela.h"

class TelaVinculo : public Tela {
public:
  void desenhar() override;
  void aoEvento(joystick::Evento evento) override;
  const char* nome() override;
};
