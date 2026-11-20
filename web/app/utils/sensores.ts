import type { SerieLeitura } from '~/types/generated'

// zoom do eixo vertical de cada leitura, na unidade do sensor.
// alturaMinimaEixo: o eixo nunca fica menor q isso, aumentou e as variacoes pequenas ficam mais achatadas
// folga: espaco em cima e embaixo da linha, 0.2 = 20% da variacao de cada lado
export const SENSORES: Record<string, { alturaMinimaEixo: number, folga: number }> = {
  distancia: { alturaMinimaEixo: 2, folga: 0.2 },
  temperatura: { alturaMinimaEixo: 2, folga: 0.2 },
  tds: { alturaMinimaEixo: 20, folga: 0.2 },
  turbidez: { alturaMinimaEixo: 5, folga: 0.2 },
}

const SENSOR_PADRAO = { alturaMinimaEixo: 1, folga: 0.2 }

// 1, 2 ou 5 vezes uma potencia de 10, pros numeros do eixo ficarem redondos
function passoRedondo(tamanho: number) {
  const potencia = 10 ** Math.floor(Math.log10(tamanho))
  if (tamanho <= potencia) return potencia
  if (tamanho <= potencia * 2) return potencia * 2
  if (tamanho <= potencia * 5) return potencia * 5
  return potencia * 10
}

// menor e maior do eixo vertical a partir das leituras do grafico
export function calcularEixo(nome: string, menor: number, maior: number): [number, number] {
  const sensor = SENSORES[nome] ?? SENSOR_PADRAO
  const folga = (maior - menor) * sensor.folga
  let inicio = menor - folga
  let fim = maior + folga

  // abre ate a altura minima mantendo a linha no meio
  const falta = sensor.alturaMinimaEixo - (fim - inicio)
  if (falta > 0) {
    inicio -= falta / 2
    fim += falta / 2
  }

  // leitura q nunca foi negativa n precisa de eixo negativo
  if (menor >= 0 && inicio < 0) {
    fim -= inicio
    inicio = 0
  }

  const passo = passoRedondo((fim - inicio) / 4)
  return [Math.floor(inicio / passo) * passo, Math.ceil(fim / passo) * passo]
}

// valor grande do card, leitura fora da faixa n aparece como numero
export function textoAtual(serie: SerieLeitura | undefined, formatar: (valor: number) => string) {
  if (!serie?.atual) return '—'
  if (serie.atual_erro) return 'Erro de leitura'
  return formatar(serie.atual.valor)
}
