import { Capacitor, CapacitorHttp } from '@capacitor/core'
import { version } from '../../package.json'

// arquivo q o ci publica junto do apk, o latest sempre aponta pra release mais nova
const URL_VERSAO = 'https://github.com/0xRibeiro/Camus-PFC/releases/latest/download/versao.json'

// numeric compara os numeros pelo valor, se n "0.10.0" ficaria menor q "0.9.0"
function menorQue(a: string, b: string) {
  return a.localeCompare(b, undefined, { numeric: true }) < 0
}

// so roda no app, no site a versao ja é sempre a mais nova
export function useVersaoApp() {
  // ok = em dia, aviso = tem versao nova, bloqueado = abaixo da minima
  const estado = ref<'ok' | 'aviso' | 'bloqueado'>('ok')
  const publicada = ref({ atual: '', minima: '', apk: '' })

  async function verificar() {
    if (!Capacitor.isNativePlatform()) {
      return
    }

    // requisicao pelo lado nativo, o download de release do github n manda cors
    try {
      const resposta = await CapacitorHttp.get({ url: URL_VERSAO, responseType: 'json' })
      if (resposta.status !== 200) {
        return
      }
      publicada.value = resposta.data
    }
    catch {
      // sem internet ou github fora, deixa usar em vez de travar todo mundo
      return
    }

    if (menorQue(version, publicada.value.minima)) {
      estado.value = 'bloqueado'
    }
    else if (menorQue(version, publicada.value.atual)) {
      estado.value = 'aviso'
    }
  }

  return { estado, publicada, verificar }
}
