// essa store das conquistas é usada para desbloqueio das mesmas e para
// incluir o toast no visual do site quando o desbloqueio acontece
import type { ConquistaRead } from '~/types/generated'

export const useConquistasStore = defineStore('conquistas', () => {
  const api = useApi()
  const toast = useToast()

  function notificarDesbloqueio(conquista: ConquistaRead) {
    toast.add({
      title: 'Conquista desbloqueada!',
      // o toast sempre mostra informações da conquista atual
      description: conquista.titulo,
      icon: 'i-lucide-trophy',
      color: 'success',
    })
  }

  async function desbloquearConquista(conquistaId: number) {
    // manda o request com o id da conquista para ser desbloqueada
    const conquista = await api(`/usuarios/me/conquistas/${conquistaId}`, {
      method: 'POST',
    }) as ConquistaRead | null

    if (!conquista) return

    // ativa o toast
    notificarDesbloqueio(conquista)
  }

  return {
    notificarDesbloqueio,
    desbloquearConquista,
  }
})
