#include <Arduino.h>
#include <modulo.h>

// os 2 sensores sao analogicos, soltam uma tensao de 0 a 5v no fio
#define TDS A0
#define TURBIDEZ A1

// a0 ja tem sensor, o a7 fica solto pro sorteio do serial
#define PINO_SEMENTE A7

#define INTERVALO_MS 5000

// 30 amostras a cada 40ms = ultimo 1,2s de leituras
#define AMOSTRA_MS 40
#define AMOSTRAS 30

// analogRead vai de 0 a 1023, 1024 seria os 5v
#define TENSAO_MAXIMA 5.0
#define ESCALA_ANALOGICA 1024.0

// sem sensor de temperatura aqui, compensa como se a agua tivesse sempre 25 c
#define TEMPERATURA_TDS 25.0

// anel de amostras, a mais nova entra no lugar da mais velha
int amostrasTds[AMOSTRAS];
int amostrasTurbidez[AMOSTRAS];
int posicao = 0;
bool encheu = false;

unsigned long ultimaAmostra = 0;
unsigned long ultimaMedida = 0;

// ---- amostras ----

void guardarAmostra() {
  amostrasTds[posicao] = analogRead(TDS);
  amostrasTurbidez[posicao] = analogRead(TURBIDEZ);

  posicao++;
  if (posicao == AMOSTRAS) {
    posicao = 0;
    encheu = true;
  }
}

// copia e ordena do menor pro maior, cada numero anda pra tras ate achar o lugar dele
void ordenar(const int origem[], int ordenadas[]) {
  for (int i = 0; i < AMOSTRAS; i++) {
    ordenadas[i] = origem[i];
  }

  for (int i = 1; i < AMOSTRAS; i++) {
    int atual = ordenadas[i];
    int j = i - 1;
    while (j >= 0 && ordenadas[j] > atual) {
      ordenadas[j + 1] = ordenadas[j];
      j--;
    }
    ordenadas[j + 1] = atual;
  }
}

// mediana = a do meio depois de ordenar, pico de ruido vai pra ponta e fica de fora
float tensaoMediana(const int amostras[]) {
  int ordenadas[AMOSTRAS];
  ordenar(amostras, ordenadas);
  return ordenadas[AMOSTRAS / 2] * TENSAO_MAXIMA / ESCALA_ANALOGICA;
}

// ---- conversao ----

// tds = sais e minerais dissolvidos, em ppm = partes por milhao.
// curva do fabricante, dfrobot sen0244
int16_t calcularTds(float tensao) {
  float compensada = tensao / (1.0 + 0.02 * (TEMPERATURA_TDS - 25.0));
  float ppm = (133.42 * compensada * compensada * compensada
    - 255.86 * compensada * compensada
    + 857.39 * compensada) * 0.5;

  if (ppm < 0) {
    return 0;
  }
  return ppm;
}

// turbidez = o quanto a agua ta turva, em ntu, vai x10.
// curva do fabricante dfrobot sen0189, so vale de 2,5v a 4,2v:
// acima disso e agua limpa = 0, abaixo e o maximo da escala = 3000 ntu
int16_t calcularTurbidez(float tensao) {
  if (tensao >= 4.2) {
    return 0;
  }
  if (tensao <= 2.5) {
    return 30000;
  }

  float ntu = -1120.4 * tensao * tensao + 5742.3 * tensao - 4352.9;
  if (ntu < 0) {
    return 0;
  }
  return ntu * 10;
}

// ---- medida ----

void medirEEntregar() {
  float tensaoTds = tensaoMediana(amostrasTds);
  float tensaoTurbidez = tensaoMediana(amostrasTurbidez);
  int16_t tds = calcularTds(tensaoTds);
  int16_t turbidez = calcularTurbidez(tensaoTurbidez);

  // ordem igual ao catalogo da esp: tds, turbidez
  modulo::entregarLeitura(tds, turbidez);

  Serial.print("tds v: ");
  Serial.print(tensaoTds, 2);
  Serial.print(" ppm: ");
  Serial.print(tds);
  Serial.print(" | turbidez v: ");
  Serial.print(tensaoTurbidez, 2);
  Serial.print(" ntu x10: ");
  Serial.println(turbidez);
}

void setup() {
  modulo::iniciar(TipoModulo::QUALIDADE_AGUA, ENDERECO_QUALIDADE_AGUA, PINO_SEMENTE);
}

// amostra o tempo todo, mas so mede a cada 5s e com o anel cheio
void loop() {
  if (millis() - ultimaAmostra >= AMOSTRA_MS) {
    ultimaAmostra = millis();
    guardarAmostra();
  }

  if (!encheu || millis() - ultimaMedida < INTERVALO_MS) {
    return;
  }
  ultimaMedida = millis();
  medirEEntregar();
}
