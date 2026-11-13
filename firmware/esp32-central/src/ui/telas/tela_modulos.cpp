#include "tela_modulos.h"

#include "../../hardware/display.h"
#include "../../modulos/barramento.h"
#include "../navbar.h"

void TelaModulos::desenhar() {
  versaoDesenhada = barramento::versao();
  display::tft.fillRect(0, navbar::ALTURA, 160, 128 - navbar::ALTURA, ST77XX_BLACK);
  display::tft.setTextSize(1);

  int y = navbar::ALTURA + 4;

  if (barramento::temRepetido()) {
    display::tft.setTextColor(ST77XX_RED);
    display::tft.setCursor(4, y);
    display::tft.print("Modulo repetido!");
    display::tft.setCursor(4, y + 10);
    display::tft.print("Remova um deles");
    y += 24;
  }

  if (barramento::quantidade() == 0) {
    display::tft.setTextColor(ST77XX_WHITE);
    display::tft.setCursor(4, y);
    display::tft.print("Nenhum modulo");
    return;
  }

  for (int i = 0; i < barramento::quantidade(); i++) {
    const barramento::Modulo& modulo = barramento::modulo(i);

    display::tft.setTextSize(1);
    display::tft.setTextColor(ST77XX_WHITE);
    display::tft.setCursor(4, y);
    display::tft.print(barramento::nomeTipo(modulo.tipo));

    display::tft.setTextSize(2);
    display::tft.setTextColor(ST77XX_CYAN);
    display::tft.setCursor(4, y + 10);

    if (modulo.temValor) {
      display::tft.print(modulo.valor, 1);
      display::tft.print(" ");
      display::tft.print(barramento::unidadeTipo(modulo.tipo));
    } else {
      display::tft.print("...");
    }

    y += 30;
  }
}

// tela só de info, sem interação
void TelaModulos::aoEvento(joystick::Evento evento) {}

const char* TelaModulos::nome() {
  return "Modulos";
}

void TelaModulos::atualizar() {
  if (barramento::versao() != versaoDesenhada) {
    desenhar();
  }
}
