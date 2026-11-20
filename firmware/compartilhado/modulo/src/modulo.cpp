#include "modulo.h"

#include <Arduino.h>
#include <EEPROM.h>
#include <Wire.h>

namespace modulo {
  TipoModulo tipoModulo;
  uint32_t serial = 0;

  // ---- variaveis divididas com a interrupcao ----
  //
  // qnd a esp fala no fio o nano pausa o loop, roda o aoReceber ou aoPedir e depois volta.
  // essa pausa e a interrupcao. volatile obriga o nano a ler a variavel da memoria toda vez,
  // senao ele pode usar um valor velho q guardou antes da interrupcao mudar

  // ultimo registrador q a esp escreveu
  volatile uint8_t registrador = 0;

  volatile int16_t valores[MAX_VALORES];
  volatile uint8_t quantidadeValores = 0;

  // true qnd tem leitura nova, volta pra false qnd a esp busca
  volatile bool temNova = false;

  volatile bool rele = false;

  // ---- serial ----

  // eeprom e a memoria q n apaga qnd desliga, o serial fica nos 4 primeiros bytes.
  // nano novo vem com tudo em 0xFF
  bool serialValido(uint32_t valor) {
    return valor != 0xFFFFFFFF && valor != 0;
  }

  // mistura o ruido do pino solto com o tempo desde q ligou, pra 2 placas n sortearem o msm
  uint32_t sortearSerial(uint8_t pinoSemente) {
    uint32_t semente = micros();
    for (int i = 0; i < 32; i++) {
      semente = (semente << 1) ^ analogRead(pinoSemente);
    }
    randomSeed(semente);

    // random so vai ate 16 bits, junta 2 sorteios pra completar os 32
    uint32_t parteDeCima = random(0x10000);
    uint32_t parteDeBaixo = random(0x10000);
    return (parteDeCima << 16) | parteDeBaixo;
  }

  // sorteia so na 1a vez q liga, depois le sempre o msm da eeprom
  void carregarSerial(uint8_t pinoSemente) {
    EEPROM.get(0, serial);

    if (!serialValido(serial)) {
      serial = sortearSerial(pinoSemente);
      EEPROM.put(0, serial);
    }

    Serial.print("serial: ");
    Serial.println(serial, HEX);
  }

  // ---- respostas pra esp ----

  void responderIdentificacao() {
    uint8_t resposta[TAM_IDENTIFICACAO];
    resposta[0] = PROTOCOLO_VERSAO;
    resposta[1] = (uint8_t) tipoModulo;
    escreverSerial(resposta, 2, serial);
    fecharMensagem(resposta, TAM_IDENTIFICACAO);
    Wire.write(resposta, TAM_IDENTIFICACAO);
  }

  // posicao sem valor vai zerada
  void responderLeitura() {
    uint8_t resposta[TAM_LEITURA] = {0};
    resposta[0] = temNova;
    resposta[1] = quantidadeValores;
    for (int i = 0; i < quantidadeValores; i++) {
      escreverInt16(resposta, 2 + i * 2, valores[i]);
    }
    fecharMensagem(resposta, TAM_LEITURA);
    Wire.write(resposta, TAM_LEITURA);

    // esp ja pegou, so marca de novo na proxima medida
    temNova = false;
  }

  void responderEstado() {
    uint8_t resposta[TAM_ESTADO];
    resposta[0] = rele;
    fecharMensagem(resposta, TAM_ESTADO);
    Wire.write(resposta, TAM_ESTADO);
  }

  // ---- interrupcoes do i2c ----

  // esp escreveu: 1o byte e o registrador, no comando a acao vem logo depois
  void aoReceber(int quantidade) {
    registrador = Wire.read();

    if (registrador == REG_COMANDO && Wire.available()) {
      rele = Wire.read() == 1;
    }

    // descarta o resto
    while (Wire.available()) {
      Wire.read();
    }
  }

  // esp pediu resposta, responde o ultimo registrador q ela escreveu
  void aoPedir() {
    if (registrador == REG_IDENTIFICACAO) {
      responderIdentificacao();
    } else if (registrador == REG_LEITURA) {
      responderLeitura();
    } else if (registrador == REG_ESTADO) {
      responderEstado();
    }
  }

  // ---- usado pelo main ----

  void iniciar(TipoModulo tipo, uint8_t endereco, uint8_t pinoSemente) {
    tipoModulo = tipo;

    // serial do pc, so pra acompanhar as medidas no monitor
    Serial.begin(115200);
    carregarSerial(pinoSemente);

    Wire.begin(endereco);

    // o nano puxa os fios do i2c pra 5v, mas a esp e 3,3v.
    // low desliga esse puxador e o fio fica so no 3,3v da esp
    digitalWrite(SDA, LOW);
    digitalWrite(SCL, LOW);

    // funcoes q o Wire chama qnd a esp escreve ou pede resposta
    Wire.onReceive(aoReceber);
    Wire.onRequest(aoPedir);
  }

  // noInterrupts segura a esp ate terminar de trocar tudo, senao ela pode pegar metade nova e metade velha
  void entregarLeitura(int16_t valor) {
    noInterrupts();
    valores[0] = valor;
    quantidadeValores = 1;
    temNova = true;
    interrupts();
  }

  void entregarLeitura(int16_t primeiro, int16_t segundo) {
    noInterrupts();
    valores[0] = primeiro;
    valores[1] = segundo;
    quantidadeValores = 2;
    temNova = true;
    interrupts();
  }

  bool releLigado() {
    return rele;
  }
}
