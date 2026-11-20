#include "telas.h"

#include "../config.h"
#include "../hardware/buzzer.h"
#include "../hardware/display.h"
#include "../hardware/sons.h"
#include "../modulos/barramento.h"
#include "../rede/credencial.h"
#include "../rede/mqtt.h"
#include "../rede/wifi.h"
#include "navbar.h"

namespace telas {
  // conteudo comeca logo abaixo da navbar
  const int TOPO = navbar::ALTURA + 4;

  // limpa só embaixo da navbar, a tela tem 160x128
  void limparConteudo() {
    display::tft.fillRect(0, navbar::ALTURA, 160, 128 - navbar::ALTURA, ST77XX_BLACK);
  }

  // prepara o proximo texto, sempre com 4px de margem na esquerda
  void escreverEm(int y, int tamanho, uint16_t cor) {
    display::tft.setCursor(4, y);
    display::tft.setTextSize(tamanho);
    display::tft.setTextColor(cor);
  }

  // ---- tela de modulos ----

  // versao do barramento q ta desenhada, -1 = nenhuma ainda
  int versaoDesenhada = -1;

  // estado do rele do lado do nome
  void desenharRele(barramento::Modulo modulo, int y) {
    display::tft.setCursor(100, y);
    if (modulo.ligado) {
      display::tft.setTextColor(ST77XX_GREEN);
      display::tft.print("rele ON");
    } else {
      display::tft.setTextColor(ST77XX_RED);
      display::tft.print("rele OFF");
    }
  }

  // 1 valor vai grande, mais de 1 n cabe e vai pequeno um por linha
  void desenharValores(barramento::Modulo modulo, int y) {
    if (!modulo.temValor) {
      escreverEm(y, 2, ST77XX_CYAN);
      display::tft.print("...");
      return;
    }

    int quantidade = barramento::quantidadeLeituras(modulo);
    if (quantidade == 1) {
      barramento::InfoLeitura leitura = barramento::leitura(modulo, 0);
      escreverEm(y, 2, ST77XX_CYAN);
      display::tft.print(modulo.valores[0], leitura.casas);
      display::tft.print(" ");
      display::tft.print(leitura.unidade);
      return;
    }

    for (int i = 0; i < quantidade; i++) {
      barramento::InfoLeitura leitura = barramento::leitura(modulo, i);
      escreverEm(y + i * 10, 1, ST77XX_CYAN);
      display::tft.print(leitura.rotulo);
      display::tft.print(": ");
      display::tft.print(modulo.valores[i], leitura.casas);
      display::tft.print(" ");
      display::tft.print(leitura.unidade);
    }
  }

  // devolve a altura q ocupou, 1 valor grande ou 2 pequenos cabem em 30px
  int desenharModulo(barramento::Modulo modulo, int y) {
    escreverEm(y, 1, ST77XX_WHITE);
    display::tft.print(barramento::nomeTipo(modulo));

    if (barramento::ehAtuador(modulo)) {
      desenharRele(modulo, y);
    }
    desenharValores(modulo, y + 10);

    int quantidade = barramento::quantidadeLeituras(modulo);
    if (quantidade > 2) {
      return 10 + quantidade * 10;
    }
    return 30;
  }

  void desenharModulos() {
    versaoDesenhada = barramento::versao();
    limparConteudo();
    int y = TOPO;

    if (barramento::temRepetido()) {
      escreverEm(y, 1, ST77XX_RED);
      display::tft.print("Modulo repetido!");
      escreverEm(y + 10, 1, ST77XX_RED);
      display::tft.print("Remova um deles");
      y += 24;
    }

    if (barramento::quantidade() == 0) {
      escreverEm(y, 1, ST77XX_WHITE);
      display::tft.print("Nenhum modulo");
      return;
    }

    for (int i = 0; i < barramento::quantidade(); i++) {
      y += desenharModulo(barramento::pegarModulo(i), y);
    }
  }

  // redesenha qnd o barramento muda: modulo entrou, saiu ou chegou leitura
  void atualizarModulos() {
    if (barramento::versao() != versaoDesenhada) {
      desenharModulos();
    }
  }

  // ---- tela de vinculo ----

