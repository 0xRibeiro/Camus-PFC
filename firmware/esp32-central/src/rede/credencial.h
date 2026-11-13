#pragma once

// senha do broker, gravada pelo script de gravacao
namespace credencial {
  void iniciar();
  void atualizar();

  bool temSenha();
  const char* senha();
}
