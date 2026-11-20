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
    barramento::Modulo modulo = barramento::pegarModulo(i);

    display::tft.setTextSize(1);
    display::tft.setTextColor(ST77XX_WHITE);
    display::tft.setCursor(4, y);
    display::tft.print(barramento::nomeTipo(modulo));

    // estado do rele do lado do nome
    if (barramento::ehAtuador(modulo)) {
      display::tft.setCursor(100, y);
      if (modulo.ligado) {
        display::tft.setTextColor(ST77XX_GREEN);
        display::tft.print("rele ON");
      } else {
        display::tft.setTextColor(ST77XX_RED);
        display::tft.print("rele OFF");
      }
    }

    int quantidade = barramento::quantidadeLeituras(modulo);
    display::tft.setTextColor(ST77XX_CYAN);

    if (!modulo.temValor) {
      display::tft.setTextSize(2);
      display::tft.setCursor(4, y + 10);
      display::tft.print("...");
    } else if (quantidade == 1) {
      barramento::InfoLeitura leitura = barramento::leitura(modulo, 0);
      display::tft.setTextSize(2);
      display::tft.setCursor(4, y + 10);
      display::tft.print(modulo.valores[0], leitura.casas);
      display::tft.print(" ");
      display::tft.print(leitura.unidade);
    } else {
      // mais de um valor n cabe grande, vai um por linha
      display::tft.setTextSize(1);
      for (int v = 0; v < quantidade; v++) {
        barramento::InfoLeitura leitura = barramento::leitura(modulo, v);
        display::tft.setCursor(4, y + 10 + v * 10);
        display::tft.print(leitura.rotulo);
        display::tft.print(": ");
        display::tft.print(modulo.valores[v], leitura.casas);
        display::tft.print(" ");
        display::tft.print(leitura.unidade);
      }
    }

    // 2 linhas pequenas ou 1 grande = 30px, mais q isso cresce
    if (quantidade > 2) {
      y += 10 + quantidade * 10;
    } else {
      y += 30;
    }
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