  enum class Vinculo { MENU, ESPERANDO, CODIGO, CONFIRMAR, RESULTADO };
  Vinculo vinculo = Vinculo::MENU;

  // 0 = gerar codigo, 1 = desvincular todos
  int opcao = 0;
  bool conectadoDesenhado = false;

  // comeca no nao pra n desvincular todo mundo sem querer
  bool confirmaSim = false;

  unsigned long pedidoEm = 0;
  unsigned long codigoChegouEm = 0;
  int segundosDesenhados = 0;

  // "> " na frente da opcao escolhida
  void desenharSeta(bool escolhida) {
    if (escolhida) {
      display::tft.print("> ");
    } else {
      display::tft.print("  ");
    }
  }

  void desenharOpcoes() {
    display::tft.fillRect(0, TOPO, 160, 28, ST77XX_BLACK);

    escreverEm(TOPO, 1, ST77XX_WHITE);
    desenharSeta(opcao == 0);
    display::tft.print("Gerar codigo");

    escreverEm(TOPO + 14, 1, ST77XX_WHITE);
    desenharSeta(opcao == 1);
    display::tft.print("Desvincular todos");
  }

  void desenharConfirmacao() {
    display::tft.fillRect(0, TOPO + 34, 160, 22, ST77XX_BLACK);

    escreverEm(TOPO + 34, 1, ST77XX_WHITE);
    desenharSeta(!confirmaSim);
    display::tft.print("Nao");

    escreverEm(TOPO + 48, 1, ST77XX_WHITE);
    desenharSeta(confirmaSim);
    display::tft.print("Sim");
  }

  // so apaga e escreve a linha do tempo, pra n piscar o codigo todo segundo
  void desenharTempo(int restante) {
    segundosDesenhados = restante;

    char texto[20];
    snprintf(texto, sizeof(texto), "Expira em %d:%02d", restante / 60, restante % 60);

    display::tft.fillRect(0, TOPO + 50, 160, 8, ST77XX_BLACK);
    escreverEm(TOPO + 50, 1, ST77XX_WHITE);
    display::tft.print(texto);
  }

  void desenharMenu() {
    conectadoDesenhado = mqtt::estaConectado();
    desenharOpcoes();

    if (conectadoDesenhado) {
      return;
    }
    escreverEm(TOPO + 40, 1, ST77XX_RED);
    if (credencial::temSenha()) {
      display::tft.print("Sem conexao");
    } else {
      display::tft.print("Sem cadastro");
    }
  }

  void desenharEsperando() {
    escreverEm(TOPO, 1, ST77XX_WHITE);
    if (opcao == 0) {
      display::tft.print("Gerando codigo...");
    } else {
      display::tft.print("Desvinculando...");
    }
  }

  void desenharPerguntaDesvincular() {
    escreverEm(TOPO, 1, ST77XX_WHITE);
    display::tft.print("Desvincular todos?");
    escreverEm(TOPO + 12, 1, ST77XX_WHITE);
    display::tft.print("Ninguem fica vinculado");
    desenharConfirmacao();
  }

  void desenharResultado() {
    escreverEm(TOPO, 1, ST77XX_WHITE);
    display::tft.print(mqtt::removidos());
    display::tft.print(" usuario(s) removido(s)");
    escreverEm(TOPO + 70, 1, ST77XX_WHITE);
    display::tft.print("Clique pra voltar");
  }

  void desenharCodigo() {
    escreverEm(TOPO, 1, ST77XX_WHITE);
    display::tft.print("Codigo:");

    // tamanho 3 = 18px por letra, x 26 centraliza os 6 digitos
    display::tft.setTextSize(3);
    display::tft.setCursor(26, TOPO + 14);
    display::tft.print(mqtt::codigo());

    desenharTempo(segundosDesenhados);
    escreverEm(TOPO + 70, 1, ST77XX_WHITE);
    display::tft.print("Clique pra voltar");
  }

