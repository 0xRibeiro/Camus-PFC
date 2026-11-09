import { FetchError } from 'ofetch'

// cliente de api que ja manda o token e tenta renovar sozinho se expirar
export function useApi(grupoId = Number(useRouter().currentRoute.value.path.match(/^\/grupos\/(\d+)(\/|$)/)?.[1])) {
  const config = useRuntimeConfig()
  const auth = useAuthStore()

  const client = $fetch.create({
    baseURL: config.public.apiBase,
    // roda antes de toda chamada, gruda o token no cabecalho se tiver
    onRequest({ options }) {
      if (auth.accessToken) {
        options.headers.set('Authorization', `Bearer ${auth.accessToken}`)
      }
    },
  })

  // tenta a chamada, se cair 401 renova o token e tenta dnv
  return async function api(request: string, options?: any) {
    // os componentes de trilha e quiz usam a API do grupo quando abertos dentro dele
    const recurso = /^\/(trilhas|modulos|conteudos|questoes|alternativas|imagens|progresso|pontuacao)(\/|$)/
    if (grupoId > 0 && recurso.test(request)) {
      request = `/grupos/${grupoId}${request}`
    }

    try {
      return await client<any>(request, options)
    }
    catch (error) {
      // rota de /auth/* nunca tenta renovar (senao entraria em loop)
      const isAuthRoute = request.startsWith('/auth/')
      if (!(error instanceof FetchError) || error.status !== 401 || isAuthRoute) {
        throw error
      }

      try {
        await auth.refresh()
      }
      catch {
        // refresh falhou, token realmente expirou, desloga e manda pro login
        await auth.logout()
        await navigateTo('/login')
        throw error
      }

      // renovou com sucesso, tenta a chamada original de novo, com o token novo
      return await client<any>(request, options)
    }
  }
}
