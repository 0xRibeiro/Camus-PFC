#pragma once

#include <stddef.h>
#include <stdint.h>

const uint8_t PROTOCOLO_VERSAO = 1;

enum class TipoModulo : uint8_t {
  DISTANCIA = 1,
  TEMPERATURA = 2,
};

const uint8_t ENDERECO_DISTANCIA = 0x10;
const uint8_t ENDERECO_TEMPERATURA = 0x11;

// 0x08 reservado
const uint8_t ENDERECO_PRIMEIRO = 0x09;
const uint8_t ENDERECO_ULTIMO = 0x77;

const uint8_t REG_IDENTIFICACAO = 0x01;
const uint8_t REG_LEITURA = 0x02;
const uint8_t REG_COMANDO = 0x03;
const uint8_t REG_ESTADO = 0x04;


// versao + tipo + serial (4) + crc
const uint8_t TAM_IDENTIFICACAO = 7;

// nova + qtd + valores int16 + crc
const uint8_t MAX_VALORES = 4;
const uint8_t TAM_LEITURA = 2 + 2 * MAX_VALORES + 1;

// estado + crc
const uint8_t TAM_ESTADO = 2;

// crc-8 smbus
inline uint8_t crc8(const uint8_t* dados, size_t tamanho) {
  uint8_t crc = 0;
  for (size_t i = 0; i < tamanho; i++) {
    crc ^= dados[i];
    for (int bit = 0; bit < 8; bit++) {
      if (crc & 0x80) {
        crc = (crc << 1) ^ 0x07;
      } else {
        crc = crc << 1;
      }
    }
  }
  return crc;
}
