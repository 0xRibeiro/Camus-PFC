#pragma once

#include "../tela.h"

class TelaWifi : public Tela {
public:
  void desenhar() override;
  void aoEvento(joystick::Evento evento) override;
};
