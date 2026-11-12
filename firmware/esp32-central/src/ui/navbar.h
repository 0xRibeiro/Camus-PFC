#pragma once

namespace navbar {
  // 18 da barra + 8 da divisória, as telas desenham daqui pra baixo
  const int ALTURA = 26;

  void desenhar(const char* nome, int pagina, int total);
  void definirWifi(bool conectado);
  void definirBroker(bool conectado);
  void avisarModuloNovo();
  void avisarModuloSaiu();
  void limparAvisos();
  void atualizar();
}
