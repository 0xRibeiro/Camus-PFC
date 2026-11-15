import { Capacitor, CapacitorHttp } from '@capacitor/core'
import { version } from '../../package.json'

// arquivo q o ci publica junto do apk, o latest sempre aponta pra release mais nova
const URL_VERSAO = 'https://github.com/0xRibeiro/Camus-PFC/releases/latest/download/versao.json'

type VersaoPublicada = {
  atual: string
  minima: string
  apk: string
}

// compara numero por numero, como texto "0.10.0" ficaria menor q "0.9.0"
// devolve negativo se a < b, 0 se igual, positivo se a > b
export function compararVersoes(a: string, b: string) {
  const partesA = a.split('.')
  const partesB = b.split('.')
  for (let i = 0; i < 3; i++) {
    const diferenca = Number(partesA[i] ?? 0) - Number(partesB[i] ?? 0)
    if (diferenca !== 0) {
      return diferenca
    }
  }
  return 0
}

// so roda no app, no site a versao ja é sempre a mais nova
export function useVersaoApp() {
  // ok = em dia, aviso = tem versao nova, bloqueado = abaixo da minima
  const estado = ref<'ok' | 'aviso' | 'bloqueado'>('ok')
  const versaoNova = ref('')
  const linkApk = ref('')

  async function verificar() {
    if (!Capacitor.isNativePlatform()) {
      return
    }

    // requisicao pelo lado nativo, o download de release do github n manda cors
    let publicada: VersaoPublicada
    try {
      const resposta = await CapacitorHttp.get({ url: URL_VERSAO })
      if (resposta.status !== 200) {
        return
      }
      publicada = resposta.data
      // dependendo do content-type o github devolve como texto
      if (typeof publicada === 'string') {
        publicada = JSON.parse(publicada)
      }
    }
    catch {
      // sem internet ou github fora, deixa usar em vez de travar todo mundo
      return
    }

    versaoNova.value = publicada.atual
    linkApk.value = publicada.apk

    if (compararVersoes(version, publicada.minima) < 0) {
      estado.value = 'bloqueado'
    }
    else if (compararVersoes(version, publicada.atual) < 0) {
      estado.value = 'aviso'
    }
  }

  return { estado, versaoNova, linkApk, verificar }
}