  void desenharVinculo() {
    limparConteudo();

    if (vinculo == Vinculo::MENU) {
      desenharMenu();
    } else if (vinculo == Vinculo::ESPERANDO) {
      desenharEsperando();
    } else if (vinculo == Vinculo::CONFIRMAR) {
      desenharPerguntaDesvincular();
    } else if (vinculo == Vinculo::RESULTADO) {
      desenharResultado();
    } else if (vinculo == Vinculo::CODIGO) {
      desenharCodigo();
    }
  }

  void mudarVinculo(Vinculo novo) {
    vinculo = novo;
    desenharVinculo();
  }

  bool ehCimaOuBaixo(joystick::Evento evento) {
    return evento == joystick::Evento::CIMA || evento == joystick::Evento::BAIXO;
  }

  // o chegouX antes do pedido apaga alguma resposta velha q tenha sobrado
  void pedirCodigo() {
    mqtt::chegouCodigo();
    mqtt::pedirCodigo();
    pedidoEm = millis();
    mudarVinculo(Vinculo::ESPERANDO);
  }

  void pedirDesvinculo() {
    mqtt::chegouDesvinculo();
    mqtt::pedirDesvincularTodos();
    pedidoEm = millis();
    mudarVinculo(Vinculo::ESPERANDO);
  }

  void eventoNoMenu(joystick::Evento evento) {
    if (ehCimaOuBaixo(evento)) {
      opcao = 1 - opcao;
      desenharOpcoes();
      return;
    }
    if (evento != joystick::Evento::CLIQUE) {
      return;
    }

    if (!mqtt::estaConectado()) {
      buzzer::tocar(sons::ERRO);
    } else if (opcao == 0) {
      pedirCodigo();
    } else {
      confirmaSim = false;
      mudarVinculo(Vinculo::CONFIRMAR);
    }
  }

  void eventoNaConfirmacao(joystick::Evento evento) {
    if (ehCimaOuBaixo(evento)) {
      confirmaSim = !confirmaSim;
      desenharConfirmacao();
      return;
    }
    if (evento != joystick::Evento::CLIQUE) {
      return;
    }

    if (confirmaSim) {
      pedirDesvinculo();
    } else {
      mudarVinculo(Vinculo::MENU);
    }
  }

  void eventoVinculo(joystick::Evento evento) {
    bool mostrandoResposta = vinculo == Vinculo::CODIGO || vinculo == Vinculo::RESULTADO;

    if (vinculo == Vinculo::MENU) {
      eventoNoMenu(evento);
    } else if (vinculo == Vinculo::CONFIRMAR) {
      eventoNaConfirmacao(evento);
    } else if (mostrandoResposta && evento == joystick::Evento::CLIQUE) {
      mudarVinculo(Vinculo::MENU);
    }
  }

  // backend respondeu ou passou do tempo de espera
  void esperarResposta() {
    if (opcao == 0 && mqtt::chegouCodigo()) {
      codigoChegouEm = millis();
      segundosDesenhados = mqtt::validade();
      mudarVinculo(Vinculo::CODIGO);
    } else if (opcao == 1 && mqtt::chegouDesvinculo()) {
      mudarVinculo(Vinculo::RESULTADO);
    } else if (millis() - pedidoEm > VINCULO_ESPERA_MS) {
      buzzer::tocar(sons::ERRO);
      mudarVinculo(Vinculo::MENU);
    }
  }

  // conta o tempo do codigo e volta pro menu qnd expira
  void contarValidade() {
    int restante = mqtt::validade() - (millis() - codigoChegouEm) / 1000;

    if (restante <= 0) {
      mudarVinculo(Vinculo::MENU);
    } else if (restante != segundosDesenhados) {
      desenharTempo(restante);
    }
  }

  void atualizarVinculo() {
    if (vinculo == Vinculo::MENU) {
      if (mqtt::estaConectado() != conectadoDesenhado) {
        desenharVinculo();
      }
    } else if (vinculo == Vinculo::ESPERANDO) {
      esperarResposta();
    } else if (vinculo == Vinculo::CODIGO) {
      contarValidade();
    }
  }

  // ---- tela de wifi ----

  // o q tava na tela da última vez, pra saber qnd redesenhar
  bool portalDesenhado = false;
  bool wifiDesenhado = false;

