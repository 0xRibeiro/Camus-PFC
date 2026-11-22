const formatoData = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' })

// data do back vem yyyy-mm-dd sem hora, o utc evita voltar um dia pelo fuso
export function formatarData(data: string) {
  return formatoData.format(new Date(`${data}T00:00:00Z`))
}

const formatoDataHora = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

// esse ja vem com hora e fuso, mostra no fuso de quem ta vendo
export function formatarDataHora(momento: string) {
  return formatoDataHora.format(new Date(momento))
}

const relativo = new Intl.RelativeTimeFormat('pt-BR', { numeric: 'auto' })

// "há 3 dias", "há 5 horas", "agora"
export function formatarRelativo(momento: string) {
  const minutos = Math.round((new Date(momento).getTime() - Date.now()) / 60000)
  if (Math.abs(minutos) < 60) return minutos > -1 ? 'agora' : relativo.format(minutos, 'minute')
  const horas = Math.round(minutos / 60)
  if (Math.abs(horas) < 24) return relativo.format(horas, 'hour')
  return relativo.format(Math.round(horas / 24), 'day')
}

const formatoDecimal =new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 })

// duracao em horas virando texto curto: 40 min, 5,5 h, 3,2 dias
export function formatarDuracao(horas: number) {
  if (horas < 1) return `${Math.round(horas * 60)} min`
  if (horas < 24) return `${formatoDecimal.format(horas)} h`
  return `${formatoDecimal.format(horas / 24)} dias`
}
