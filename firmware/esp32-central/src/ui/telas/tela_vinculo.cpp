#include "tela_vinculo.h"

#include "../../config.h"
#include "../../hardware/buzzer.h"
#include "../../hardware/display.h"
#include "../../hardware/sons.h"
#include "../../rede/mqtt.h"
#include "../navbar.h"

const int TOPO = navbar::ALTURA + 4;

void TelaVinculo::desenharOpcoes() {
  display::tft.fillRect(0, TOPO, 160, 28, ST77XX_BLACK);
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(1);

  display::tft.setCursor(4, TOPO);
  display::tft.print(opcao == 0 ? "> " : "  ");
  display::tft.print("Gerar codigo");

  display::tft.setCursor(4, TOPO + 14);
  display::tft.print(opcao == 1 ? "> " : "  ");
  display::tft.print("Desvincular todos");
}

void TelaVinculo::desenharConfirmacao() {
  display::tft.fillRect(0, TOPO + 34, 160, 22, ST77XX_BLACK);
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(1);

  display::tft.setCursor(4, TOPO + 34);
  display::tft.print(confirmaSim ? "  " : "> ");
  display::tft.print("Nao");

  display::tft.setCursor(4, TOPO + 48);
  display::tft.print(confirmaSim ? "> " : "  ");
  display::tft.print("Sim");
}

void TelaVinculo::desenharTempo(int restante) {
  segundosDesenhados = restante;

  char texto[20];
  snprintf(texto, sizeof(texto), "Expira em %d:%02d", restante / 60, restante % 60);

  display::tft.fillRect(0, TOPO + 50, 160, 8, ST77XX_BLACK);
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(1);
  display::tft.setCursor(4, TOPO + 50);
  display::tft.print(texto);
}

void TelaVinculo::desenhar() {
  display::tft.fillRect(0, navbar::ALTURA, 160, 128 - navbar::ALTURA, ST77XX_BLACK);
  display::tft.setTextColor(ST77XX_WHITE);
  display::tft.setTextSize(1);

  if (estado == Estado::MENU) {
    conectadoDesenhado = mqtt::estaConectado();
    desenharOpcoes();

    if (!conectadoDesenhado) {
      display::tft.setTextColor(ST77XX_RED);
      display::tft.setCursor(4, TOPO + 40);
      display::tft.print("Sem conexao");
    }
  } else if (estado == Estado::ESPERANDO) {
    display::tft.setCursor(4, TOPO);
    display::tft.print(opcao == 0 ? "Gerando codigo..." : "Desvinculando...");
  } else if (estado == Estado::CONFIRMAR) {
    display::tft.setCursor(4, TOPO);
    display::tft.print("Desvincular todos?");
    display::tft.setCursor(4, TOPO + 12);
    display::tft.print("Ninguem fica vinculado");
    desenharConfirmacao();
  } else if (estado == Estado::RESULTADO) {
    display::tft.setCursor(4, TOPO);
    display::tft.print(mqtt::removidos());
    display::tft.print(" usuario(s) removido(s)");
    display::tft.setCursor(4, TOPO + 70);
    display::tft.print("Clique pra voltar");
  } else if (estado == Estado::CODIGO) {
    display::tft.setCursor(4, TOPO);
    display::tft.print("Codigo:");

    // tamanho 3 = 18px por letra, 6 digitos centralizados
    display::tft.setTextSize(3);
    display::tft.setCursor(26, TOPO + 14);
    display::tft.print(mqtt::codigo());

    desenharTempo(segundosDesenhados);

    display::tft.setCursor(4, TOPO + 70);
    display::tft.print("Clique pra voltar");
  }
}

void TelaVinculo::voltarProMenu() {
  estado = Estado::MENU;
  desenhar();
}

void TelaVinculo::aoEvento(joystick::Evento evento) {
  if (estado == Estado::MENU) {
    if (evento == joystick::Evento::CIMA || evento == joystick::Evento::BAIXO) {
      opcao = 1 - opcao;
      desenharOpcoes();
    } else if (evento == joystick::Evento::CLIQUE) {
      if (!mqtt::estaConectado()) {
        buzzer::tocar(sons::ERRO);
      } else if (opcao == 0) {
        mqtt::chegouCodigo();
        mqtt::pedirCodigo();
        pedidoEm = millis();
        estado = Estado::ESPERANDO;
        desenhar();
      } else {
        confirmaSim = false;
        estado = Estado::CONFIRMAR;
        desenhar();
      }
    }
  } else if (estado == Estado::CONFIRMAR) {
    if (evento == joystick::Evento::CIMA || evento == joystick::Evento::BAIXO) {
      confirmaSim = !confirmaSim;
      desenharConfirmacao();
    } else if (evento == joystick::Evento::CLIQUE && !confirmaSim) {
      voltarProMenu();
    } else if (evento == joystick::Evento::CLIQUE) {
      mqtt::chegouDesvinculo();
      mqtt::pedirDesvincularTodos();
      pedidoEm = millis();
      estado = Estado::ESPERANDO;
      desenhar();
    }
  } else if (evento == joystick::Evento::CLIQUE && (estado == Estado::CODIGO || estado == Estado::RESULTADO)) {
    voltarProMenu();
  }
}

void TelaVinculo::atualizar() {
  if (estado == Estado::MENU) {
    if (mqtt::estaConectado() != conectadoDesenhado) {
      desenhar();
    }
  } else if (estado == Estado::ESPERANDO) {
    if (opcao == 0 && mqtt::chegouCodigo()) {
      codigoChegouEm = millis();
      segundosDesenhados = mqtt::validade();
      estado = Estado::CODIGO;
      desenhar();
    } else if (opcao == 1 && mqtt::chegouDesvinculo()) {
      estado = Estado::RESULTADO;
      desenhar();
    } else if (millis() - pedidoEm > VINCULO_ESPERA_MS) {
      buzzer::tocar(sons::ERRO);
      voltarProMenu();
    }
  } else if (estado == Estado::CODIGO) {
    int restante = mqtt::validade() - (millis() - codigoChegouEm) / 1000;

    if (restante <= 0) {
      voltarProMenu();
    } else if (restante != segundosDesenhados) {
      desenharTempo(restante);
    }
  }
}

const char* TelaVinculo::nome() {
  return "Vinculo";
}