  // nome e senha grandes pra ler de longe
  void desenharPortal() {
    escreverEm(TOPO, 1, ST77XX_WHITE);
    display::tft.print("Conecte na rede:");
    escreverEm(TOPO + 10, 2, ST77XX_WHITE);
    display::tft.print(wifi::nomePortal());

    escreverEm(TOPO + 32, 1, ST77XX_WHITE);
    display::tft.print("Senha:");
    escreverEm(TOPO + 42, 2, ST77XX_WHITE);
    display::tft.print(wifi::senhaPortal());

    escreverEm(TOPO + 66, 1, ST77XX_WHITE);
    display::tft.print("Fecha em ");
    display::tft.print(WIFI_PORTAL_TIMEOUT_S / 60);
    display::tft.print(" min");
  }

  void desenharConexao() {
    escreverEm(TOPO, 1, ST77XX_WHITE);
    if (wifiDesenhado) {
      display::tft.print("Conectado em:");
      escreverEm(TOPO + 12, 1, ST77XX_WHITE);
      display::tft.print(wifi::redeAtual());
    } else {
      display::tft.print("Sem Wi-Fi");
    }

    escreverEm(TOPO + 36, 1, ST77XX_WHITE);
    display::tft.print("Clique pra configurar");
  }

  void desenharWifi() {
    portalDesenhado = wifi::portalAberto();
    wifiDesenhado = wifi::estaConectado();
    limparConteudo();

    if (portalDesenhado) {
      desenharPortal();
    } else {
      desenharConexao();
    }
  }

  void eventoWifi(joystick::Evento evento) {
    if (evento == joystick::Evento::CLIQUE && !wifi::portalAberto()) {
      wifi::abrirPortal();
    }
  }

  // redesenha só qnd o portal abre/fecha ou a conexão muda
  void atualizarWifi() {
    bool mudouPortal = wifi::portalAberto() != portalDesenhado;
    bool mudouConexao = wifi::estaConectado() != wifiDesenhado;

    if (mudouPortal || mudouConexao) {
      desenharWifi();
    }
  }

  // ---- troca de tela ----

  const int TELA_MODULOS = 0;
  const int TELA_WIFI = 1;
  const int TELA_VINCULO = 2;
  const int QUANTIDADE = 3;

  // nome q aparece na navbar, na ordem das telas
  const char* NOMES[] = { "Modulos", "Wi-Fi", "Vinculo" };

  int atual = TELA_MODULOS;

  void desenharAtual() {
    if (atual == TELA_MODULOS) {
      desenharModulos();
    } else if (atual == TELA_VINCULO) {
      desenharVinculo();
    } else {
      desenharWifi();
    }
  }

  // so na troca apaga a tela inteira e redesenha a navbar
  void trocarPara(int tela) {
    atual = tela;
    display::tft.fillScreen(ST77XX_BLACK);

    // +1 pq a contagem na navbar comeca do 1
    navbar::desenhar(NOMES[atual], atual + 1, QUANTIDADE);
    desenharAtual();
  }

  // tela de modulos so mostra, n tem evento
  void repassarEvento(joystick::Evento evento) {
    if (atual == TELA_VINCULO) {
      eventoVinculo(evento);
    } else if (atual == TELA_WIFI) {
      eventoWifi(evento);
    }
  }

  void atualizarAtual() {
    if (atual == TELA_MODULOS) {
      atualizarModulos();
    } else if (atual == TELA_VINCULO) {
      atualizarVinculo();
    } else {
      atualizarWifi();
    }
  }

  void iniciar() {
    trocarPara(TELA_MODULOS);
  }

  // esquerda e direita trocam de tela e param nas pontas, o resto vai pra tela aberta
  void atualizar(joystick::Evento evento) {
    if (evento != joystick::Evento::NENHUM) {
      navbar::limparAvisos();
    }

    if (evento == joystick::Evento::DIREITA) {
      if (atual < QUANTIDADE - 1) {
        trocarPara(atual + 1);
      }
    } else if (evento == joystick::Evento::ESQUERDA) {
      if (atual > 0) {
        trocarPara(atual - 1);
      }
    } else if (evento != joystick::Evento::NENHUM) {
      repassarEvento(evento);
    }

    atualizarAtual();
    navbar::atualizar();
  }
}
