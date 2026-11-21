#pragma once

#include <stddef.h>
#include <stdint.h>

// ---- como a esp e os nanos conversam ----
//
// a conversa e pelo i2c, 2 fios: sda leva os dados e scl marca o ritmo.
// a esp sempre comeca, o nano so responde o q ela pergunta.
//
// cada nano tem um endereco no fio e uma lista de registradores.
// registrador e o numero da pergunta: a esp escreve ele e ja pede a resposta.
//
// toda resposta termina com um byte de crc, uma conta feita com os outros bytes.
// quem recebe refaz a conta, se der diferente algum byte chegou errado

// sobe se mudar o formato das mensagens
const uint8_t PROTOCOLO_VERSAO = 1;

// msm numero do TipoModulo do backend
enum class TipoModulo : uint8_t {
  DISTANCIA = 1,
  TEMPERATURA = 2,
  QUALIDADE_AGUA = 3,
};

// ---- enderecos ----

// um por tipo, 2 modulos iguais no fio brigam pelo msm endereco
const uint8_t ENDERECO_DISTANCIA = 0x10;
const uint8_t ENDERECO_TEMPERATURA = 0x11;
const uint8_t ENDERECO_QUALIDADE_AGUA = 0x12;

// faixa q a esp procura, o i2c reserva o q fica fora dela
const uint8_t ENDERECO_PRIMEIRO = 0x09;
const uint8_t ENDERECO_ULTIMO = 0x77;

// ---- registradores ----

// identificacao: tipo e serial do modulo
// resposta: [0] versao  [1] tipo  [2..5] serial  [6] crc
const uint8_t REG_IDENTIFICACAO = 0x01;
const uint8_t TAM_IDENTIFICACAO = 7;

// leitura: ultimos valores medidos
// resposta: [0] se e nova  [1] quantos valores  [2..9] ate 4 valores de 2 bytes  [10] crc
// valor vai sem virgula, multiplicado: 25,37 c vai como 2537
const uint8_t REG_LEITURA = 0x02;
const uint8_t MAX_VALORES = 4;
const uint8_t TAM_LEITURA = 2 + 2 * MAX_VALORES + 1;

// comando: liga ou desliga o rele, a esp manda [0x03, 1] ou [0x03, 0] e n tem resposta
const uint8_t REG_COMANDO = 0x03;

// estado: se o rele ta ligado
// resposta: [0] ligado  [1] crc
const uint8_t REG_ESTADO = 0x04;
const uint8_t TAM_ESTADO = 2;

// ---- montar e ler os bytes ----

// cada byte so guarda de 0 a 255, numero maior vai dividido em varios bytes.
// >> 8 pega o pedaco de cima do numero e << 8 coloca ele de volta no lugar

// numero de 2 bytes, pedaco de cima primeiro
inline void escreverInt16(uint8_t mensagem[], int posicao, int16_t valor) {
  mensagem[posicao] = valor >> 8;
  mensagem[posicao + 1] = valor;
}

inline int16_t lerInt16(const uint8_t mensagem[], int posicao) {
  return (mensagem[posicao] << 8) | mensagem[posicao + 1];
}

// serial tem 4 bytes, msm esquema
inline void escreverSerial(uint8_t mensagem[], int posicao, uint32_t serial) {
  mensagem[posicao] = serial >> 24;
  mensagem[posicao + 1] = serial >> 16;
  mensagem[posicao + 2] = serial >> 8;
  mensagem[posicao + 3] = serial;
}

inline uint32_t lerSerial(const uint8_t mensagem[], int posicao) {
  uint32_t serial = 0;
  for (int i = 0; i < 4; i++) {
    serial = (serial << 8) | mensagem[posicao + i];
  }
  return serial;
}

// ---- crc ----

// crc-8 padrao smbus: mistura byte por byte num acumulador, trocar qualquer byte muda o resultado
inline uint8_t crc8(const uint8_t dados[], size_t tamanho) {
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

// crc vai no ultimo byte, calculado com todos os anteriores
inline void fecharMensagem(uint8_t mensagem[], int tamanho) {
  mensagem[tamanho - 1] = crc8(mensagem, tamanho - 1);
}

inline bool mensagemIntegra(const uint8_t mensagem[], int tamanho) {
  return crc8(mensagem, tamanho - 1) == mensagem[tamanho - 1];
}
