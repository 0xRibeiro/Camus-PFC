const formatoData = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' })

// data do back vem yyyy-mm-dd sem hora, o utc evita voltar um dia pelo fuso
export function formatarData(data: string) {
  return formatoData.format(new Date(`${data}T00:00:00Z`))
}
