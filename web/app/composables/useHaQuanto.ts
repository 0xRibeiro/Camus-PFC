// texto tipo "ha 5s", atualiza sozinho a cada segundo
export function useHaQuanto() {
  const agora = useNow({ interval: 1000 })

  return function haQuanto(tempo: string) {
    const segundos = Math.max(0, Math.round((agora.value.getTime() - new Date(tempo).getTime()) / 1000))
    if (segundos < 60) return `há ${segundos}s`
    if (segundos < 3600) return `há ${Math.floor(segundos / 60)} min`
    if (segundos < 86400) return `há ${Math.floor(segundos / 3600)} h`
    return `há ${Math.floor(segundos / 86400)} dias`
  }
}
