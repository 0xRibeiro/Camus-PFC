const formatoNota = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 })

// nota sempre de 0 a 10, independente de quantas questoes o quiz tem
export function formatarNota(acertos: number, questoes: number) {
  return formatoNota.format(acertos / questoes * 10)
}

// msm faixa da dashboard do quiz
export function corDaNota(acertos: number, questoes: number) {
  const nota = acertos / questoes
  if (nota < 0.5) return 'error' as const
  if (nota < 0.75) return 'warning' as const
  return 'success' as const
}
