#pragma once

#include <protocolo.h>
#include <stdint.h>

// parte igual em todo nano: serial, i2c e as respostas pra esp.
// o main.cpp de cada modulo so cuida do sensor
namespace modulo {
  // liga o i2c no endereco e carrega o serial.
  // pinoSemente e uma entrada analogica solta, o ruido dela ajuda a sortear o serial
  void iniciar(TipoModulo tipo, uint8_t endereco, uint8_t pinoSemente);

  // guarda os valores pra qnd a esp pedir, na ordem do catalogo dela
  void entregarLeitura(int16_t valor);
  void entregarLeitura(int16_t primeiro, int16_t segundo);

  // ultimo pedido da esp pro rele, so o de temperatura usa
  bool releLigado();
}
